"""Module for handling the calculation of neurite orientations."""
import inspect

import numpy as np

from neurots.morphmath import rotation
from neurots.morphmath import sample
from neurots.morphmath.utils import normalize_vectors
from neurots.utils import NeuroTSError


class OrientationManagerBase:
    """Base class that automatically registers orientation modes.

    Args:
        soma (Soma): NeuroTS Soma
        parameters (dict): NeuroTS parameters dict
        distributions (dict): NeuroTS distributions dict
        context (dict): Context dict
        rng (Generator): numpy's random generator

    .. note::
        To register an orientation mode, derive from this base class and
        create a method with the following signature:

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
        soma (Soma): NeuroTS Soma
        parameters (dict): NeuroTS parameters dict
        distributions (dict): NeuroTS distributions dict
        context (dict): Context dict
        rng (Generator): numpy's random generator

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

        phis, thetas = trunk_to_spherical_angles(
            trunk_angles=sample.trunk_angles(tree_type_distrs, n_orientations, self._rng),
            z_angles=sample.azimuth_angles(tree_type_distrs, n_orientations, self._rng),
        )

        return spherical_angles_to_orientations(phis, thetas)


def spherical_angles_to_orientations(phis, thetas):
    """Compute orientation from spherical angles.

    Args:
        phis (np.ndarray): polar angles
        thetas (np.ndarray): azimuthal angles

    Returns:
        np.array: The orientation vectors where each row correspnds to a phi-theta pair.
    """
    return np.column_stack(
        (np.cos(phis) * np.sin(thetas), np.sin(phis) * np.sin(thetas), np.cos(thetas))
    )


def points_to_orientations(origin, points):
    """Returns the unit vector that corresponds to the orientation of a point on the soma surface.

    Args:
        origin (np.ndarray): The origin of the vectors
        points (np.ndarray): Points to calculate the vectors to

    Returns:
        np.ndarray: Normalized orientations from origin to points
    """
    return normalize_vectors(points - origin)


def orientations_to_sphere_points(oris, sphere_center, sphere_radius):
    """Compute points on a sphere from the given directions.

    Args:
        oris (np.ndarray): Normalized orientation vectors
        sphere_center (np.ndarray): Center of sphere
        sphere_radius (float): Radius of sphere

    Returns:
        np.ndarray: Points on the surface of the sphere corresponding
            to the given orientations
    """
    return sphere_center + oris * sphere_radius


def trunk_to_spherical_angles(trunk_angles, z_angles):
    """Generate spherical angles from a list of NeuroM angles.

    trunk_angles correspond to the angles on the x-y plane,
    while z_angles correspond to the equivalent z-direction.

    trunk angles correspond to polar angles, phi
    z_angles correspond to azimuthal angles, theta
    """
    trunk_angles = np.asarray(trunk_angles)
    z_angles = np.asarray(z_angles)

    n_angles = len(trunk_angles)
    sorted_ids = np.argsort(trunk_angles)

    sorted_phi_devs = trunk_angles[sorted_ids]

    thetas = z_angles[sorted_ids]

    equiangle = 2.0 * np.pi / n_angles
    phis = np.arange(1, n_angles + 1) * equiangle + sorted_phi_devs

    return phis, thetas


def trunk_absolute_orientation_to_spherical_angles(orientation, trunk_absolute_angles, z_angles):
    """Generate spherical angles from a unit vector and a list of angles."""
    # Sort angles
    sort_ids = np.argsort(trunk_absolute_angles)
    sorted_phis = np.asarray(trunk_absolute_angles)[sort_ids]
    sorted_thetas = np.asarray(z_angles)[sort_ids]

    # Convert orientation vector to angles
    phi, theta = rotation.spherical_from_vector(orientation)

    phis = phi + sorted_phis - 0.5 * np.pi
    thetas = theta + sorted_thetas - 0.5 * np.pi

    return phis, thetas
