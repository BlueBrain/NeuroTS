from nose import tools as nt
from nose.tools import assert_dict_equal
import neurom
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal, assert_equal
from tns import extract_input
import os
import json
import tns.extract_input as test_module


_path = os.path.dirname(os.path.abspath(__file__))
POP_PATH = os.path.join(_path, '../test_data/bio/')
NEU_PATH = os.path.join(_path, '../test_data/diam_simple.swc')

POPUL = neurom.load_neurons(POP_PATH)
NEU = neurom.load_neurons(NEU_PATH)

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
    model0 =  {3: {'Rall_ratio': 0.6666666666666666,
                   'siblings_ratio': 1.0,
                   'taper': [0.24000000000000005, 0.1],
                   'term': [2.0, 2.0],
                   'trunk': [3.9],
                   'trunk_taper': [0.3000000000000001]}}
    assert_equal(model0, extract_input.from_diameter.model(NEU))


class NeuromJSON(json.JSONEncoder):
    '''JSON encoder that handles numpy types

    In python3, numpy.dtypes don't serialize to correctly, so a custom converter
    is needed.
    '''

    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, np.floating):
            return float(o)
        elif isinstance(o, np.integer):
            return int(o)
        elif isinstance(o, np.ndarray):
            return o.tolist()
        return json.JSONEncoder.default(self, o)


def test_distributions():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(dir_path, '../test_data/bio/')
    distr = test_module.distributions(filename)

    assert_equal(set(distr.keys()), {'soma', 'basal', 'apical', 'axon'})
    assert_equal(distr['basal']['num_trees'],
                 {'data': {'bins': [4, 5, 6, 7, 8, 9], 'weights': [1, 0, 0, 0, 0, 1]}})

def test_parameters():
    params = test_module.parameters(
        neurite_types=['basal', 'apical'], method='tmd')

    assert_equal(params,
    {'basal': {'randomness': 0.15, 'targeting': 0.12, 'radius': 0.3, 'orientation': None, 'growth_method': 'tmd', 'branching_method': 'bio_oriented', 'modify': None, 'tree_type': 3}, 'apical': {'randomness': 0.15, 'targeting': 0.12, 'radius': 0.3, 'orientation': [(0.0, 1.0, 0.0)], 'growth_method': 'tmd_apical', 'branching_method': 'directional', 'modify': None, 'apical_distance': 0.0, 'tree_type': 4}, 'axon': {}, 'origin': (0.0, 0.0, 0.0), 'grow_types': ['basal', 'apical']})
