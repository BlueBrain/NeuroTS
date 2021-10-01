import os
import json

import neurom
import numpy as np
import pytest
from neurom import load_morphologies
from neurom import stats
from numpy.testing import assert_array_almost_equal
from numpy.testing import assert_array_equal
from numpy.testing import assert_equal

from neurots import extract_input
from neurots import NeuroTSError


_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_data')
POP_PATH = os.path.join(_PATH, 'bio/')
NEU_PATH = os.path.join(_PATH, 'diam_simple.swc')


@pytest.fixture
def POPUL():
    return load_morphologies(POP_PATH)


@pytest.fixture
def NEU():
    return load_morphologies(NEU_PATH)


def test_num_trees(POPUL):
    target_numBAS = {'num_trees': {'data': {'bins': [4, 5, 6, 7, 8, 9],
                                      'weights': [1, 0, 0, 0, 0, 1]}}}
    target_numAX =  {'num_trees': {'data': {'bins': [1], 'weights': [2]}}}

    numBAS = extract_input.from_neurom.number_neurites(POPUL)
    numAX = extract_input.from_neurom.number_neurites(POPUL, neurite_type=neurom.AXON)
    assert_equal(numBAS, target_numBAS)
    assert_equal(numAX, target_numAX)


def test_trunk_distr(POPUL):
    bins_BAS = [0.19391773616376634,
                0.4880704446023673,
                0.7822231530409682,
                1.076375861479569,
                1.3705285699181702,
                1.6646812783567713,
                1.9588339867953721,
                2.2529866952339734,
                2.547139403672574,
                2.841292112111175]

    absolute_elevation_deviation_BAS = {
        "data": {
            "weights": [2, 0, 0, 3, 1, 2, 1, 1, 1, 2],
        }
    }
    bins_absolute_ele_dev_BAS = [-0.7718245274301169,
                                 -0.6464835753472811,
                                 -0.5211426232644452,
                                 -0.39580167118160936,
                                 -0.27046071909877345,
                                 -0.1451197670159376,
                                 -0.019778814933101796,
                                 0.10556213714973406,
                                 0.23090308923256997,
                                 0.35624404131540577]
    bins_absolute_ele_dev_APIC = [1.03738723]

    target_trunkBAS = {'trunk':
                      {'azimuth': {'uniform': {'max': 0.0, 'min': np.pi}},
                                   'orientation_deviation': {'data': {'weights': [4, 3, 1, 2, 0, 1, 0, 0, 0, 2]}},
                                   'absolute_elevation_deviation': absolute_elevation_deviation_BAS}}
    target_trunkAPIC = {'trunk': {'azimuth': {'uniform': {'max': 0.0, 'min': np.pi}},
                                  'orientation_deviation': {'data': {'bins': [0.0], 'weights': [2]}},
                                  'absolute_elevation_deviation': {'data': {'weights': [2]}}}}

    trunkAP = extract_input.from_neurom.trunk_neurite(POPUL, neurite_type=neurom.APICAL_DENDRITE, bins=1)
    trunkBAS = extract_input.from_neurom.trunk_neurite(POPUL, bins=10)

    assert_array_almost_equal(trunkBAS['trunk']['orientation_deviation']['data']['bins'],
                              bins_BAS)
    assert_array_almost_equal(trunkBAS['trunk']['absolute_elevation_deviation']['data']['bins'],
                              bins_absolute_ele_dev_BAS)
    assert_array_almost_equal(trunkAP['trunk']['absolute_elevation_deviation']['data']['bins'],
                              bins_absolute_ele_dev_APIC)
    del trunkBAS['trunk']['orientation_deviation']['data']['bins']
    del trunkBAS['trunk']['absolute_elevation_deviation']['data']['bins']
    del trunkAP['trunk']['absolute_elevation_deviation']['data']['bins']

    assert_equal(trunkBAS, target_trunkBAS)
    assert_equal(trunkAP, target_trunkAPIC)


def test_diameter_extract(POPUL, NEU):
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

    with pytest.raises(NeuroTSError):
        extract_input.from_diameter.model(load_morphologies(os.path.join(_PATH, 'simple.swc')))

    # Test on Population
    res = extract_input.from_diameter.model(POPUL)
    assert_equal(set(res.keys()), {'axon', 'basal', 'apical'})
    expected = {
        'basal': {
            'Rall_ratio': 1.5,
            'siblings_ratio': 1.0,
            'taper': [
                0.003361, 0.009487, 0.009931, 0.016477,
                0.023878, 0.024852, 0.027809, 0.027975
            ],
            'term': [0.3] * 8,
            'trunk': [0.6 , 0.6 , 0.72, 0.84, 1.2 , 1.5 , 1.8 , 2.4],
            'trunk_taper': [
                0, 3.036411e-02, 3.053287e-02, 5.059035e-02,
                1.168936e-01, 1.172027e-01, 0.15, 2.121002e-01
            ]
        },
        'apical': {
            'Rall_ratio': 1.5,
            'siblings_ratio': 1.0,
            'taper': [
                0.010331, 0.02135 , 0.02264 , 0.033914,
                0.035313, 0.041116, 0.055751, 0.056211
            ],
            'term': [0.3] * 8,
            'trunk': [1.57, 7.51],
            'trunk_taper': [0.05324615, 0.65223652]
        },
        'axon': {
            'Rall_ratio': 1.5,
            'siblings_ratio': 1.0,
            'taper': [
                0.04079 , 0.055286, 0.092382, 0.099524,
                0.11986 , 0.140346, 0.214172, 0.407058
            ],
            'term': [0.12] * 8,
            'trunk': [2.1, 3.0],
            'trunk_taper': [0.0435508, 0.0717109]
        }
    }

    for neurite_type in ['basal', 'apical', 'axon']:
        for key in expected[neurite_type].keys():
            try:
                assert_equal(res[neurite_type].keys(), expected[neurite_type].keys())
                if key in ['taper', 'term', 'trunk', 'trunk_taper']:
                    tested = sorted(res[neurite_type][key])[:8]
                else:
                    tested = res[neurite_type][key]
                assert_array_almost_equal(tested, expected[neurite_type][key])
            except AssertionError:
                raise AssertionError(f"Failed for res[{neurite_type}][{key}]")


class TestDistributions:
    @pytest.fixture
    def filename(self):
        return os.path.join(_PATH, 'bio/')

    def test_radial_distances(self, filename):
        distr = extract_input.distributions(filename, feature='radial_distances')
        assert_equal(set(distr.keys()), {'soma', 'basal', 'apical', 'axon', 'diameter'})
        assert_equal(distr['basal']['num_trees'],
                     {'data': {'bins': [4, 5, 6, 7, 8, 9], 'weights': [1, 0, 0, 0, 0, 1]}})
        assert_equal(distr['basal']['filtration_metric'], 'radial_distances')

    def test_path_distances(self, filename):
        distr = extract_input.distributions(filename, feature='path_distances')
        assert_equal(distr['basal']['filtration_metric'], 'path_distances')

    def test_diameter_model_none(self, filename):
        distr = extract_input.distributions(
            filename,
            feature='radial_distances',
            diameter_model=None,
        )
        assert_equal(set(distr.keys()), {'soma', 'basal', 'apical', 'axon', 'diameter'})

    def test_diameter_model_M5(self, filename):
        distr_M5 = extract_input.distributions(
            filename, feature='radial_distances', diameter_model='M5'
        )
        assert_equal(set(distr_M5.keys()), {'soma', 'basal', 'apical', 'axon', 'diameter'})

    def test_external_diameter_model(self, filename):

        def diam_method(pop):
            return extract_input.from_diameter.model(pop)

        distr_external = extract_input.distributions(
            filename, feature='radial_distances', diameter_model=diam_method
        )
        assert_equal(set(distr_external.keys()), {'soma', 'basal', 'apical', 'axon', 'diameter'})


def test_transform_distr():
    ss = stats.fit([1, 2], distribution='norm')
    tss = extract_input.from_neurom.transform_distr(ss)
    assert_equal(tss, {'norm': {'mean': 1.5, 'std': 0.5}})

    ss = stats.fit([1, 2], distribution='uniform')
    tss = extract_input.from_neurom.transform_distr(ss)
    assert_equal(tss, {'uniform': {'min': 1, 'max': 2}})

    ss = stats.fit([1, 2], distribution='expon')
    tss = extract_input.from_neurom.transform_distr(ss)
    assert_equal(tss, {'expon': {'loc': 1.0, 'lambda': 2.0}})

    ss = stats.fit([1, 2], distribution='gamma')
    tss = extract_input.from_neurom.transform_distr(ss)
    assert_equal(tss, None)


def test_number_neurites(POPUL):
    res = extract_input.from_neurom.number_neurites(POPUL)
    assert_equal(
        res,
        {'num_trees': {'data': {'bins': [4, 5, 6, 7, 8, 9], 'weights': [1, 0, 0, 0, 0, 1]}}}
    )

def test_number_neurites_cut_pop(POPUL):
    neurons = [neuron for neuron in POPUL]
    if len(neurons[0].neurites) > len(neurons[1].neurites):
        smallest = 1
        biggest = 0
    else:
        smallest = 0
        biggest = 1

    for i in list(range(2, len(neurons[biggest].root_sections) - 1))[::-1]:
        neurons[biggest].delete_section(
            neurons[biggest].root_sections[i], recursive=True
        )

    POPUL = neurom.core.population.Population(neurons)
    assert_equal(len(neurons), 2)
    assert_equal(len(neurons[biggest].neurites), 3)
    assert_equal(len(neurons[smallest].neurites), 6)
    assert_equal(len([i for i in POPUL.neurites]), 9)
    res_cut = extract_input.from_neurom.number_neurites(POPUL)
    assert_equal(
        res_cut,
        {'num_trees': {'data': {'bins': [2, 3, 4],
                                'weights': [1, 0, 1]}}}
    )


def test_parameters():
    params = extract_input.parameters(
        neurite_types=['basal', 'apical'], method='tmd', feature='radial_distances')

    assert_equal(params,
    {'basal': {'randomness': 0.15, 'targeting': 0.12, 'radius': 0.3, 'orientation': None,
              'growth_method': 'tmd', 'branching_method': 'bio_oriented', 'modify': None,
              "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
              'tree_type': 3, 'metric': 'radial_distances'},
     'apical': {'randomness': 0.15, 'targeting': 0.12, 'radius': 0.3, 'orientation': [(0.0, 1.0, 0.0)],
                'growth_method': 'tmd_apical', 'branching_method': 'directional', 'modify': None,
                "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                'tree_type': 4, 'metric': 'radial_distances'},
     'axon': {}, 'origin': (0.0, 0.0, 0.0), 'grow_types': ['basal', 'apical'], 'diameter_params': {'method': 'default'}})

    params_path = extract_input.parameters(
        neurite_types=['basal', 'apical'], method='tmd')

    assert_equal(params_path,
    {'basal': {'randomness': 0.15, 'targeting': 0.12, 'radius': 0.3, 'orientation': None,
              'growth_method': 'tmd', 'branching_method': 'bio_oriented', 'modify': None,
              "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
              'tree_type': 3, 'metric': 'path_distances'},
     'apical': {'randomness': 0.15, 'targeting': 0.12, 'radius': 0.3, 'orientation': [(0.0, 1.0, 0.0)],
                'growth_method': 'tmd_apical', 'branching_method': 'directional', 'modify': None,
                "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                'tree_type': 4, 'metric': 'path_distances'},
     'axon': {}, 'origin': (0.0, 0.0, 0.0), 'grow_types': ['basal', 'apical'], 'diameter_params': {'method': 'default'}})

    params_axon = extract_input.parameters(neurite_types=['axon'], method='tmd')

    assert_equal(params_axon,
        {'basal': {},
         'apical': {},
         'axon': {'randomness': 0.15, 'targeting': 0.12, 'radius': 0.3, 'orientation': [(0.0, -1.0, 0.0)],
                  'growth_method': 'tmd', 'branching_method': 'bio_oriented', 'modify': None,
                  "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                  'tree_type': 2, 'metric': 'path_distances'},
         'origin': (0.0, 0.0, 0.0),
         'grow_types': ['axon'], 'diameter_params': {'method': 'default'}
        })

    params_axon = extract_input.parameters(neurite_types=['axon'], method='trunk')

    assert_equal(params_axon,
        {'basal': {},
         'apical': {},
         'axon': {'randomness': 0.15, 'targeting': 0.12, 'radius': 0.3, 'orientation': [(0.0, -1.0, 0.0)],
                  'growth_method': 'trunk', 'branching_method': 'random', 'modify': None,
                  "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                  'tree_type': 2, 'metric': 'path_distances'},
         'origin': (0.0, 0.0, 0.0),
         'grow_types': ['axon'], 'diameter_params': {'method': 'default'}
        })

    params_diameter = extract_input.parameters(
        neurite_types=['axon'], method='trunk', diameter_parameters='M1'
    )

    assert_equal(params_diameter,
        {'basal': {},
         'apical': {},
         'axon': {'randomness': 0.15, 'targeting': 0.12, 'radius': 0.3, 'orientation': [(0.0, -1.0, 0.0)],
                  'growth_method': 'trunk', 'branching_method': 'random', 'modify': None,
                  "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                  'tree_type': 2, 'metric': 'path_distances'},
         'origin': (0.0, 0.0, 0.0),
         'grow_types': ['axon'], 'diameter_params': {'method': 'M1'}
        })

    params_diameter_dict = extract_input.parameters(
        neurite_types=['axon'],
        method='trunk',
        diameter_parameters={'a': 1, 'b': 2},
    )

    assert_equal(params_diameter_dict,
        {'basal': {},
         'apical': {},
         'axon': {'randomness': 0.15, 'targeting': 0.12, 'radius': 0.3, 'orientation': [(0.0, -1.0, 0.0)],
                  'growth_method': 'trunk', 'branching_method': 'random', 'modify': None,
                  "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                  'tree_type': 2, 'metric': 'path_distances'},
         'origin': (0.0, 0.0, 0.0),
         'grow_types': ['axon'], 'diameter_params': {'method': 'external', 'a': 1, 'b': 2}
        })

    with pytest.raises(KeyError):
        extract_input.parameters(
            neurite_types=['axon'],
            method='UNKNOWN METHOD',
        )
    with pytest.raises(ValueError):
        extract_input.parameters(
            neurite_types=['axon'],
            method='trunk',
            diameter_parameters=object(),
        )
