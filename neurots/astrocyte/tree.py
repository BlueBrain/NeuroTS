"""NeuroTS class: Tree."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy

from neurots.astrocyte.section import SectionSpatialGrower
from neurots.astrocyte.space_colonization import SpaceColonization
from neurots.astrocyte.space_colonization import SpaceColonizationTarget
from neurots.generate.tree import TreeGrower

GROWTH_ALGORITHMS = {
    "tmd_space_colonization": SpaceColonization,
    "tmd_space_colonization_target": SpaceColonizationTarget,
}

SECTION_GROWERS = {
    "tmd_space_colonization": SectionSpatialGrower,
    "tmd_space_colonization_target": SectionSpatialGrower,
}


class TreeGrowerSpaceColonization(TreeGrower):
    """Tree class."""

    def _initialize_algorithm(self):
        """Initialization steps."""
        grow_meth = GROWTH_ALGORITHMS[self.params["growth_method"]]

        growth_algo = grow_meth(
            input_data=self.distr,
            params=self.params,
            start_point=self.point,
            context=self.context,
            random_generator=self._rng,
        )

        stop, num_sec = growth_algo.initialize()

        section = self.add_section(
            parent=None,
            direction=self.direction,
            first_point=self.point,
            stop=copy.deepcopy(stop),
            process="major",
            pathlength=0.0,
            children=2 if num_sec > 1 else 0,
        )

        # First section of the tree has at least one point.
        section.first_point()

        return growth_algo

    def add_section(
        self, parent, direction, first_point, stop, pathlength, process=None, children=0
    ):
        """Generates a section from the parent section "act" from all the required information.

        The section is added to the neuron.sections and activated.
        """
        SGrower = SECTION_GROWERS[self.params["growth_method"]]

        sec_grower = SGrower(
            parent=parent,
            children=children,
            first_point=first_point,
            direction=direction,
            parameters=self._section_parameters,
            process=process,
            stop_criteria=copy.deepcopy(stop),
            step_size_distribution=self.seg_length_distr,
            pathlength=pathlength,
            context=self.context,
            random_generator=self._rng,
        )

        self.active_sections.append(sec_grower)
        return sec_grower
