from nose import tools as nt
from nose.tools import assert_dict_equal
import neurom
from neurom import load_neurons
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal, assert_equal, assert_raises
from tns import extract_input
import os
import json

from tns import TNSError
import tns.extract_input as test_module


_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_data')
POP_PATH = os.path.join(_PATH, 'bio/')
NEU_PATH = os.path.join(_PATH, 'diam_simple.swc')

POPUL = load_neurons(POP_PATH)
NEU = load_neurons(NEU_PATH)

def test_num_trees():
    target_numBAS = {'num_trees': {'data': {'bins': [4, 5, 6, 7, 8, 9],
                                      'weights': [1, 0, 0, 0, 0, 1]}}}
    target_numAX =  {'num_trees': {'data': {'bins': [1], 'weights': [2]}}}

    numBAS = extract_input.from_neurom.number_neurites(POPUL)
    numAX = extract_input.from_neurom.number_neurites(POPUL, neurite_type=neurom.AXON)
    assert_equal(numBAS, target_numBAS)
    assert_equal(numAX, target_numAX)

def test_trunk_distr():
    target_trunkBAS = {'trunk':
                      {'azimuth': {'uniform': {'max': 0.0, 'min': np.pi}},
                                   'orientation_deviation': {'data': {'bins': [0.19391773616376634,
                                                                               0.4880704446023673,
                                                                               0.7822231530409682,
                                                                               1.076375861479569,
                                                                               1.3705285699181702,
                                                                               1.6646812783567713,
                                                                               1.9588339867953721,
                                                                               2.2529866952339734,
                                                                               2.547139403672574,
                                                                               2.841292112111175],
                                                                       'weights': [4, 3, 1, 2, 0, 1, 0, 0, 0, 2]}}}}
    target_trunkAPIC = {'trunk': {'azimuth': {'uniform': {'max': 0.0, 'min': np.pi}},
                                  'orientation_deviation': {'data': {'bins': [0.0], 'weights': [2]}}}}

    trunkAP = extract_input.from_neurom.trunk_neurite(POPUL, neurite_type=neurom.APICAL_DENDRITE, bins=1)
    trunkBAS = extract_input.from_neurom.trunk_neurite(POPUL, bins=10)
    assert_equal(trunkBAS, target_trunkBAS)
    assert_equal(trunkAP, target_trunkAPIC)

def test_diameter_extract():
    res = extract_input.from_diameter.model(NEU)
    assert_equal(set(res.keys()), {'basal'})
    expected = {'Rall_ratio': 1.5,
                'siblings_ratio': 1.0,
                'taper': [0.24, 0.1],
                'term': [2.0, 2.0],
                'trunk': [3.9],
                'trunk_taper': [0.30]}

    assert_equal(set(res['basal'].keys()), set(expected.keys()))
    for key in expected.keys():
        assert_array_almost_equal(res['basal'][key], expected[key])

    assert_raises(TNSError, extract_input.from_diameter.model,
                  load_neurons(os.path.join(_PATH, 'simple.swc')))


def test_distributions():
    filename = os.path.join(_PATH, 'bio/')
    distr = test_module.distributions(filename)
    assert_equal(set(distr.keys()), {'soma', 'basal', 'apical', 'axon'})
    assert_equal(distr['basal']['num_trees'],
                 {'data': {'bins': [4, 5, 6, 7, 8, 9], 'weights': [1, 0, 0, 0, 0, 1]}})
    assert_equal(distr['basal']['filtration_metric'], 'radial_distances')
    distr = test_module.distributions(filename, feature='path_distances')
    assert_equal(distr['basal']['filtration_metric'], 'path_distances')

def test_parameters():
    params = test_module.parameters(
        neurite_types=['basal', 'apical'], method='tmd')

    assert_equal(params,
    {'basal': {'randomness': 0.15, 'targeting': 0.12, 'radius': 0.3, 'orientation': None, 
              'growth_method': 'tmd', 'branching_method': 'bio_oriented', 'modify': None,
              "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
              'tree_type': 3, 'metric': 'radial_distances'},
     'apical': {'randomness': 0.15, 'targeting': 0.12, 'radius': 0.3, 'orientation': [(0.0, 1.0, 0.0)],
                'growth_method': 'tmd_apical', 'branching_method': 'directional', 'modify': None,
                "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                'tree_type': 4, 'metric': 'radial_distances'},
     'axon': {}, 'origin': (0.0, 0.0, 0.0), 'grow_types': ['basal', 'apical']})
