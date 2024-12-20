"""NeuroTS class: Tree."""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

import copy
import json
import logging
from collections import namedtuple

import numpy as np
from morphio import PointLevel
from morphio import SectionType

from neurots.generate.algorithms import basicgrower
from neurots.generate.algorithms import tmdgrower
from neurots.generate.section import SectionGrower
from neurots.generate.section import SectionGrowerPath
from neurots.generate.section import SectionGrowerTMD
from neurots.morphmath import sample
from neurots.utils import NeuroTSError

L = logging.getLogger("neurots")

LAMBDA = 1.0
"""Parameter that defines the slope of exponential probability."""

DEFAULT_DIAMETER = 1
"""The default diameter used to add new sections before they are diametrized later."""

growth_algorithms = {
    "tmd": tmdgrower.TMDAlgo,
    "tmd_apical": tmdgrower.TMDApicalAlgo,
    "tmd_gradient": tmdgrower.TMDGradientAlgo,
    "axon_trunk": basicgrower.AxonAlgo,
    "trunk": basicgrower.TrunkAlgo,
}

section_growers = {
    "radial_distances": SectionGrowerTMD,
    "path_distances": SectionGrowerPath,
    "trunk_length": SectionGrower,
}


# Section grower parameters
SectionParameters = namedtuple(
    "SectionParameters", ["randomness", "targeting", "scale_prob", "history"]
)


def _create_section_parameters(input_dict):
    """Create section parameters from input dictionary.

    Args:
        input_dict (dict): Input dictionary with ``randomness`` and ``targeting`` entries.

    Returns:
        SectionParameters: The section parameters.
    """
    randomness = np.clip(input_dict["randomness"], 0.0, 1.0)
    targeting = np.clip(input_dict["targeting"], 0.0, 1.0)
    history = np.clip(1.0 - randomness - targeting, 0.0, 1.0)

    parameters = SectionParameters(
        randomness=randomness, targeting=targeting, scale_prob=LAMBDA, history=history
    )

    try:
        assert np.isclose(randomness + targeting + history, 1.0)
        L.debug("Section Parameters: %s", parameters)
        return parameters

    except AssertionError as err:
        msg = f"Parameters randomness, targeting and history do not sum to 1:\n{parameters}"
        L.error(msg)
        raise NeuroTSError(msg) from err


class TreeGrower:
    """Tree class.

    Args:
        neuron (morphio.mut.Morphology): The morphology in which groups and points are stored.
        initial_direction (list[float]): 3D vector that defines the starting direction of the tree.
        initial_point (list[float]): 3D vector that defines the starting point of the tree.
        parameters (dict): A dictionary with ``tree_type``, ``radius``, ``randomness`` and
            ``targeting`` keys.
        distributions (dict): The distributions used.
        context (Any): The context used for the tree.
        random_generator (numpy.random.Generator): The random number generator to use.
    """

    def __init__(
        self,
        neuron,
        initial_direction,
        initial_point,
        parameters,
        distributions,
        context=None,
        random_generator=np.random,
    ):
        """Constructor of TreeGrower object."""
        self.neuron = neuron
        self.direction = initial_direction
        self.point = initial_point
        self.type = parameters["tree_type"]  # 2: axon, 3: basal, 4: apical, 5: other
        self.params = parameters
        self.distr = distributions
        self.active_sections = []
        self.context = context
        self._rng = random_generator

        # Creates the distribution from which the segment lengths
        # To sample a new seg_len call self.seg_len.draw()
        self.seg_length_distr = sample.Distr(self.params["step_size"], random_generator=self._rng)
        self._section_parameters = _create_section_parameters(parameters)
        self.growth_algo = self._initialize_algorithm()

    def _initialize_algorithm(self):
        """Initialization steps for TreeGrower."""
        grow_meth = growth_algorithms[self.params["growth_method"]]

        growth_algo = grow_meth(
            input_data=self.distr,
            params=self.params,
            start_point=self.point,
            context=self.context,
            random_generator=self._rng,
        )

        stop, num_sec = growth_algo.initialize()

        sec = self.add_section(
            parent=None,
            direction=self.direction,
            first_point=list(self.point),
            stop=copy.deepcopy(stop),
            process="major",
            pathlength=0.0,
            children=2 if num_sec > 1 else 0,
        )
        # First section of the tree has at least one point.
        sec.first_point()

        return growth_algo

    def add_section(
        self, parent, direction, first_point, stop, pathlength, process=None, children=0
    ):
        """Generates a section from the parent section "act" from all the required information.

        The section is added to the neuron.sections and activated.

        Args:
            parent (morphio.Section): The parent of the section.
            direction (list[float]): The direction of the section.
            first_point (list[float]): The first point of the section.
            stop (dict):The stop criteria used for this section.
            pathlength (float): The path length of the section.
            process (str): The process type.
            children (int): The number of children.
        """
        SGrower = section_growers[self.params["metric"]]
        context = copy.deepcopy(self.context)
        if "constraints" in self.context:  # pragma: no cover
            context["constraints"] = [
                constraint
                for constraint in self.context["constraints"]
                if "section_prob" in constraint
                and SectionType(self.params["tree_type"]).name
                in constraint.get("neurite_types", [])
                and process in constraint.get("processes", ["major", "secondary"])
            ]

        sec_grower = SGrower(
            parent=parent,
            first_point=first_point,
            direction=direction,
            parameters=self._section_parameters,
            children=children,
            process=process,
            stop_criteria=copy.deepcopy(stop),
            step_size_distribution=self.seg_length_distr,
            pathlength=pathlength,
            context=context,
            random_generator=self._rng,
        )

        self.active_sections.append(sec_grower)
        return sec_grower

    def end(self):
        """Ends the growth."""
        return not bool(self.active_sections)

    @staticmethod
    def order_per_process(secs):
        """Orders sections according to process type, major first."""
        return np.copy(secs)[np.argsort([ss.process for ss in secs], kind="stable")]

    @staticmethod
    def order_per_bif(secs):
        """Orders sections according to bifurcation times."""
        ordered_list = np.argsort([ss.stop_criteria["TMD"].bif for ss in secs], kind="stable")
        return np.copy(secs)[ordered_list]

    def append_section(self, section):
        """Append section to the MorphIO neuron.

        Args:
            section (SectionGrowerPath): The section that is going to be appended.

        Returns:
            section (morphio.Section): The new appended section.
        """
        if section.parent:
            append_fun = section.parent.append_section
        else:
            append_fun = self.neuron.append_root_section

        if L.level == logging.DEBUG:  # pragma: no cover
            data = {
                "parent": section.parent.id if section.parent else None,
                "coord": np.vstack(section.points).tolist(),
                "type": int(SectionType(self.params["tree_type"])),
            }
            L.debug("appended_data=%s", json.dumps(data))

        return append_fun(
            PointLevel(
                np.array(section.points).tolist(),
                [DEFAULT_DIAMETER] * len(section.points),
            ),
            SectionType(self.params["tree_type"]),
        )

    def next_point(self):
        """Operates the tree growth according to the selected algorithm."""
        if not isinstance(self.growth_algo, basicgrower.TrunkAlgo):
            ordered_sections = self.order_per_bif(self.active_sections)
        else:
            # TrunkAlgo does not keep track of the bifurcations so it is not
            # possible to order per bifurcation
            ordered_sections = np.copy(self.active_sections)

        for section_grower in ordered_sections:
            # the current section_grower is generated
            # In here the stop criterion can be modified accordingly

            if section_grower.process == "major" and "major_termination_length" in self.params:
                # this makes an early termination of major branch
                # it needs to revert the value after getting the state to preserve
                # the original topology
                _term = section_grower.stop_criteria["TMD"].term
                section_grower.stop_criteria["TMD"].term = self.params["major_termination_length"]
            else:
                _term = None

            state = self.growth_algo.extend(section_grower)

            if _term is not None:
                section_grower.stop_criteria["TMD"].term = _term

            if state != "continue":
                section = self.append_section(section_grower)

                if state == "bifurcate":
                    # Save the final normed direction of parent
                    latest = section_grower.latest_directions[-1]
                    section_grower.id = section.id

                    # we need this so that the path length matches due to the child.first_point()
                    for other_section in self.active_sections:
                        if other_section != section_grower:
                            other_section.next()

                    # the current section_grower bifurcates
                    # Returns two section_grower dictionaries: (S1, S2)
                    for child_section in self.growth_algo.bifurcate(section_grower):
                        child = self.add_section(
                            parent=section, pathlength=section_grower.pathlength, **child_section
                        )
                        # Copy the final normed direction of parent to all children
                        child.latest_directions.append(latest)
                        # Generate the first point of the section
                        child.first_point()
                    self.active_sections.remove(section_grower)

                elif state == "terminate":
                    # the current section_grower terminates
                    self.growth_algo.terminate(section_grower)
                    self.active_sections.remove(section_grower)

                else:
                    raise NeuroTSError(f"Unknown state during growth: {state}")  # pragma: no cover
