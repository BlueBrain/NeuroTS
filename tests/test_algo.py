'''Test tns.generate.section code'''
import json
import os

import numpy as np
from nose.tools import assert_dict_equal
from numpy.testing import assert_array_almost_equal, assert_equal

from tns.generate.algorithms.tmdgrower import (TMDAlgo, TMDApicalAlgo,
                                               TMDGradientAlgo)
from tns.generate.algorithms.tmdgrower_path import TMDAlgoPath, TMDApicalAlgoPath, TMDGradientAlgoPath
from tns.generate.section import SectionGrower, SectionGrowerPath

_PATH = os.path.dirname(os.path.abspath(__file__))


def _setup_test(Algo, Grower):
    with open(os.path.join(_PATH, 'dummy_distribution.json')) as f:
        distributions = json.load(f)['basal']

    with open(os.path.join(_PATH, 'dummy_params.json')) as f:
        parameters = json.load(f)['basal']
    parameters['bias_length'] = 0.5
    parameters['bias'] = 0.5

    np.random.seed(42)
    algo = Algo(distributions, parameters, [0, 0, 1])

    grower = Grower(None, None, [1.1,0.,0.], [2, 2, 2], 0.2, 0.3, 'major',
                           {'bif_term': {'bif': 9.7747, 'ref': [0, 0, 1], 'term': 159.798}})
    return algo, grower


def _assert_dict_or_array(dict1, dict2):
    assert_equal(dict1.keys(), dict2.keys())
    for key in dict1.keys():
        if isinstance(dict1[key], np.ndarray):
            assert_array_almost_equal(dict1[key], dict2[key])
        elif isinstance(dict1[key], dict):
            _assert_dict_or_array(dict1[key], dict2[key])
        else:
            assert_equal(dict1[key], dict2[key], 'Error for key: %s' % key)


def test_TMDAlgo():
    algo, grower = _setup_test(TMDAlgo, SectionGrower)

    stop, num_sec = algo.initialize()
    assert_dict_equal(stop, {'bif_term': {'bif': 9.7747, 'ref': [0, 0, 1], 'term': 159.798}})
    assert_equal(num_sec, 10)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(s1,
                          {'direction': [0., 0., 0.],
                           'process': 'major',
                           'start_point': [1.1, 0. , 0. ],
                           'stop': {'bif_term': {'bif': 18.5246, 'ref': [0, 0, 1], 'term': 159.798}}})

    _assert_dict_or_array(s2,
                          {'direction': [0., 0., 0.],
                           'process': 'major',
                           'start_point': [1.1, 0. , 0. ],
                           'stop': {'bif_term': {'bif': 18.5246, 'ref': [0, 0, 1], 'term': 124.8796}}})

def test_TMDApicalAlgo():
    algo, grower = _setup_test(TMDApicalAlgo, SectionGrower)

    stop, num_sec = algo.initialize()
    expected_stop = {'bif_term': {'bif': 9.7747, 'ref': [0, 0, 1], 'term': 159.798}}
    assert_dict_equal(stop, expected_stop)
    assert_equal(num_sec, 10)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(s1,
                          {'direction': [2., 2., 2.],
                           'process': 'secondary',
                           'start_point': [1.1, 0. , 0. ],
                           'stop': {'bif_term': {'bif': 18.5246, 'ref': [0, 0, 1], 'term': 159.798}}})

    _assert_dict_or_array(s2,
                          {'direction': np.array([0.704878, 1.874423, 2.826603]),
                           'process': 'secondary',
                           'start_point': [1.1, 0. , 0. ],
                           'stop': {'bif_term': {'bif': 18.5246, 'ref': [0, 0, 1], 'term': 124.8796}}})



def test_TMDGradientAlgo():
    algo, grower = _setup_test(TMDGradientAlgo, SectionGrower)

    stop, num_sec = algo.initialize()
    expected_stop = {'bif_term': {'bif': 9.7747, 'ref': [0, 0, 1], 'term': 159.798}}
    assert_dict_equal(stop, expected_stop)
    assert_equal(num_sec, 10)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(s1,
                          {'direction': [2., 2., 2.],
                           'process': 'major',
                           'start_point': [1.1, 0. , 0. ],
                           'stop': {'bif_term': {'bif': 18.5246, 'ref': [0, 0, 1], 'term': 159.798}}})

    _assert_dict_or_array(s2,
                          {'direction': np.array([1.352439, 1.937212, 2.413301]),
                           'process': 'major',
                           'start_point': [1.1, 0. , 0. ],
                           'stop': {'bif_term': {'bif': 18.5246, 'ref': [0, 0, 1], 'term': 124.8796}}})


def test_TMDAlgoPath():
    algo, grower = _setup_test(TMDAlgoPath, SectionGrowerPath)

    stop, num_sec = algo.initialize()
    assert_dict_equal(stop, {'bif_term': {'bif': 9.7747, 'ref': 0, 'term': 159.798}})
    assert_equal(num_sec, 10)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(s1,
                          {'direction': [0., 0., 0.],
                           'process': 'major',
                           'start_point': [1.1, 0. , 0. ],
                           'stop': {'bif_term': {'bif': 18.5246, 'ref': 0, 'term': 159.798}}})

    _assert_dict_or_array(s2,
                          {'direction': [0., 0., 0.],
                           'process': 'major',
                           'start_point': [1.1, 0. , 0. ],
                           'stop': {'bif_term': {'bif': 18.5246, 'ref': 0, 'term': 124.8796}}})


def test_TMDApicalAlgoPath():
    algo, grower = _setup_test(TMDApicalAlgoPath, SectionGrowerPath)

    stop, num_sec = algo.initialize()
    expected_stop = {'bif_term': {'bif': 9.7747, 'ref': 0, 'term': 159.798}}
    assert_dict_equal(stop, expected_stop)
    assert_equal(num_sec, 10)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(s1,
                          {'direction': [2., 2., 2.],
                           'process': 'major',
                           'start_point': [1.1, 0. , 0. ],
                           'stop': {'bif_term': {'bif': 18.5246, 'ref': 0, 'term': 159.798}}})

    _assert_dict_or_array(s2,
                          {'direction': np.array([0.704878, 1.874423, 2.826603]),
                           'process': 'secondary',
                           'start_point': [1.1, 0. , 0. ],
                           'stop': {'bif_term': {'bif': 18.5246, 'ref': 0, 'term': 124.8796}}})



def test_TMDGradientAlgoPath():
    algo, grower = _setup_test(TMDGradientAlgoPath, SectionGrowerPath)

    stop, num_sec = algo.initialize()
    expected_stop = {'bif_term': {'bif': 9.7747, 'ref': 0, 'term': 159.798}}
    assert_dict_equal(stop, expected_stop)
    assert_equal(num_sec, 10)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(s1,
                          {'direction': [2., 2., 2.],
                           'process': 'major',
                           'start_point': [1.1, 0. , 0. ],
                           'stop': {'bif_term': {'bif': 18.5246, 'ref': 0, 'term': 159.798}}})

    _assert_dict_or_array(s2,
                          {'direction': np.array([1.352439, 1.937212, 2.413301]),
                           'process': 'major',
                           'start_point': [1.1, 0. , 0. ],
                           'stop': {'bif_term': {'bif': 18.5246, 'ref': 0, 'term': 124.8796}}})
