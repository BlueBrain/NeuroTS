'''
This test ensures that the radial and path distances are computed correctly through TNS,
so that the code is treating the input barcode, according to the given parameters.
For this reason, we need to check that the same input distribution
will generate cells with different properties, according to their input parameters.
Finally, we need to check the TMD of the produced cells.
'''


from tempfile import TemporaryDirectory
import json
import os
from os.path import join
import numpy as np
from scipy.spatial.distance import cdist
from numpy.testing import assert_almost_equal, assert_array_almost_equal
from nose.tools import assert_raises, ok_
from morph_tool import diff
from tns.generate.grower import NeuronGrower
import tmd

_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def assert_close_persistent_diagram(actual, expected):
    # compute distances between points
    distances = np.min(cdist(np.array(tmd.analysis.sort_ph(expected)), actual), axis=0)
    # We compare distances between expected and generated peristence as it is more stable to check.
    # This comparison does not depend on ordering of the points
    # and ensures that the points of the original persistence are consistently generated.
    assert_almost_equal(len(expected), len(actual))
    assert_array_almost_equal(distances, np.zeros(len(distances)), decimal=0.1)
    assert_almost_equal(np.max(expected[-1]), np.max(actual[-1]), decimal=0.1)


def _load_inputs(distributions, parameters):
    with open(distributions) as f:
        distributions = json.load(f)

    with open(parameters) as f:
        params = json.load(f)

    return distributions, params


def _test_full(feature, distributions, parameters, ref_cell, ref_persistence_diagram, save=False):

    np.random.seed(0)
    distributions, params = _load_inputs(join(_path, distributions), join(_path, parameters))
    n = NeuronGrower(input_distributions=distributions, input_parameters=params).grow()

    with TemporaryDirectory('test_grower') as folder:
        out_neuron = os.path.join(folder, 'test_output_neuron_.h5')
        n.write(out_neuron)
        # For checking purposes, we can output the cells as swc
        if save:
            n.write(ref_cell.replace('.h5', 'NEW.h5'))

        if ref_persistence_diagram is not None:
            # Load with TMD and extract radial persistence
            n0 = tmd.io.load_neuron(out_neuron)

            actual_persistence_diagram = tmd.methods.get_persistence_diagram(n0.apical[0], feature=feature)
            if save:
                print(actual_persistence_diagram)

            with open(join(_path, ref_persistence_diagram)) as f:
                expected_persistence_diagram = json.load(f)

            assert_close_persistent_diagram(actual_persistence_diagram,
                                            expected_persistence_diagram)

        ok_(not diff(out_neuron, os.path.join(_path, ref_cell)))


def test_wrong_filtration():
    '''Test filtration metric inconsistency in distrib and params: path != radial'''
    distributions, parameters = _load_inputs(os.path.join(_path, 'bio_path_distribution.json'),
                                             os.path.join(_path, 'bio_radial_params.json'))
    assert_raises(ValueError, NeuronGrower, parameters, distributions)


def test_basic_grower():
    _test_full('radial_distances',
               'bio_trunk_distribution.json',
               'trunk_parameters.json',
               'test_trunk_grower.h5',
               None)

def test_path_grower():
    '''test tmd_path and tmd_apical_path'''
    _test_full('path_distances',
               'bio_distribution.json',
               'bio_path_params.json',
               'path_grower.h5',
               'bio_path_persistence_diagram.json')

def test_gradient_path_grower():
    '''test tmd_path'''
    _test_full('path_distances',
              'bio_distribution.json',
              'bio_gradient_path_params.json',
              'gradient_path_grower.h5',
              'gradient_path_persistence_diagram.json')


def test_bio_rat_l5_tpc():
    _test_full('path_distances',
               'bio_rat_L5_TPC_B.json',
               'params1.json',
               'expected_bio_rat_L5_TPC_B_with_params1.h5',
               'expected_bio_rat_L5_TPC_B_with_params1_persistence_diagram.json')

    _test_full('path_distances',
               'bio_rat_L5_TPC_B.json',
               'params2.json',
               'expected_bio_rat_L5_TPC_B_with_params2.h5',
               'expected_bio_rat_L5_TPC_B_with_params2_persistence_diagram.json')

    _test_full('path_distances',
               'bio_rat_L5_TPC_B.json',
               'params3.json',
               'expected_bio_rat_L5_TPC_B_with_params3.h5',
               'expected_bio_rat_L5_TPC_B_with_params3_persistence_diagram.json')

    _test_full('path_distances',
               'bio_rat_L5_TPC_B.json',
               'params4.json',
               'expected_bio_rat_L5_TPC_B_with_params4.h5',
               'expected_bio_rat_L5_TPC_B_with_params4_persistence_diagram.json')
