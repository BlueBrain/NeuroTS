"""NeuroTS class: Grower object that contains the grower functionality."""

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

import copy
import json
import logging

import numpy as np
from morphio.mut import Morphology  # pylint: disable=import-error
from numpy.random import BitGenerator
from numpy.random import Generator
from numpy.random import RandomState
from numpy.random import SeedSequence

from neurots.generate import diametrizer
from neurots.generate import orientations as _oris
from neurots.generate.orientations import OrientationManager
from neurots.generate.soma import Soma
from neurots.generate.soma import SomaGrower
from neurots.generate.tree import TreeGrower
from neurots.morphmath import sample
from neurots.morphmath.utils import normalize_vectors
from neurots.validator import validate_neuron_distribs
from neurots.validator import validate_neuron_params

L = logging.getLogger(__name__)

bifurcation_methods = ["symmetric", "bio_oriented", "directional", "bio_smoothed"]


def _load_json(path_or_json):
    """Copy the given data if it is a dictionary or a list or load it if it is a file path."""
    if isinstance(path_or_json, (dict, list)):
        data = copy.deepcopy(path_or_json)
    else:
        with open(path_or_json, encoding="utf-8") as f:
            data = json.load(f)
    return data


class NeuronGrower:
    """The main class for growing algorithms of neurons.

    A Grower object is a container for a Neuron, encoded in the (groups, points) structure,
    as a morphIO Morphology object. A set of input distributions that store the data
    consumed by the algorithms and the user-selected parameters are also stored.

    Args:
        input_parameters (dict): The user-defined parameters.
        input_distributions (dict): Distributions extracted from biological data.
        context (Any): An object containing contextual information.
        external_diametrizer (Callable): Diametrizer function for external diametrizer module
        skip_validation (bool): If set to ``False``, the parameters and distributions are
            validated.
        rng_or_seed (int or numpy.random.Generator): A random number generator to use. If an
            int is given, it is passed to :func:`numpy.random.default_rng()` to create a new
            random number generator.
        trunk_orientations_class (typing.Generic[OrientationManagerBase]): The class used to
            build the trunk orientation manager. This class should inherit from
            :class:`neurots.generate.orientations.OrientationManagerBase`.
    """

    def __init__(
        self,
        input_parameters,
        input_distributions,
        context=None,
        external_diametrizer=None,
        skip_validation=False,
        rng_or_seed=np.random,
        trunk_orientations_class=OrientationManager,
    ):
        """Constructor of the NeuronGrower class."""
        self.neuron = Morphology()
        self.context = context
        if rng_or_seed is None or isinstance(
            rng_or_seed, (int, np.integer, SeedSequence, BitGenerator)
        ):
            self._rng = np.random.default_rng(rng_or_seed)
        elif isinstance(rng_or_seed, (RandomState, Generator)) or rng_or_seed is np.random:
            self._rng = rng_or_seed
        else:
            raise TypeError(
                "The 'rng_or_seed' argument must be None, np.random or an instance of one of the "
                "following types: [int, SeedSequence, BitGenerator, RandomState, Generator]."
            )

        self.input_parameters = _load_json(input_parameters)
        L.debug("Input Parameters: %s", self.input_parameters)

        self.input_distributions = _load_json(input_distributions)

        # Validate parameters and distributions
        if not skip_validation:
            self.validate_params()
            self.validate_distribs()

        # Consistency check between parameters and distributions
        for tree_type in self.input_parameters["grow_types"]:
            metric1 = self.input_parameters[tree_type].get("metric")
            metric2 = self.input_distributions[tree_type].get("filtration_metric")
            if metric1 not in ["trunk_length", metric2]:
                raise ValueError(
                    "Metric of parameters and distributions is inconsistent:"
                    + f" {metric1} != {metric2}"
                )

        method1 = self.input_parameters["diameter_params"]["method"]
        method2 = self.input_distributions["diameter"]["method"]
        if method1 != method2:
            raise ValueError(
                "Diameters methods of parameters and distributions is inconsistent:"
                + f" {method1} != {method2}"
            )

        if (
            self.input_distributions["diameter"]["method"] == "external"
            and external_diametrizer is None
        ):
            raise ValueError("External diametrizer is missing the diametrizer function.")

        # A list of trees with the corresponding orientations
        # and initial points on the soma surface will be initialized.
        self.active_neurites = []
        self.soma_grower = SomaGrower(
            Soma(
                center=self.input_parameters["origin"],
                radius=sample.soma_size(self.input_distributions, self._rng),
            ),
            context=context,
            rng=self._rng,
        )
        # Create a list to expose apical sections for each apical tree in the neuron,
        # the user can call NeuronGrower.apical_sections to get section IDs whose the last
        # point is the apical point of each generated apical tree.
        self.apical_sections = []

        # initialize diametrizer
        self._init_diametrizer(external_diametrizer=external_diametrizer)

        self._trunk_orientations_class = trunk_orientations_class

    def validate_params(self):
        """Validate the parameter dictionary."""
        validate_neuron_params(self.input_parameters)

    def validate_distribs(self):
        """Validate the distribution dictionary."""
        validate_neuron_distribs(self.input_distributions)

    def next(self):
        """Call the "next" method of each neurite grower."""
        for grower in list(self.active_neurites):
            if grower.end():
                # If tree is an apical, the apical points get appended at the end of growth
                # This will ensure that for each apical tree a relevant apical point,
                # will be exposed to the user as a set of 3D coordinates (x,y,z).
                if (
                    "apical" in self.input_parameters["grow_types"]
                    and grower.type == self.input_parameters["apical"]["tree_type"]
                ):
                    self.apical_sections.append(grower.growth_algo.apical_section)
                self.active_neurites.remove(grower)
            else:
                grower.next_point()

    def grow(self):
        """Generates a neuron according to the input_parameters and the input_distributions.

        The neuron consists of a soma
        and a list of trees encoded in the h5 format as a set of points
        and groups.

        Returns:
            morphio.mut.Morphology: The grown neuron.
        """
        self._grow_soma()
        while self.active_neurites:
            self.next()  # pylint: disable=E1102
        self._post_grow()
        self._diametrize()
        return self.neuron

    def _post_grow(self):
        """Actions after the morphology has been grown and before its diametrization."""

    def _init_diametrizer(self, external_diametrizer=None):
        """Set a diametrizer function."""
        if self.input_distributions["diameter"]["method"] == "default":
            self._diametrize = lambda: None
            L.warning("No diametrizer provided, so neurons will have default diameters.")
        else:
            if self.input_distributions["diameter"]["method"] == "external":
                if external_diametrizer is None:
                    raise Exception("Please provide an external diametrizer!")
                diam_method = external_diametrizer
            else:
                diam_method = self.input_distributions["diameter"]["method"]

            def _diametrize():
                """Diametrizer function."""
                self.input_distributions["diameter"]["apical_point_sec_ids"] = self.apical_sections
                neurite_types = self.input_parameters.get("diameter_params", {}).get(
                    "neurite_types", None
                )
                if neurite_types is None:
                    neurite_types = self.input_parameters["grow_types"]
                diametrizer.build(
                    self.neuron,
                    self.input_distributions["diameter"],
                    neurite_types=neurite_types,
                    diam_method=diam_method,
                    diam_params=self.input_parameters.get("diameter_params", {}),
                    random_generator=self._rng,
                )

            self._diametrize = _diametrize

    def _convert_orientation2points(self, orientation, n_trees, distr, params):
        """Return soma point from given orientations.

        Checks the type of orientation input and returns the soma points generated by the
        corresponding selection.

        Currently accepted orientations include the following options:
        * list of 3D points: select the orientation externally.
        * ``None``: creates a list of orientations according to the biological distributions.
        * ``from_space``: generates orientations depending on spatial input (not implemented yet).
        """
        # pylint: disable=too-many-locals
        if isinstance(orientation, list):  # Gets major orientations externally
            assert np.all(
                np.linalg.norm(orientation, axis=1) > 0
            ), "Orientations should have non-zero lengths"
            if params.get("trunk_absolute_orientation", False):
                if len(orientation) == 1:

                    orientation = np.asarray(orientation[0], dtype=np.float64)
                    orientation /= np.linalg.norm(orientation)

                    # Pick random absolute angles
                    trunk_absolute_angles = sample.trunk_absolute_angles(distr, n_trees, self._rng)
                    z_angles = sample.azimuth_angles(distr, n_trees, self._rng)

                    phis, thetas = _oris.trunk_absolute_orientation_to_spherical_angles(
                        orientation, trunk_absolute_angles, z_angles
                    )

                    orientations = _oris.spherical_angles_to_orientations(phis, thetas)

                else:
                    raise ValueError("The orientation should contain exactly one point!")
            else:
                if len(orientation) >= n_trees:

                    # TODO: pick orientations randomly?
                    orientations = normalize_vectors(np.asarray(orientation, dtype=np.float64))[
                        :n_trees
                    ]

                else:
                    raise ValueError("Not enough orientation points!")
        elif orientation is None:  # Samples from trunk_angles
            phi_intervals, interval_n_trees = _oris.compute_interval_n_tree(
                self.soma_grower.soma,
                n_trees,
                self._rng,
            )

            # Create trunks in each interval
            orientations_i = []
            for phi_interval, i_n_trees in zip(phi_intervals, interval_n_trees):
                phis, thetas = _oris.trunk_to_spherical_angles(
                    sample.trunk_angles(distr, i_n_trees, self._rng),
                    sample.azimuth_angles(distr, i_n_trees, self._rng),
                    phi_interval,
                )
                orientations_i.append(_oris.spherical_angles_to_orientations(phis, thetas))
            orientations = np.vstack(orientations_i)

        elif orientation == "from_space":
            raise ValueError("Not implemented yet!")
        else:
            raise ValueError("Input orientation format is not correct!")

        pts = self.soma_grower.add_points_from_orientations(orientations)
        return pts

    def _grow_trunks(self):
        """Grow the trunks.

        Generates the initial points of each tree, which depend on the selectedS
        tree types and the soma surface. All the trees start growing from the surface
        of the soma. The outgrowth direction is either specified in the input parameters,
        as ``parameters['type']['orientation']`` or it is randomly chosen according to the
        biological distribution of trunks on the soma surface if ``orientation`` is ``None``.
        """
        tree_types = self.input_parameters["grow_types"]

        legacy_mode = not isinstance(self.input_parameters[tree_types[0]]["orientation"], dict)

        if not legacy_mode:

            trunk_orientations_manager = self._trunk_orientations_class(
                soma=self.soma_grower.soma,
                parameters=self.input_parameters,
                distributions=self.input_distributions,
                context=self.context,
                rng=self._rng,
            )

        for type_of_tree in tree_types:

            params = self.input_parameters[type_of_tree]
            distr = self.input_distributions[type_of_tree]

            if legacy_mode:

                n_trees = sample.n_neurites(distr["num_trees"], random_generator=self._rng)

                if type_of_tree == "basal" and n_trees < 2:
                    raise Exception(f"There should be at least 2 basal dendrites (got {n_trees})")

                orientation = params["orientation"]
                points = self._convert_orientation2points(orientation, n_trees, distr, params)

            else:

                orientations = trunk_orientations_manager.compute_tree_type_orientations(
                    type_of_tree
                )
                n_trees = len(orientations)

                if type_of_tree == "basal" and n_trees < 2:
                    raise Exception(f"There should be at least 2 basal dendrites (got {n_trees})")

                points = self.soma_grower.add_points_from_orientations(orientations)

            # Iterate over all initial points on the soma and create new trees
            # with a direction and initial_point
            for p in points:
                self.active_neurites.append(
                    TreeGrower(
                        self.neuron,
                        initial_direction=self.soma_grower.soma.orientation_from_point(p),
                        initial_point=p,
                        parameters=params,
                        distributions=distr,
                        context=self.context,
                        random_generator=self._rng,
                    )
                )

    def _grow_soma(self, soma_type="contour"):
        """Generates a soma based on the input_distributions.

        The coordinates of the soma contour are retrieved from the trunks.
        """
        self._grow_trunks()

        points, diameters = self.soma_grower.build(soma_type)
        self.neuron.soma.points = points
        self.neuron.soma.diameters = diameters
