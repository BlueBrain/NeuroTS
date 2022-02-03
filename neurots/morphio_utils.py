"""Models to create diameters of synthesized cells."""

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

from morphio import SectionType
from neurom import NeuriteType

STR_TO_TYPES = {
    "apical": SectionType.apical_dendrite,
    "basal": SectionType.basal_dendrite,
    "axon": SectionType.axon,
}

TYPE_TO_STR = {
    SectionType.apical_dendrite: "apical",
    SectionType.basal_dendrite: "basal",
    SectionType.axon: "axon",
    SectionType.soma: "soma",
}


NEUROM_TYPE_TO_STR = {
    NeuriteType.apical_dendrite: "apical",
    NeuriteType.basal_dendrite: "basal",
    NeuriteType.soma: "soma",
    NeuriteType.axon: "axon",
}

STR_TO_NEUROM_TYPES = {
    "apical": NeuriteType.apical_dendrite,
    "basal": NeuriteType.basal_dendrite,
    "soma": NeuriteType.soma,
    "axon": NeuriteType.axon,
}


def section_filter(neuron, tree_type=None):
    """Filters all sections according to type."""
    if tree_type is None:
        return list(neuron.iter())
    return [i for i in neuron.iter() if i.type == tree_type]


def root_section_filter(neuron, tree_type=None):
    """Filters root sections according to type."""
    if tree_type is None:
        return list(neuron.root_sections)
    return [i for i in neuron.root_sections if i.type == tree_type]
