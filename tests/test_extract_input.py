from nose import tools as nt
from nose.tools import assert_dict_equal
import neurom
import numpy as np
from numpy.testing import assert_array_almost_equal
from tns import extract_input
import os

_path = os.path.dirname(os.path.abspath(__file__))
POP_PATH = os.path.join(_path, '../test_data/bio/')

POPUL = neurom.load_neurons(POP_PATH)

def test_num_trees():
    target_numBAS = {'num_trees': {'data': {'bins': [4, 5, 6, 7, 8, 9],
                                      'weights': [1, 0, 0, 0, 0, 1]}}}
    target_numAX =  {'num_trees': {'data': {'bins': [1], 'weights': [2]}}}

    numBAS = extract_input.from_neurom.number_neurites(POPUL)
    numAX = extract_input.from_neurom.number_neurites(POPUL, neurite_type=neurom.AXON)
    assert_dict_equal(numBAS, target_numBAS)
    assert_dict_equal(numAX, target_numAX)

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
    assert_dict_equal(trunkBAS, target_trunkBAS)
    assert_dict_equal(trunkAP, target_trunkAPIC)

