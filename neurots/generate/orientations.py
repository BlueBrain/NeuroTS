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

import numpy as np

from neurots.morphmath import rotation
from neurots.morphmath import sample
from neurots.morphmath.utils import normalize_vectors
from neurots.utils import NeuroTSError

_TWOPI = 2.0 * np.pi


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
        strip_mode = lambda name: name.replace("_mode_", "")
        return {strip_mode(name): method for name, method in methods if name.startswith("_mode_")}

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

    def _mode_use_predefined(self, values_dict, tree_type):  # pylint: disable=no-self-use
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
