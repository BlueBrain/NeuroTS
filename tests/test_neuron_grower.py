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
    np.random.seed(0)
    g = NeuronGrower({'origin': [0,0,0]},
                     {'soma': {'size': {"norm": {"mean": 6, "std": 3}}}})

    with patch.object(g, '_grow_trunks'):
        # test one soma point
        g._grow_soma(soma_type='one_point')
        assert_array_equal(g.neuron.soma.points, [[0.0, 0.0, 0.0]])
        assert_array_almost_equal(g.neuron.soma.diameters,  [11.292157])

        # normal case
        g.soma.points3D = [[0,0,0], [1,0,0], [0,1,1], [1,0,0]]
        g._grow_soma(soma_type='original')
        assert_array_equal(g.neuron.soma.points,
                           [[0., 0., 0.],
                            [1., 0., 0.],
                            [0., 1., 1.],
                            [1., 0., 0.]])
        assert_array_equal(g.neuron.soma.diameters,  [0,0,0,0])
        g._grow_soma(soma_type='contour')
        assert_array_almost_equal(g.neuron.soma.points,
                           [[ -7.10052,     8.7804,      0.       ],
                            [ -8.961295,   -6.870808,    0.       ],
                            [ -6.794974,   -9.018932,    0.       ],
                            [ -3.1424513, -10.846097,    0.       ],
                            [  4.315604,  -10.434959,    0.       ],
                            [  5.211388,  -10.017696,    0.       ],
                            [  1.,          0.,          0.       ]])

def test_interpolate():
    np.random.seed(0)
    g = NeuronGrower({'origin': [0,0,0]},
                     {'soma': {'size': {"norm": {"mean": 6, "std": 3}}}})
    g.soma.points3D = [[0,0,0], [1,0,0], [0,1,1], [1,0,0]]
    assert_array_equal(g.soma.interpolate(g.soma.points3D, interpolation=4),
                       [[0,0,0], [1,0,0], [0,1,1]])
    assert_array_almost_equal(g.soma.interpolate(g.soma.points3D, interpolation=7),
                       [[0.0, 1.0, 1.0], [-6.794973666551906, -9.018932499998446, 0.0],
                        [-3.1424513796161775, -10.846096528033044, 0.0],
                        [5.211388179030298, -10.017696532443242, 0.0],
                        [1.0, 0.0, 0.0]])

def test_soma_grower():
    np.random.seed(0)
    with open(join(_path, 'dummy_distribution.json')) as f:
        distributions = json.load(f)

    with open(join(_path, 'dummy_params.json')) as f:
        params = json.load(f)
    N = tns.NeuronGrower(input_distributions=distributions,
                         input_parameters=params).grow()

    actual = morphio.Morphology(N)
    expected = morphio.Morphology(join(_path, 'dummy_neuron.asc'))

    assert_array_almost_equal(actual.soma.points, expected.soma.points)
    assert_array_almost_equal(actual.root_sections[0].points,
                              expected.root_sections[0].points)
    for sec_actual, sec_expected in zip(actual.iter(), expected.iter()):
        assert_array_almost_equal(sec_actual.points, sec_expected.points)
