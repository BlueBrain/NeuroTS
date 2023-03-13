"""Module for handling the calculation of neurite orientations."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import inspect
import warnings
from copy import deepcopy

import neurom as nm
import numpy as np
from scipy.optimize import curve_fit
from scipy.special import expit

from neurots.morphmath import rotation
from neurots.morphmath import sample
from neurots.morphmath.utils import normalize_vectors
from neurots.utils import PIA_DIRECTION
from neurots.utils import NeuroTSError

_TWOPI = 2.0 * np.pi
FIT_3D_ANGLES_BOUNDS = {
    "double_step": ([0, 0.1, -np.pi, 0.1], [np.pi, 10, 0, 10]),
    "step": ([-np.pi, 0.1], [np.pi, 10]),
}
FIT_3D_ANGLES_PARAMS = {
    "with_apical": {"basal_dendrite": {"form": "step", "bounds": FIT_3D_ANGLES_BOUNDS["step"]}},
    "without_apical": {"basal_dendrite": {"form": "flat", "bounds": []}},
}
_3D_ANGLES_MAPPING = {
    "apical_constraint": "apical_3d_angles",
    "pia_constraint": "pia_3d_angles",
}
_3D_ANGLES_MODES = {"apical_constraint", "pia_constraint", "normal_pia_constraint"}


class OrientationManagerBase:
    """Base class that automatically registers orientation modes.

    Args:
        soma (Soma): The soma on which the trees should be attached.
        parameters (dict): The parameters used to compute the orientations.
        distributions (dict): The distributions used to compute the orientations.
        context (any): An object containing contextual information.
        rng (numpy.random.Generator): The random number generator to use.

    .. note::
        To register an orientation mode, derive from this base class and
        create a method with the following signature:

        .. code-block:: python

            def _mode_{name}(self, values_dict, tree_type)
    """

    def __init__(self, soma, parameters, distributions, context, rng):
        self._soma = soma
        self._parameters = parameters
        self._distributions = distributions
        self._context = context
        self._rng = rng

        self._orientations = {}
        self._modes = self._collect_mode_methods()

    def _collect_mode_methods(self):
        """Collects and stores in self._modes the methods, the name of which starts with '_mode_'.

        Returns:
            dict: A dictionary mapping mode names without the '_modes_' prefix to the methods.
        """
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        return {
            name.replace("_mode_", ""): method
            for name, method in methods
            if name.startswith("_mode_")
        }

    @property
    def mode_names(self):
        """Returns the names of the available modes."""
        return self._modes.keys()

    def get_tree_type_orientations(self, tree_type):
        """Returns the orientations for the specific tree type."""
        return self._orientations.get(tree_type, None)

    def compute_tree_type_orientations(self, tree_type):
        """Computes the orientations for all tree types. It updates the _orientations dictionary.

        Notes:
            Updating a data structure that is accessible by all orientation methods, allows to
            take into account existing orientations for calculating new ones.
        """
        mode_method, values_dict = self._tree_type_method_values(tree_type)
        oris = mode_method(values_dict, tree_type)
        self._orientations[tree_type] = oris
        return oris

    def _tree_type_method_values(self, tree_type):
        """Checks if the orientation entry in parameters has the correct format."""
        params = self._parameters[tree_type]["orientation"]

        if params is None or params.keys() != {"mode", "values"}:
            raise NeuroTSError(
                f"Parameters orientation entry for {tree_type} is not valid"
                f"Expected dict keys {'mode', 'values'}, but got params={params}"
            )

        mode_name = params["mode"]

        if mode_name not in self._modes:
            raise NeuroTSError(
                f"Orientation mode name {mode_name} is not recognized.\n"
                f"Available orientation modes: {self.mode_names}"
            )

        return self._modes[mode_name], params["values"]


class OrientationManager(OrientationManagerBase):
    """Class to generate the tree orientations starting from the soma of the cell.

    Args:
        soma (Soma): The soma on which the trees should be attached.
        parameters (dict): The parameters used to compute the orientations.
        distributions (dict): The distributions used to compute the orientations.
        context (any): An object containing contextual information.
        rng (numpy.random.Generator): The random number generator to use.

    .. note::
        All orientation mode dicts:

        .. code-block:: python

            {
                "mode": "use_predefined",
                "values": {"orientations": [or1, or2, ...]}
            }
            {
                "mode": "sample_pairwise_angles",
                "values": {}
            }
            {
                "mode": "sample_around_primary_orientation",
                "values": {"primary_orientation": [0, 1, 0]}
            }

    """

    def _mode_use_predefined(self, values_dict, tree_type):
        """Returns predefined orientations."""
        assert "orientations" in values_dict, "'orientations' key is missing"
        tree_type_distrs = self._distributions[tree_type]

        # the reason of this sampling is to maintain the pseudorandom
        # sequence of the legacy implementation. Otherwise the functional tests
        # will break because the sequence will be slightly different.
        sample.n_neurites(tree_type_distrs["num_trees"], self._rng)
        return normalize_vectors(np.asarray(values_dict["orientations"], dtype=np.float64))

    def _mode_sample_around_primary_orientation(self, values_dict, tree_type):
        """Sample orientations around a primary direction."""
        tree_type_distrs = self._distributions[tree_type]
        n_orientations = sample.n_neurites(tree_type_distrs["num_trees"], self._rng)

        trunk_absolute_angles = sample.trunk_absolute_angles(
            tree_type_distrs, n_orientations, self._rng
        )
        z_angles = sample.azimuth_angles(tree_type_distrs, n_orientations, self._rng)

        primary_orientation = np.asarray(values_dict["primary_orientation"], dtype=np.float64)
        primary_orientation /= np.linalg.norm(primary_orientation)

        phis, thetas = trunk_absolute_orientation_to_spherical_angles(
            orientation=primary_orientation,
            trunk_absolute_angles=trunk_absolute_angles,
            z_angles=z_angles,
        )

        return spherical_angles_to_orientations(phis, thetas)

    def _mode_sample_pairwise_angles(self, _, tree_type):
        """Returns sampled orientations."""
        tree_type_distrs = self._distributions[tree_type]

        n_orientations = sample.n_neurites(tree_type_distrs["num_trees"], self._rng)

        phi_intervals, interval_n_trees = compute_interval_n_tree(
            self._soma,
            n_orientations,
            self._rng,
        )

        # Create trunks in each interval
        orientations_i = []
        for phi_interval, i_n_trees in zip(phi_intervals, interval_n_trees):
            phis, thetas = trunk_to_spherical_angles(
                sample.trunk_angles(tree_type_distrs, i_n_trees, self._rng),
                sample.azimuth_angles(tree_type_distrs, i_n_trees, self._rng),
                phi_interval,
            )
            orientations_i.append(spherical_angles_to_orientations(phis, thetas))
        return np.vstack(orientations_i)

    def _mode_uniform(self, _, tree_type):
        """Uniformly sample angles on the sphere."""
        n_orientations = sample.n_neurites(self._distributions[tree_type]["num_trees"], self._rng)
        return np.asarray(
            [sample.sample_spherical_unit_vectors(rng=self._rng) for _ in range(n_orientations)]
        )

    def _mode_normal_pia_constraint(self, values_dict, _):
        """Returns orientations using normal/exp distribution along a direction.

        The `direction` value should be a dict with two entries: `mean` and `std`. The mean is the
        angle wrt to pia (`[0, 1, 0]`) direction and the second is the standard deviation of a
        normal distribution if `mean>0` or scaling of exponential distribution if `mean=0`. As the
        resulting angle must be in `[0, 2 * pi]`, we clip the obtained angle and uniformly sample
        the second angle to obtain a 3d direction. For multiple apical trees, `mean` and `std`
        should be two lists with lengths equal to number of trees, otherwise it can be a float.
        """
        means = values_dict["direction"]["mean"]
        means = means if isinstance(means, list) else [means]
        stds = values_dict["direction"]["std"]
        stds = stds if isinstance(stds, list) else [stds]

        thetas = []
        for mean, std in zip(means, stds):
            if mean == 0:
                if std > 0:
                    thetas.append(np.clip(self._rng.exponential(std), 0, np.pi))
                else:
                    thetas.append(0)
            else:
                thetas.append(np.clip(self._rng.normal(mean, std), 0, np.pi))

        phis = self._rng.uniform(0, 2 * np.pi, len(means))
        return spherical_angles_to_pia_orientations(phis, thetas)

    def _mode_pia_constraint(self, _, tree_type):
        """Create trunks from distribution of angles with pia (`[0 , 1, 0]`) direction.

        See :func:`_sample_trunk_from_3d_angle` for more details on the algorithm.
        """
        n_orientations = sample.n_neurites(self._distributions[tree_type]["num_trees"], self._rng)
        pia_direction = self._parameters.get("pia_direction", PIA_DIRECTION)
        return np.asarray(
            [
                _sample_trunk_from_3d_angle(self._parameters, self._rng, tree_type, pia_direction)
                for _ in range(n_orientations)
            ]
        )

    def _mode_apical_constraint(self, _, tree_type):
        """Create trunks from distribution of angles with apical direction.

        See :func:`_sample_trunk_from_3d_angle` for more details on the algorithm.
        """
        n_orientations = sample.n_neurites(self._distributions[tree_type]["num_trees"], self._rng)
        ref_dir = self._orientations["apical_dendrite"][0]
        return np.asarray(
            [
                _sample_trunk_from_3d_angle(self._parameters, self._rng, tree_type, ref_dir)
                for _ in range(n_orientations)
            ]
        )


def spherical_angles_to_orientations(phis, thetas):
    """Compute orientation from spherical angles.

    Args:
        phis (numpy.ndarray): Polar angles.
        thetas (numpy.ndarray): Azimuthal angles.

    Returns:
        numpy.ndarray: The orientation vectors where each row correspnds to a phi-theta pair.
    """
    return np.column_stack(
        (np.cos(phis) * np.sin(thetas), np.sin(phis) * np.sin(thetas), np.cos(thetas))
    )


def points_to_orientations(origin, points):
    """Returns the unit vector that corresponds to the orientation of a point on the soma surface.

    Args:
        origin (numpy.ndarray): The origin of the vectors.
        points (numpy.ndarray): Points to calculate the vectors to.

    Returns:
        numpy.ndarray: Normalized orientations from origin to points.
    """
    return normalize_vectors(points - origin)


def orientations_to_sphere_points(oris, sphere_center, sphere_radius):
    """Compute points on a sphere from the given directions.

    Args:
        oris (numpy.ndarray): Normalized orientation vectors.
        sphere_center (numpy.ndarray): Center of sphere.
        sphere_radius (float): Radius of sphere.

    Returns:
        numpy.ndarray: Points on the surface of the sphere corresponding
        to the given orientations.
    """
    return sphere_center + oris * sphere_radius


def trunk_to_spherical_angles(trunk_angles, z_angles, phi_interval=None):
    """Generate spherical angles from a list of NeuroM angles.

    Args:
        trunk_angles (list[float]): The polar angles (phi in spherical coordinates).
        z_angles (list[float]): The azimuthal angles (theta in spherical coordinates).
        phi_interval (tuple[float, float]): The interval in which the trunks should be added.

    Returns:
        tuple[numpy.ndarray[float], numpy.ndarray[float]]: The phi and theta angles.
    """
    if phi_interval is None:
        phi_interval = (0.0, _TWOPI)

        nb_intervals_min = 0
    else:
        assert len(phi_interval) == 2, "'phi_interval' must be a sequence of 2 elements."
        assert phi_interval[0] < phi_interval[1], "'phi_interval' must be sorted ascending."

        # Add 1 so the equiangle is computed such that angles are not equal to any boundary of the
        # given interval
        nb_intervals_min = 1

    trunk_angles = np.asarray(trunk_angles)
    z_angles = np.asarray(z_angles)

    n_angles = len(trunk_angles)
    sorted_ids = np.argsort(trunk_angles)

    sorted_phi_devs = trunk_angles[sorted_ids]

    thetas = z_angles[sorted_ids]

    equiangle = (phi_interval[1] - phi_interval[0]) / (n_angles + nb_intervals_min)
    phis = np.arange(1, n_angles + 1) * equiangle + sorted_phi_devs + phi_interval[0]

    return phis, thetas


def trunk_absolute_orientation_to_spherical_angles(orientation, trunk_absolute_angles, z_angles):
    """Generate spherical angles from a unit vector and a list of angles.

    Args:
        orientation (list[float]): The orientation vector.
        trunk_absolute_angles (list[float]): The polar angles (phi in spherical coordinates).
        z_angles (list[float]): The azimuthal angles (theta in spherical coordinates).

    Returns:
        tuple[numpy.ndarray[float], numpy.ndarray[float]]: The phi and theta angles.
    """
    # Sort angles
    sort_ids = np.argsort(trunk_absolute_angles)
    sorted_phis = np.asarray(trunk_absolute_angles)[sort_ids]
    sorted_thetas = np.asarray(z_angles)[sort_ids]

    # Convert orientation vector to angles
    phi, theta = rotation.spherical_from_vector(orientation)

    phis = phi + sorted_phis - 0.5 * np.pi
    thetas = theta + sorted_thetas - 0.5 * np.pi

    return phis, thetas


def compute_interval_n_tree(soma, n_trees, rng=np.random):
    """Compute the number of trunks to add between each pair of consecutive existing trunks.

    If points already exist in the soma, the algorithm is the following:

    - build the intervals between each pair of consecutive points.
    - compute the size of each interval.
    - randomly select the interval in which each new point will be added (the intervals are
      weighted by their sizes to ensure the new trunks are created isotropically).
    - count the number of new points in each interval.
    - return the intervals in which at least one point must be added.

    If no point exists in the soma, the interval [0, 2pi] contains all the new trunks.

    Args:
        soma (Soma): The soma on which the trunks should be added.
        n_trees (int): The number of trees that should be added.
        rng (numpy.random.Generator): The random number generator to use.

    Returns:
        tuple[numpy.ndarray[float], numpy.ndarray[int]]: The phi intervals and the number of trees
        in each of them.
    """
    if soma and len(soma.points) > 0:
        # Get angles of existing trunk origins
        phis = []
        for pt in soma.points:
            pt_orientation = soma.orientation_from_point(pt)
            phi, _ = rotation.spherical_from_vector(pt_orientation)
            phis.append(phi)

        phis = sorted(phis)

        # The last interval goes beyond 2 * pi but the function
        # self.soma.add_points_from_trunk_angles can deal with it.
        phis += [phis[0] + _TWOPI]
        phi_intervals = np.column_stack((phis[:-1], phis[1:]))

        # Compute the number of trunks to create in each interval: each interval is weighted by
        # its size to ensure the new trunks are created isotropically.
        sizes = phi_intervals[:, 1] - phi_intervals[:, 0]
        interval_i, interval_i_n_trees = np.unique(
            rng.choice(range(len(sizes)), size=n_trees, p=sizes / sizes.sum()), return_counts=True
        )

        # Keep only intervals with n_trees > 0
        phi_intervals = phi_intervals[interval_i].tolist()
        interval_n_trees = interval_i_n_trees

    else:
        # If there is no existing trunk, we create a None interval
        phi_intervals = [None]
        interval_n_trees = np.array([n_trees])

    return phi_intervals, interval_n_trees


def spherical_angles_to_pia_orientations(phis, thetas):
    """Compute orientation from spherical angles where thetas are wrt to pia at `[0, 1, 0]`.

    Args:
        phis (numpy.ndarray): Polar angles.
        thetas (numpy.ndarray): Azimuthal angles.

    Returns:
        numpy.ndarray: The orientation vectors where each row corresponds to a phi-theta pair.
    """
    return np.column_stack(
        (np.cos(phis) * np.sin(thetas), np.cos(thetas), np.sin(phis) * np.sin(thetas))
    )


def get_probability_function(form="step", with_density=True):
    """Get probability functions to fit 3d trunk angles distributions.

    Args:
        form (str): Form of the function, can be `flat`, `step` or `double_step`.
        with_density (bool): Return the function with spherical density factor or not.

    Three forms of functions are available:
    - `flat`: uniform flat distribution
    - `step`: distribution with a single sigmoid :func:`scipy.special.expit`
    - `double_step`: distribution with two opposite sigmoids :func:`scipy.special.expit`

    Each sigmoid is parametrized by a scale and a rate.

    In practice, the `flat` function is used when no asymetry is present in the data, and the other
    two are when an asymmetry towards one direction, usually opposite to pia or apical,
    or two directions, usually along and opposite to pia.

    Returns:
        function with first arg as angle and next args to parametrize the function
    """
    if form == "flat":

        def flat_prob(angle):
            p = 1.0 + 0 * angle
            if with_density:
                p *= np.sin(angle)
            return p

        return flat_prob

    if form == "step":

        def single_prob(angle, scale, rate):
            def _prob(angle):
                return expit((angle - scale) / rate)

            p = _prob(angle) / max(_prob(np.linspace(0, np.pi, 100)))
            if with_density:
                p *= np.sin(angle)
            return np.clip(p, 0.0, 1.0)

        return single_prob

    if form == "double_step":

        def double_prob(angle, scale_low, rate_low, scale_high, rate_high):
            def _prob(angle):
                return 0.5 * (
                    expit((angle - scale_low) / rate_low) + expit((-angle - scale_high) / rate_high)
                )

            p = _prob(angle) / max(_prob(np.linspace(0, np.pi, 100)))
            if with_density:
                p *= np.sin(angle)
            return np.clip(p, 0.0, 1.0)

        return double_prob

    raise ValueError(
        f"The '{form}' value is unknown, it should be one of ['flat', 'step', 'double_step']"
    )


def _fit_single_3d_angles(data, neurite_type, morph_class, fit_params=None):
    """Fit function to distribution of 3d angles for a `neurite_type`.

    Args:
        data (dict): bins and weights data from input_distribution
        neurite_type (str): neurite_type to consider
        morph_class (str): morph_class of the neuron (with_apical or without_apical)
        fit_params (dict): specific fit parameters such as form and bounds to overwrite the defaults
    """
    _fit_params = deepcopy(FIT_3D_ANGLES_PARAMS)
    if fit_params is not None:
        _fit_params[morph_class][neurite_type].update(fit_params)
    form = _fit_params[morph_class][neurite_type]["form"]
    if form != "flat":
        function = get_probability_function(form, with_density=True)

        try:
            popt = curve_fit(
                function,
                data["bins"],
                data["weights"],
                bounds=_fit_params[morph_class][neurite_type]["bounds"],
            )[0].tolist()
        except RuntimeError:  # pragma: no cover
            warnings.warn("Cannot fit some trunk angles, we fallback to flat distribution")
            form = "flat"
            popt = []
    else:
        popt = []
    return {"form": form, "params": popt}


def _get_fit_params_from_input_parameters(parameters):
    """Get parameter dict for fits from `tmd_parameters`."""
    values = parameters["orientation"].get("values")
    if values is not None:
        form = values.get("form")
        if form is not None and values.get("params") is None:
            bounds = values.get("bounds", FIT_3D_ANGLES_BOUNDS.get(form, None))
            return {"form": form, "bounds": deepcopy(bounds)}
    return None


def check_3d_angles(tmd_parameters):
    """Check whether the parameters correspond to 3d_angle modes, and return a bool."""
    with_3d = []
    for neurite_type in tmd_parameters["grow_types"]:
        orient = tmd_parameters[neurite_type]["orientation"]
        if orient is not None and "mode" in orient and orient["mode"] in _3D_ANGLES_MODES:
            with_3d.append(True)
        else:
            with_3d.append(False)
    if len(set(with_3d)) > 1:
        raise NeuroTSError("Only partial 3d_angle parameters are present")
    return with_3d[0]


def fit_3d_angles(tmd_parameters, tmd_distributions):
    """Fit functions to 3d_angles from `tmd_distributions` and save in copy of `tmd_parameters`.

    If the fit parameters are already in `tmd_parameters`, the fit is skipped.

    Args:
        tmd_parameters (dict): Input parameters.
        tmd_distributions (dict): Input distributions.

    Returns:
        `tmd_parmeters` with fit data if `3d_angles` mode is found, else None
    """
    morph_class = (
        "with_apical" if "apical_dendrite" in tmd_parameters["grow_types"] else "without_apical"
    )

    for neurite_type in tmd_parameters["grow_types"]:
        orientation = tmd_parameters[neurite_type]["orientation"]

        if orientation is None or "mode" not in orientation:
            continue

        mode = orientation["mode"]
        make_fit = False
        if mode in _3D_ANGLES_MAPPING:
            if orientation.get("values") is None:
                make_fit = True
            else:
                val = orientation["values"]
                if "params" not in val and "direction" not in val:
                    make_fit = True

        if make_fit:
            tmd_parameters[neurite_type]["orientation"]["values"] = _fit_single_3d_angles(
                tmd_distributions[neurite_type]["trunk"][_3D_ANGLES_MAPPING[mode]]["data"],
                neurite_type,
                morph_class,
                fit_params=_get_fit_params_from_input_parameters(tmd_parameters[neurite_type]),
            )

    return tmd_parameters


def _sample_trunk_from_3d_angle(parameters, rng, tree_type, ref_dir, max_tries=100):
    """Sample trunk directions from fit of distribution of `3d_angles` wrt to `ref_dir`.

    We use the accept-reject algorithm so we can sample from any distribution.
    After a number of unsuccessful tries (default=100), we stop and return a random direction.
    We also issue a warning so the user is aware that the provided distribution may have issues,
    mostly related to large region of small probabilities.
    """
    prob = get_probability_function(
        form=parameters[tree_type]["orientation"]["values"]["form"],
        with_density=False,
    )
    params = parameters[tree_type]["orientation"]["values"]["params"]
    n_try = 0
    while n_try < max_tries:
        propose = sample.sample_spherical_unit_vectors(rng)
        angle = nm.morphmath.angle_between_vectors(ref_dir, propose)
        if rng.binomial(1, prob(angle, *params)):
            return propose
        n_try += 1
    warnings.warn(
        """We could not sample from distribution, so we take a random point.
                    Consider checking the given probability distribution."""
    )
    return sample.sample_spherical_unit_vectors(rng)
