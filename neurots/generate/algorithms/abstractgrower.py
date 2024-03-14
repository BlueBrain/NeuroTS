"""Abstract class for TreeGrower Algorithms."""

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

import abc
import copy


class AbstractAlgo:
    """TreeGrower abstract class.

    Args:
        input_data (dict): All the data required for the growth.
        params (dict): The parameters required for growth.
        start_point (list[float]): The first point of the trunk.
        context (Any): An object containing contextual information.
    """

    # meta class is used to define other classes
    __metaclass__ = abc.ABCMeta

    def __init__(self, input_data, params, start_point, context):
        """The TreeGrower Algorithm initialization."""
        self.context = context
        self.input_data = copy.deepcopy(input_data)
        self.params = copy.deepcopy(params)
        self.start_point = start_point

    @abc.abstractmethod
    def initialize(self):
        """Abstract TreeGrower Algorithm initialization.

        Generates the data to be used for the initialization of the first section to be grown.
        """

    @abc.abstractmethod
    def bifurcate(self, current_section):
        """When the section bifurcates two new sections need to be created.

        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """

    @abc.abstractmethod
    def terminate(self, current_section):
        """Terminate the current section.

        When the growth of a section is terminated the "term" must be removed from the TMD grower.
        """

    @abc.abstractmethod
    def extend(self, current_section):
        """Definition of stop criterion for the growth of the current section."""
