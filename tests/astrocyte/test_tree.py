from mock import Mock
import numpy as np

from neurots.astrocyte.context import SpaceColonizationContext
from neurots.astrocyte.section import SectionSpatialGrower
from neurots.astrocyte.tree import TreeGrowerSpaceColonization

from test_grower import _parameters, _distributions, _context


def test_tree_grower_space_colonization_constructor():

    neuron = Mock()
    initial_direction = np.array([0.12427115, 0.93206836, 0.3403017 ])
    initial_point = np.array([1.5411615 , 0.29389329, 0.15904417])

    grower_distributions = _distributions()
    grower_parameters = _parameters()
    grower_context = SpaceColonizationContext(_context())
    tree_parameters = grower_parameters['basal']
    tree_parameters['origin'] = np.zeros(3)
    tree_distributions = grower_distributions['basal']

    tree_grower = TreeGrowerSpaceColonization(neuron, initial_direction, initial_point, tree_parameters, tree_distributions, grower_context)

    assert isinstance(tree_grower.active_sections[0], SectionSpatialGrower)

    tree_parameters = grower_parameters['axon']
    tree_parameters['origin'] = np.zeros(3)
    tree_parameters['target_id'] = 0
    tree_parameters['distance_soma_target'] = 1.2
    tree_distributions = grower_distributions['axon']

    tree_grower = TreeGrowerSpaceColonization(neuron, initial_direction, initial_point, tree_parameters, tree_distributions, grower_context)
    assert isinstance(tree_grower.active_sections[0], SectionSpatialGrower)
