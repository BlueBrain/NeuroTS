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

import logging

import numpy as np

from neurots.generate.algorithms.abstractgrower import AbstractAlgo
from neurots.generate.algorithms.common import bif_methods
from neurots.generate.algorithms.common import section_data

logger = logging.getLogger(__name__)


class TrunkAlgo(AbstractAlgo):
    """TreeGrower basic growth of trunks class.

    Args:
        input_data (dict): All the data required for the growth.
        params (dict): The parameters required for growth.
        start_point (list[float]): The first point of the trunk.
        context (Any): An object containing contextual information.
    """

    def __init__(self, input_data, params, start_point, context=None, **_):
        """Constructor of the TrunkAlgo class."""
        super().__init__(input_data, params, start_point, context)
        self.bif_method = bif_methods[params["branching_method"]]

    def initialize(self):
        """Generates the data to be used for the initialization of the first section to be grown.

        Saves the extracted input data into the corresponding structures.
        """
        stop = {"num_seg": self.params["num_seg"]}
        num_sec = 1  # A single section per tree will be generated

        return stop, num_sec

    def bifurcate(self, current_section):
        """When the section bifurcates two new sections are created.

        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.

        Args:
            current_section (neurots.generate.section.SectionGrowerPath): The current section.

        Returns:
            tuple[dict, dict]: Two dictionaries containing the two children sections data.
        """
        dir1, dir2 = self.bif_method()
        first_point = np.array(current_section.last_point)
        stop = current_section.stop_criteria

        return (
            section_data(dir1, first_point, stop, current_section.process),
            section_data(dir2, first_point, stop, current_section.process),
        )

    def terminate(self, current_section):
        """Terminate the current section.

        When the growth of a section is terminated the "term" must be removed from the TMD grower.
        """

    def extend(self, current_section):
        """Extend the current section.

        Create a section with the selected parameters until at least one stop criterion is
        fulfilled.
        """
        return current_section.next()


class AxonAlgo(TrunkAlgo):
    """TreeGrower of axon growth.

    Only a trunk with one segment is synthesized and another process is supposed to gaft an actual
    axon on this trunk.
    """

    def __init__(self, *args, **kwargs):
        # Force num_seg in params to 1
        params = kwargs.get("params", None) or args[1]
        params["num_seg"] = 1

        super().__init__(*args, **kwargs)
