'''
TNS class : Grower object that contains the grower functionality.
'''
import copy
import logging

import numpy as np
from numpy.random import BitGenerator, Generator, RandomState, SeedSequence

from morphio.mut import Morphology  # pylint: disable=import-error
from tns.generate import diametrizer
from tns.generate.soma import SomaGrower
from tns.generate.tree import TreeGrower
from tns.morphmath import sample
from tns.validator import validate_neuron_params, validate_neuron_distribs

L = logging.getLogger(__name__)

bifurcation_methods = ['symmetric', 'bio_oriented', 'directional', 'bio_smoothed']


class NeuronGrower:
    """
    A Grower object is a container for a Neuron, encoded in the (groups, points) structure,
    as a morphIO Morphology object. A set of input distributions that store the data
    consumed by the algorithms and the user-selected parameters are also stored.
    """

    def __init__(self, input_parameters, input_distributions,
                 context=None, external_diametrizer=None, skip_validation=False,
                 rng_or_seed=np.random):
        """TNS NeuronGrower
        input_parameters: the user-defined parameters
        input_distributions: distributions extracted from biological data
        context: an object containing contextual information
        external_diametrizer: diametrizer function for external diametrizer module
        skip_validation: if set to False, the parameters and distributions are validated
        rng_or_seed: should be a `numpy.random.Generator` or an object that can be used as a seed
        for the `numpy.random.default_rng()` function.
        """
        self.neuron = Morphology()
        self.context = context
        if rng_or_seed is None or isinstance(
            rng_or_seed,
            (int, np.integer, SeedSequence, BitGenerator)
        ):
            self._rng = np.random.default_rng(rng_or_seed)
        elif isinstance(rng_or_seed, (RandomState, Generator)) or rng_or_seed is np.random:
            self._rng = rng_or_seed
        else:
            raise TypeError(
                "The 'rng_or_seed' argument must be None, np.random or an instance of one of the "
                "following types: [int, SeedSequence, BitGenerator, RandomState, Generator]."
            )

        self.input_parameters = copy.deepcopy(input_parameters)
        L.debug('Input Parameters: %s', input_parameters)

        self.input_distributions = copy.deepcopy(input_distributions)

        # Validate parameters and distributions
        if not skip_validation:
            self.validate_params()
            self.validate_distribs()

        # Consistency check between parameters and distributions
        for tree_type in self.input_parameters['grow_types']:
            metric1 = self.input_parameters[tree_type].get('metric')
            metric2 = self.input_distributions[tree_type].get('filtration_metric')
            if metric1 != metric2:
                raise ValueError('Metric of parameters and distributions is inconsistent:' +
                                ' {} != {}'.format(metric1, metric2))

        method1 = self.input_parameters['diameter_params']['method']
        method2 = self.input_distributions['diameter']['method']
        if method1 != method2:
            raise ValueError('Diameters methods of parameters and distributions is inconsistent:' +
                            ' {} != {}'.format(method1, method2))

        if self.input_distributions['diameter']['method'] == 'external' \
                and external_diametrizer is None:
            raise ValueError('External diametrizer is missing the diametrizer function.')

        # A list of trees with the corresponding orientations
        # and initial points on the soma surface will be initialized.
        self.active_neurites = list()
        self.soma = SomaGrower(initial_point=self.input_parameters["origin"],
                               radius=sample.soma_size(self.input_distributions, self._rng),
                               context=context, random_generator=self._rng)
        # Create a list to expose apical sections for each apical tree in the neuron,
        # the user can call NeuronGrower.apical_sections to get section IDs whose the last
        # point is the apical point of each generated apical tree.
        self.apical_sections = list()

        # initialize diametrizer
        self._init_diametrizer(external_diametrizer=external_diametrizer)

    def validate_params(self):
        '''Validate the parameter dictionary'''
        validate_neuron_params(self.input_parameters)

    def validate_distribs(self):
        '''Validate the distribution dictionary'''
        validate_neuron_distribs(self.input_distributions)

    def next(self):
        '''Call the "next" method of each neurite grower'''
        for grower in list(self.active_neurites):
            if grower.end():
                # If tree is an apical, the apical points get appended at the end of growth
                # This will ensure that for each apical tree a relevant apical point,
                # will be exposed to the user as a set of 3D coordinates (x,y,z).
                if 'apical' in self.input_parameters['grow_types'] and \
                   grower.type == self.input_parameters['apical']['tree_type']:
                    self.apical_sections.append(grower.growth_algo.apical_section)
                self.active_neurites.remove(grower)
            else:
                grower.next_point()

    def grow(self):
        """Generates a neuron according to the input_parameters
        and the input_distributions. The neuron consists of a soma
        and a list of trees encoded in the h5 format as a set of points
        and groups.

        Returns the grown neuron
        """
        self._grow_soma()
        while self.active_neurites:
            self.next()  # pylint: disable=E1102
        self._post_grow()
        self._diametrize()
        return self.neuron

    def _post_grow(self):
        """ Actions after the morphology has been grown and before its diametrization """

    def _init_diametrizer(self, external_diametrizer=None):
        """set a diametrizer function"""
        if self.input_distributions['diameter']['method'] == 'default':
            self._diametrize = lambda: None
            L.warning('No diametrizer provided, so neurons will have default diameters.')
        else:
            if self.input_distributions['diameter']['method'] == 'external':
                if external_diametrizer is None:
                    raise Exception('Please provide an external diametrizer!')
                diam_method = external_diametrizer
            else:
                diam_method = self.input_distributions['diameter']['method']

            def _diametrize():
                """diametrizer function"""
                self.input_distributions['diameter']['apical_point_sec_ids'] = self.apical_sections
                neurite_types = self.input_parameters.get(
                    'diameter_params', {}
                ).get('neurite_types', None)
                if neurite_types is None:
                    neurite_types = self.input_parameters['grow_types']
                diametrizer.build(self.neuron, self.input_distributions['diameter'],
                                  neurite_types=neurite_types, diam_method=diam_method,
                                  random_generator=self._rng)
            self._diametrize = _diametrize

    def _convert_orientation2points(self, orientation, n_trees, distr, params):
        '''Checks the type of orientation input and returns the soma points generated by the
        corresponding selection. Currently accepted orientations include the following options:
        list of 3D points: select the orientation externally
        None: creates a list of orientations according to the biological distributions.
        'from_space': generates orientations depending on spatial input (not implemented yet).
        '''

        if isinstance(orientation, list):  # Gets major orientations externally
            assert np.all(np.linalg.norm(orientation, axis=1) > 0), (
                'Orientations should have non-zero lengths')
            if params.get('trunk_absolute_orientation', False):
                if len(orientation) == 1:
                    # Pick random absolute angles
                    trunk_absolute_angles = sample.trunk_absolute_angles(distr, n_trees, self._rng)
                    z_angles = sample.azimuth_angles(distr, n_trees, self._rng)
                    pts = self.soma.add_points_from_trunk_absolute_orientation(
                        orientation, trunk_absolute_angles, z_angles)
                else:
                    raise ValueError('The orientation should contain exactly one point!')
            else:
                if len(orientation) >= n_trees:
                    # TODO: pick orientations randomly?
                    pts = self.soma.add_points_from_orientations(orientation[:n_trees])
                else:
                    raise ValueError('Not enough orientation points!')
        elif orientation is None:  # Samples from trunk_angles
            trunk_angles = sample.trunk_angles(distr, n_trees, self._rng)
            trunk_z = sample.azimuth_angles(distr, n_trees, self._rng)
            pts = self.soma.add_points_from_trunk_angles(trunk_angles, trunk_z)
        elif orientation == 'from_space':
            raise ValueError('Not implemented yet!')
        else:
            raise ValueError('Input orientation format is not correct!')
        return pts

    def _grow_trunks(self):
        """Generates the initial points of each tree, which depend on the selectedS
        tree types and the soma surface. All the trees start growing from the surface
        of the soma. The outgrowth direction is either specified in the input parameters,
        as parameters['type']['orientation'] or it is randomly chosen according to the
        biological distribution of trunks on the soma surface if 'orientation' is None.
        """

        for type_of_tree in self.input_parameters['grow_types']:
            # Easier to access distributions
            params = self.input_parameters[type_of_tree]
            distr = self.input_distributions[type_of_tree]

            # Sample the number of trees depending on the tree type
            n_trees = sample.n_neurites(distr["num_trees"], self._rng)
            if type_of_tree == 'basal' and n_trees < 2:
                raise Exception('There should be at least 2 basal dendrites (got {})'.format(
                    n_trees))

            orientation = params['orientation']
            # Clean up orientation options in converting function
            points = self._convert_orientation2points(orientation, n_trees, distr, params)

            # Iterate over all initial points on the soma and create new trees
            # with a direction and initial_point
            for p in points:
                tree_direction = self.soma.orientation_from_point(p)
                obj = TreeGrower(self.neuron,
                                 initial_direction=tree_direction,
                                 initial_point=p,
                                 parameters=params,
                                 distributions=distr,
                                 context=self.context,
                                 random_generator=self._rng)
                self.active_neurites.append(obj)

    def _grow_soma(self, soma_type='contour'):
        """Generates a soma based on the input_distributions. The coordinates
        of the soma contour are retrieved from the trunks.
        """
        self._grow_trunks()

        points, diameters = self.soma.build(soma_type)
        self.neuron.soma.points = points
        self.neuron.soma.diameters = diameters
