"""Basic class for TreeGrower Algorithms."""

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
import logging

import numpy as np

from neurots.generate.algorithms.abstractgrower import AbstractAlgo
from neurots.generate.algorithms.barcode import Barcode
from neurots.generate.algorithms.common import TMDStop
from neurots.generate.algorithms.common import bif_methods
from neurots.generate.algorithms.common import section_data
from neurots.morphmath import sample
from neurots.morphmath.utils import norm

L = logging.getLogger(__name__)


class TMDAlgo(AbstractAlgo):
    """TreeGrower of TMD basic growth.

    Args:
        input_data (dict): All the data required for the growth.
        params (dict): The parameters required for growth. It should include the
            ``branching_method`` selected from: ``|bio_oriented, symmetric, directional]``.
        start_point (list[float]): The first point of the trunk.
            the "min_bar_length" parameter are validated.
        context (Any): An object containing contextual information.
        random_generator (numpy.random.Generator): The random number generator to use.
    """

    def __init__(
        self,
        input_data,
        params,
        start_point,
        context=None,
        random_generator=np.random,
        **_,
    ):
        """TMD basic grower."""
        super().__init__(input_data, params, start_point, context)
        self.bif_method = bif_methods[params["branching_method"]]
        self.ph_angles = self.select_persistence(input_data, random_generator)
        self.barcode = Barcode(list(self.ph_angles))
        self.apical_section = None
        self.apical_point_distance_from_soma = 0.0
        self.persistence_length = self.barcode.get_persistence_length()

    def select_persistence(self, input_data, random_generator=np.random):
        """Select the persistence.

        Sample one persistence diagram from a list of diagrams and modifies according to input
        parameters.
        """
        list_of_persistences = input_data["persistence_diagram"]
        persistence = sample.ph(list_of_persistences, random_generator)

        if self.params.get("modify"):
            persistence = self.params["modify"]["funct"](
                persistence, self.context, **self.params["modify"]["kwargs"]
            )
        return persistence

    @staticmethod
    def metric_ref(section):
        """Return the metric reference.

        The metric reference is the path distance reference, or zero if no section is provided as
        input.
        """
        # Function to return reference for path distance
        if section:
            return section.pathlength
        return 0.0

    @staticmethod
    def metric(section):
        """Return the metric at the current position, here path distance, recorded in section."""
        # Function to return path distance
        return section.pathlength

    def get_stop_criteria(self, current_section):
        """Return stop criteria that are the commonly shared by all TMDPath algorithms.

        Returns:
            tuple[dict, dict]: Two dictionaries, each containing one entry whose key is ``TMD`` and
            value is a :class:`neurots.generate.algorithms.common.TMDStop` object.
        """
        # Ensure that reference is correctly assigned
        current_section.stop_criteria["TMD"].ref = self.metric_ref(current_section)
        # Copy the values for the parent stop TMD to use
        parent_tmd = copy.deepcopy(current_section.stop_criteria["TMD"])
        # Save the values of bifurcation for parent
        parent_bif_id = parent_tmd.bif_id
        parent_bif = parent_tmd.bif
        # Define the current criterion, inherited from parent
        current_tmd = copy.deepcopy(current_section.stop_criteria["TMD"])

        # The termination remains the same, so it is always True that
        # current_tmd.term <= parent_tmd.term
        # We find the smallest bifurcation that fulfils requirements
        # parent_tmd.ref <= current_tmd.bif <= parent_tmd.term
        # Bifurcation is larger than current reference distance
        bif_id, bif = self.barcode.min_bif(bif_above=parent_tmd.ref, bif_below=parent_tmd.term)
        # Update the bifurcation in the stop_criterion
        current_tmd.update_bif(bif_id, bif)
        # Ensure that criterion fulfils all requirements
        # the term that corresponds to current_tmd.bif term_target
        # term_target <= parent_tmd.term
        # If not re-assign a new one, find the min bifurcation for which:
        # term_target <= parent_tmd.term
        target_stop1 = self.barcode.curate_stop_criterion(parent_tmd, current_tmd)
        stop1 = {"TMD": target_stop1}
        # Find the termination that fulfils the requirement
        # termination <= current termination

        # Use the current bifurcation to determine the respective termination
        # Bifurcation should be larger than current reference distance
        term_id, term = self.barcode.get_term_between(parent_bif_id, parent_bif, current_tmd.term)
        current_tmd.update_term(term_id, term)

        # Get a stop criterion that fulfils requirements
        target_stop2 = self.barcode.curate_stop_criterion(parent_tmd, current_tmd)
        stop2 = {"TMD": target_stop2}

        return (stop1, stop2)

    def initialize(self):
        """Generates the data to be used for the initialization of the first section to be grown.

        Saves the extracted input data into the corresponding structures.

        Returns:
            tuple[TMDStop, int]: A :class:`neurots.generate.algorithms.common.TMDStop` object and
            the number of sections.
        """
        b0_id, b0 = self.barcode.min_bif()
        t0_id, t0 = self.barcode.max_term()
        stop = {
            "TMD": TMDStop(ref=self.metric_ref(None), bif_id=b0_id, bif=b0, term_id=t0_id, term=t0)
        }

        num_sec = len(self.ph_angles)

        return stop, num_sec

    def bifurcate(self, current_section):
        """When the section bifurcates two new sections need to be created.

        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.

        Returns:
            tuple[dict, dict]: Two dictionaries containing the data of the two children sections.
        """
        self.barcode.remove_bif(current_section.stop_criteria["TMD"].bif_id)
        ang = self.barcode.angles[current_section.stop_criteria["TMD"].bif_id]

        dir1, dir2 = self.bif_method(current_section.history(), angles=ang)
        first_point = np.array(current_section.last_point)

        stop1, stop2 = self.get_stop_criteria(current_section)

        return (
            section_data(dir1, first_point, stop1, current_section.process),
            section_data(dir2, first_point, stop2, current_section.process),
        )

    def terminate(self, current_section):
        """Terminate the current section.

        When the growth of a section is terminated the "term" must be removed from the TMD grower.
        """
        self.barcode.remove_term(current_section.stop_criteria["TMD"].term_id)

    def extend(self, current_section):
        """Definition of stop criterion for the growth of the current section."""
        criteria_tmd = copy.deepcopy(current_section.stop_criteria["TMD"])
        maximum_target = current_section.stop_criteria["TMD"].term
        reference = current_section.stop_criteria["TMD"].ref

        # We check that the current bifurcation has not been used
        if criteria_tmd.bif_id not in self.barcode.bifs and not np.isinf(criteria_tmd.bif):
            criteria_tmd.update_bif(
                *self.barcode.min_bif(bif_above=reference, bif_below=maximum_target)
            )
            criteria_tmd = self.barcode.curate_stop_criterion(criteria_tmd, criteria_tmd)

        # We check that the current termination has not been used
        if criteria_tmd.term_id not in self.barcode.terms:
            # Termination must be larger that bifurcation
            # unless if bifurcation is infinite
            reference = criteria_tmd.bif if not np.isinf(criteria_tmd.bif) else criteria_tmd.ref
            criteria_tmd.update_term(
                *self.barcode.min_term(term_above=reference, term_below=maximum_target)
            )
            criteria_tmd = self.barcode.curate_stop_criterion(criteria_tmd, criteria_tmd)

        current_section.stop_criteria["TMD"] = criteria_tmd

        return current_section.next()


class TMDApicalAlgo(TMDAlgo):
    """TreeGrower of TMD apical growth."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._found_last_bif = False

    def initialize(self):
        """Initialize the algorithm.

        TMD basic grower of an apical tree based on path distance.
        Initializes the tree grower and computes the apical distance using the input barcode.
        """
        # pylint: disable=C0415
        from tmd.Topology.analysis import find_apical_point_distance_smoothed as ap_dist

        stop, num_sec = super().initialize()
        if self.params.get("has_apical_tuft", False):
            self.apical_point_distance_from_soma = ap_dist(self.ph_angles)
        else:
            # If cell does not have a tuft return the distance before last bifurcation
            # this will result in a point very close to the proximal apical point.
            step_size = self.params["step_size"]["norm"]["mean"]
            selected_length = list(self.barcode.bifs.values())[-1]
            # From last bifurcation subtract 10 step sizes for apical point distance
            self.apical_point_distance_from_soma = selected_length - 10 * step_size
        return stop, num_sec

    def bifurcate(self, current_section):
        """When the section bifurcates two new sections need to be created.

        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.

        Returns:
            tuple[dict, dict]: Two dictionaries containing the data of the two children sections.
        """
        self.barcode.remove_bif(current_section.stop_criteria["TMD"].bif_id)
        ang = self.barcode.angles[current_section.stop_criteria["TMD"].bif_id]
        current_pd = self.metric(current_section)
        first_point = np.array(current_section.last_point)

        if current_section.process == "major":
            dir1, dir2 = bif_methods["directional"](current_section.direction, angles=ang)

            if not self._found_last_bif:
                self.apical_section = current_section.id

            if current_pd <= self.apical_point_distance_from_soma:
                process1 = "major"
                process2 = "secondary"
            else:
                process1 = "secondary"
                process2 = "secondary"

                if not self._found_last_bif:
                    self._found_last_bif = True
        else:
            dir1, dir2 = self.bif_method(current_section.history(), angles=ang)
            process1 = "secondary"
            process2 = "secondary"

            if not self._found_last_bif:
                self.apical_section = current_section.id

                if current_pd > self.apical_point_distance_from_soma:
                    self._found_last_bif = True

        stop1, stop2 = self.get_stop_criteria(current_section)

        return (
            section_data(dir1, first_point, stop1, process1),
            section_data(dir2, first_point, stop2, process2),
        )


class TMDGradientAlgo(TMDApicalAlgo):
    """TreeGrower of TMD apical growth."""

    def _majorize_process(self, section, stop, process, input_dir):
        """Currates the non-major processes to apply a gradient to large components."""
        bias_length = self.params["bias_length"] * self.persistence_length
        difference = stop.expected_maximum_length()
        if difference > bias_length:
            direction1 = (1.0 - self.params["bias"]) * np.array(input_dir)
            direction2 = self.params["bias"] * np.array(section.direction)
            direct = np.add(direction1, direction2)
            return "major", direct / norm(direct)
        return process, input_dir

    def bifurcate(self, current_section):
        """When the section bifurcates two new sections need to be created.

        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.

        Returns:
            tuple[dict, dict]: Two dictionaries containing the two children sections data.
        """
        s1, s2 = super().bifurcate(current_section)

        if s1["process"] != "major":
            s1["process"], s1["direction"] = self._majorize_process(
                current_section, s1["stop"]["TMD"], s1["process"], s1["direction"]
            )
        if s2["process"] != "major":
            s2["process"], s2["direction"] = self._majorize_process(
                current_section, s2["stop"]["TMD"], s2["process"], s2["direction"]
            )
        return s1, s2
