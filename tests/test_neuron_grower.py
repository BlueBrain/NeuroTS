import json
import os
from os.path import join
from nose.tools import assert_equal
import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal

import morphio

from tns.extract_input import distributions

import tns

_path = os.path.dirname(os.path.abspath(__file__))

def test_neuron_grower():
    np.random.seed(0)
    with open(join(_path, 'dummy_distribution.json')) as f:
        distributions = json.load(f)

    with open(join(_path, 'dummy_params.json')) as f:
        params = json.load(f)
    N = tns.NeuronGrower(input_distributions=distributions,
                         input_parameters=params).grow()

    actual = morphio.Morphology(N)
    expected = morphio.Morphology(join(_path, 'test_neuron_grower.asc'))

    assert_array_almost_equal(actual.soma.points, expected.soma.points)
    assert_array_almost_equal(actual.root_sections[0].points,
                              expected.root_sections[0].points)
    for sec_actual, sec_expected in zip(actual.iter(), expected.iter()):
        assert_array_almost_equal(sec_actual.points, sec_expected.points)
