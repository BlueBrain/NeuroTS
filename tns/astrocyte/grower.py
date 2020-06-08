'''
TNS class : Grower object that contains the grower functionality.
'''
import logging
from copy import deepcopy

import numpy as np
from scipy.spatial import cKDTree

from morphio import SectionType
from tns.generate.grower import NeuronGrower

from tns.morphmath import sample
from tns.astrocyte.tree import TreeGrowerSpaceColonization
from tns.astrocyte.context import SpaceColonizationContext
from tns.astrocyte.section import grow_to_target
from tns.astrocyte.math_utils import normalize_vectors
from tns.astrocyte.math_utils import norm as vectorial_norm


L = logging.getLogger(__name__)


def _number_of_trees(tree_type, orientations, distributions):
    """ Sample the number of trees depending on the tree type if no predef orientations
    """
    if orientations is None:
        n_trees = sample.n_neurites(distributions["num_trees"])
    else:
        n_trees = len(orientations)

    if tree_type == 'basal' and n_trees < 2:
        raise Exception('There should be at least 2 basal dendrites (got {})'.format(
            n_trees))

    return n_trees


def _ensure_endfeet_are_reached(cell, targets):
    """ If there are any targets left active, i.e. not reached, the closest section to each one
    of them will be grown to reach it. This is the last resort to ensure that endfeet targets will
    be reached no matter what. However, a warning will be emitted.
    """
    perivascular_terminations = [
        s for s in cell.iter() if s.type == SectionType(2) and len(s.children) == 0
    ]

    termination_points = np.array([s.points[-1] for s in perivascular_terminations])

    target_points = targets.active_points
    distances, section_indices = cKDTree(termination_points, copy_data=False).query(target_points)

    for distance, section_index, target_point in zip(distances, section_indices, target_points):

        if not np.isclose(distance, 0.0):

            L.warning('Target %s was not reached. Extending closest section to reach it.', target_point)

            section = perivascular_terminations[section_index]
            points, diameters = section.points, section.diameters

            vector = points[-1] - points[-2]
            segment_length = np.linalg.norm(vector)
            direction = vector / segment_length

            new_points = grow_to_target(points[-1], direction, target_point, segment_length)

            section.points = np.vstack((points, new_points))
            section.diameters = np.hstack((diameters, np.full(len(new_points), fill_value=diameters[-1])))


class AstrocyteGrower(NeuronGrower):
    """
    A Grower object is a container for an Astrocyte, encoded in the (groups, points) structure,
    as a morphIO Morphology object. A set of input distributions that store the data
    consumed by the algorithms and the user-selected parameters are also stored.
    """
    def __init__(self, input_parameters, input_distributions, context, external_diametrizer=None):
        super().__init__(
            input_parameters, input_distributions,
            context=SpaceColonizationContext(context),
            external_diametrizer=external_diametrizer)

    def validate_params(self):
        """Astrocyte parameter validation"""

    def validate_distribs(self):
        """Astrocyte distribution validation"""

    def _post_grow(self):
        """After the cell has grown ensure that endfeet targets have been reached """
        endfeet_targets = self.context.endfeet_targets
        if endfeet_targets is not None and np.any(endfeet_targets.active):
            _ensure_endfeet_are_reached(self.neuron, self.context.endfeet_targets)

    def _add_active_neurite(self, initial_soma_point, parameters, distributions):
        """Create a TreeGrower with the input data and add it to the active neurites
        """
        tree_direction = self.soma.orientation_from_point(initial_soma_point)

        obj = TreeGrowerSpaceColonization(self.neuron,
                         initial_direction=tree_direction,
                         initial_point=initial_soma_point,
                         parameters=parameters,
                         distributions=distributions,
                         context=self.context)

        self.active_neurites.append(obj)

    def _orientations_to_points(self, orientations, n_trees, distr):
        '''Checks the type of orientation input and returns the soma points generated by the
        corresponding selection. Currently accepted orientations include the following options:
        list of 3D points: select the orientation externally
        None: creates a list of orientations according to the biological distributions.
        'from_space': generates orientations depending on spatial input (not implemented yet).
        '''
        if orientations is None:
            assert n_trees != 0, "Number of trees should be greater than zero"
            trunk_angles = sample.trunk_angles(distr, n_trees)
            trunk_z = sample.azimuth_angles(distr, n_trees)
            return self.soma.add_points_from_trunk_angles(trunk_angles, trunk_z)

        assert len(orientations) >= n_trees, "n_orientations < n_trees"
        return self.soma.add_points_from_orientations(orientations[:n_trees])

    def _create_process_trunks(self, tree_type, parameters, distributions):
        """Creates the starts of the processes for the astrocyte
        Args:
            tree_type (str)
            parameters (dict)
            distributions (distributions)

        Notes:
            Astrocytic perivascular type corresponds to the neuronal axon, while
            perisynaptic type to basal or apical type.
        """
        tree_type = 'perivascular' if tree_type == 'axon' else 'perisynaptic'

        if tree_type == 'perivascular':

            target_ids = np.array(parameters['target_ids'], dtype=np.int32)
            target_points = self.context.endfeet_targets.points[target_ids]

            orientations = normalize_vectors(
                np.array(
                    [self.soma.orientation_from_point(p) for p in target_points],
                    dtype=np.float32)
            )

            trunk_points = self.soma.add_points_from_orientations(orientations)

            assert len(target_ids) == len(trunk_points), \
                "Number of targets is not equal to number of orientations"

            for target_id, trunk_point in zip(target_ids, trunk_points):

                neurite_params = deepcopy(parameters)
                neurite_params['target_id'] = target_id
                neurite_params['distance_soma_target'] = vectorial_norm(
                    self.soma.center - self.context.endfeet_targets.points[target_id]
                )
                self._add_active_neurite(trunk_point, neurite_params, distributions)
        else:

            orientations = parameters['orientation']

            if orientations is not None:
                orientations = normalize_vectors(np.array(orientations, dtype=np.float32))

            trunk_points = self._orientations_to_points(
                orientations,
                _number_of_trees(tree_type, orientations, distributions),
                distributions)

            for i, trunk_point in enumerate(trunk_points):

                neurite_params = deepcopy(parameters)
                if 'domain_distances' in neurite_params:
                    neurite_params['distance_to_domain'] = parameters['domain_distances'][i]
                self._add_active_neurite(trunk_point, neurite_params, distributions)

    def _grow_trunks(self):
        """Generates the initial points of each tree, which depend on the selected
        tree types and the soma surface. All the trees start growing from the surface
        of the soma. The outgrowth direction is either specified in the input parameters,
        as parameters['type']['orientation'] or it is randomly chosen according to the
        biological distribution of trunks on the soma surface if 'orientation' is None.
        """
        origin = np.array(self.input_parameters['origin'], dtype=np.float32)

        for tree_type in self.input_parameters['grow_types']:
            parameters = self.input_parameters[tree_type]
            distributions = self.input_distributions[tree_type]
            parameters['origin'] = origin
            self._create_process_trunks(tree_type, parameters, distributions)
