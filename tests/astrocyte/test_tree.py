"""Test neurots.astrocyte.tree code."""

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

# pylint: disable=missing-function-docstring
import numpy as np
from mock import Mock

from neurots.astrocyte.context import SpaceColonizationContext
from neurots.astrocyte.section import SectionSpatialGrower
from neurots.astrocyte.tree import TreeGrowerSpaceColonization

from .test_grower import _context
from .test_grower import _distributions
from .test_grower import _parameters


def test_tree_grower_space_colonization_constructor():
    neuron = Mock()
    initial_direction = np.array([0.12427115, 0.93206836, 0.3403017])
    initial_point = np.array([1.5411615, 0.29389329, 0.15904417])

    grower_distributions = _distributions()
    grower_parameters = _parameters()
    grower_context = SpaceColonizationContext(_context())
    tree_parameters = grower_parameters["basal"]
    tree_parameters["origin"] = np.zeros(3)
    tree_distributions = grower_distributions["basal"]

    tree_grower = TreeGrowerSpaceColonization(
        neuron,
        initial_direction,
        initial_point,
        tree_parameters,
        tree_distributions,
        grower_context,
    )

    assert isinstance(tree_grower.active_sections[0], SectionSpatialGrower)

    tree_parameters = grower_parameters["axon"]
    tree_parameters["origin"] = np.zeros(3)
    tree_parameters["target_id"] = 0
    tree_parameters["distance_soma_target"] = 1.2
    tree_distributions = grower_distributions["axon"]

    tree_grower = TreeGrowerSpaceColonization(
        neuron,
        initial_direction,
        initial_point,
        tree_parameters,
        tree_distributions,
        grower_context,
    )
    assert isinstance(tree_grower.active_sections[0], SectionSpatialGrower)
