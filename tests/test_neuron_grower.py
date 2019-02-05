import json
import os
from os.path import join
from nose.tools import assert_equal
import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal
from mock import patch

import morphio

from tns.extract_input import distributions
from tns.generate.grower import NeuronGrower

import tns

_path = os.path.dirname(os.path.abspath(__file__))


def test_grow_soma():
    g = NeuronGrower({'origin': [0,0,0]},
                     {'soma': {'size': {"norm": {"mean": 9, "std": 3}}}})

    with patch.object(g, '_grow_trunks'):
        # 2 neurite case
        g.soma.points3D = [[0,0,0], [1,1,1]]
        g._grow_soma()
        assert_array_equal(g.neuron.soma.points, [[0.5, 0.5, 0.5]])
        assert_array_almost_equal(g.neuron.soma.diameters,  [1.732051])

        # normal case
        g.soma.points3D = [[0,0,0], [1,0,0], [0,1,1], [1,0,0]]
        g._grow_soma()
        assert_array_equal(g.neuron.soma.points,
                           [[0., 0., 0.],
                            [1., 0., 0.],
                            [0., 1., 0.],
                            [1., 0., 0.]])
        assert_array_equal(g.neuron.soma.diameters,  [0,0,0,0])


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
