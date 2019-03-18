import os
import json
import morphio
import numpy as np
from numpy.testing import assert_equal
from numpy.testing import assert_raises
from numpy.testing import assert_allclose
from numpy.testing import assert_array_equal
from numpy.testing import assert_almost_equal

from tns.utils import TNSError
from tns import NeuronGrower
from tns.generate.soma import SomaGrower
from tns import NeuronGrower
from numpy.testing import assert_array_equal, assert_array_almost_equal
from mock import patch


_path = os.path.dirname(os.path.abspath(__file__))


def test_constructor():

    inputs = [[np.array([1., 2., 3.]), 2.0],
              [np.array([1, 2, 3]), 2],
              [[1., 2., 3.], 2.0],
              [[1, 2, 3], 2.0],
              [(1., 2., 3.), 2],
              [(1, 2, 3), 2.0]]

    for center, radius in inputs:

        soma = SomaGrower(center, radius)

        assert_equal(len(soma.points), 0)
        assert soma.context is None

        assert_equal(type(soma.radius), float)
        assert_almost_equal(soma.radius, 2.0)

        assert_allclose(soma.center, [1., 2., 3.])
        assert_equal(type(soma.center), np.ndarray)


def test_point_from_trunk_direction():

    soma = SomaGrower((1., 2., 3.), 2.0)

    phi = 4.5
    theta = 1.2

    point = soma.point_from_trunk_direction(phi, theta)

    expected = np.array([-0.3929398485, -1.822192555, 0.724715509]) + soma.center

    assert_array_almost_equal(point, expected)


def test_orientation_from_point():

    soma = SomaGrower((1., 2., 3.), 2.0)

    point = np.array([0.32764176, 0.53033757, 0.74690682])

    vector = point - soma.center

    expected_orientation = vector / np.linalg.norm(vector)

    result = soma.orientation_from_point(point)
    assert_array_almost_equal(expected_orientation, result)


def test_orientation_from_point_exception():

    soma = SomaGrower((1., 2., 3.), 2.0)

    point = np.array([1., 2., 3.])

    with assert_raises(ValueError):
        _ = soma.orientation_from_point(point)


def test_contour_point():
    
    soma = SomaGrower((1., 2., 3.), 2.0)

    point = [4., 5., 6.]

    expected = [4., 5. , 3.]

    result = soma.contour_point(point)

    assert_array_almost_equal(expected, result)


def test_add_points_from_trunk_angles():
    
    soma = SomaGrower((1., 2., 3.), 2.0)

    trunk_angle_deviations = [0.1, 0.1, 0.1]

    z_angles = [1., 1., 1.]

    points = soma.add_points_from_trunk_angles(trunk_angle_deviations, z_angles)

    expected = np.array([[0.017229, 3.366182, 4.080605],
                      [0.308237, 0.465804, 4.080605],
                      [2.674534, 2.168014, 4.080605]])

    assert_array_almost_equal(points, expected)


def test_add_points_from_orientations():

    soma = SomaGrower((1., 2., 3.), 2.0)

    vectors = np.array([[0.87112168, 0.45651245, 0.42912960],
                        [0.43898550, 0.16391644, 0.03717331],
                        [0.42663795, 0.79006525, 0.85176434],
                        [0.36492627, 0.54107164, 0.83189980]])

    points = soma.add_points_from_orientations(vectors)

    expected = [soma.center + soma.radius * (v / np.linalg.norm(v)) for v in vectors]

    for p, e in zip(points, expected):
        assert_array_almost_equal(p, e)


def test_build():

    soma = SomaGrower((1., 2., 3.), 2.0)

    soma.contour_soma = lambda: 'contour_function'
    soma.one_point_soma = lambda: 'one_point_soma_function'
    soma.original_soma = lambda: 'original_soma_function'

    assert_equal(soma.build(method='contour'), 'contour_function')
    assert_equal(soma.build(method='one_point'), 'one_point_soma_function')
    assert_equal(soma.build(method='original'), 'original_soma_function')


def test_one_point_soma():
    
    soma = SomaGrower((1., 2., 3.), 2.0)

    soma_points, soma_diameters = soma.one_point_soma()

    assert_array_equal(soma_points, [soma.center])
    assert_array_equal(soma_diameters, [4.0])


def test_contour_soma():

    soma = SomaGrower((1., 2., 3.), 2.0)

    soma.points = [(3., 4., 1000000.)]

    expected_pts = np.array([[1., 2., 3.], [4., 5., 3.]])

    # bypass interpolate
    soma.interpolate = lambda c: expected_pts

    soma_pts, diameters = soma.contour_soma()

    assert_array_almost_equal(soma_pts, expected_pts)
    assert_allclose(diameters, 0.)


def test_interpolate():

    soma = SomaGrower((0., 0., 0.), 6.0)

    soma.center = np.asarray([0., 0., 0.], dtype=np.float)

    soma.points = [[0, 0, 0], [1, 0, 0], [0, 1, 1], [1, 0, 0]]

    np.random.seed(0)
    assert_array_equal(soma.interpolate(soma.points, interpolation=4),
                       [[0, 0, 0], [1, 0, 0], [0, 1, 1]])

    result = soma.interpolate(soma.points, interpolation=7)

    expected = [[-1.8115102245941463, -5.720002684106964, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 1.0],
                [-5.857053738900479, -1.3018915083953513, 0.0],
                [-3.6104565197299623, -4.792139785016648, 0.0]]

    assert_array_almost_equal(result, expected)


def test_interpolate_exception():

    soma = SomaGrower((0., 0., 0.), 6.0)

    soma.center = np.asarray([0., 0., 0.], dtype=np.float)

    soma.points = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]

    with assert_raises(TNSError):
        result = soma.interpolate(soma.points, interpolation=1)


def test_interpolate_from_neuron():
    np.random.seed(0)

    g = NeuronGrower({'origin': [0,0,0]},
                     {'soma': {'size': {"norm": {"mean": 6, "std": 0}}}})

    g.soma.points = [[0, 0, 0], [1, 0, 0], [0, 1, 1], [1, 0, 0]]

    assert_array_equal(g.soma.interpolate(g.soma.points, interpolation=4),
                       [[0, 0, 0], [1, 0, 0], [0, 1, 1]])

    result = g.soma.interpolate(g.soma.points, interpolation=7)

    expected = [[-1.8115102245941463, -5.720002684106964, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 1.0],
                [-5.857053738900479, -1.3018915083953513, 0.0],
                [-3.6104565197299623, -4.792139785016648, 0.0]]

    assert_array_almost_equal(result, expected)


def test_interpolate_from_neuron_2():
    np.random.seed(0)
    g = NeuronGrower({'origin': [0,0,0]},
                     {'soma': {'size': {"norm": {"mean": 6, "std": 3}}}})

    g.soma.points = [[0, 0, 0], [1, 0, 0], [0, 1, 1], [1, 0, 0]]

    assert_array_equal(g.soma.interpolate(g.soma.points, interpolation=4),
                       [[0,0,0], [1,0,0], [0,1,1]])
    assert_array_almost_equal(g.soma.interpolate(g.soma.points, interpolation=7),
                       [[0.0, 1.0, 1.0], [-6.794973666551906, -9.018932499998446, 0.0],
                        [-3.1424513796161775, -10.846096528033044, 0.0],
                        [5.211388179030298, -10.017696532443242, 0.0],
                        [1.0, 0.0, 0.0]])


def test_original_soma():

    soma = SomaGrower((1., 2., 3.), 2.0)

    points, diameters = soma.original_soma()

    assert_equal(len(points), 0)
    assert_equal(len(diameters), 0)


def test_grow_soma_types():
    np.random.seed(0)
    g = NeuronGrower({'origin': [0, 0, 0]},
                     {'soma': {'size': {"norm": {"mean": 6, "std": 3}}}})

    with patch.object(g, '_grow_trunks'):
        # test one soma point
        g._grow_soma(soma_type='one_point')
        assert_array_equal(g.neuron.soma.points, [[0.0, 0.0, 0.0]])
        assert_array_almost_equal(g.neuron.soma.diameters,  [22.584314])

        # normal case
        g.soma.points = [[0, 0, 0], [1, 0, 0], [0, 1, 1], [1, 0, 0]]
        g._grow_soma(soma_type='original')
        assert_array_equal(g.neuron.soma.points,
                           [[0., 0., 0.],
                            [1., 0., 0.],
                            [0., 1., 1.],
                            [1., 0., 0.]])
        assert_array_equal(g.neuron.soma.diameters,  [0, 0, 0, 0])
        g._grow_soma(soma_type='contour')
        assert_array_almost_equal(g.neuron.soma.points,
                           [[ -7.10052,     8.7804,      0.       ],
                            [ -8.961295,   -6.870808,    0.       ],
                            [ -6.794974,   -9.018932,    0.       ],
                            [ -3.1424513, -10.846097,    0.       ],
                            [  4.315604,  -10.434959,    0.       ],
                            [  5.211388,  -10.017696,    0.       ],
                            [  1.,          0.,          0.       ]])


def test_soma_grower():
    np.random.seed(0)
    with open(os.path.join(_path, 'dummy_distribution.json')) as f:
        distributions = json.load(f)

    with open(os.path.join(_path, 'dummy_params.json')) as f:
        params = json.load(f)
    N = NeuronGrower(input_distributions=distributions,
                     input_parameters=params).grow()

    actual = morphio.Morphology(N)
    expected = morphio.Morphology(os.path.join(_path, 'dummy_neuron.asc'))

    assert_array_almost_equal(actual.soma.points, expected.soma.points)
    assert_array_almost_equal(actual.root_sections[0].points,
                              expected.root_sections[0].points)
    for sec_actual, sec_expected in zip(actual.iter(), expected.iter()):
        assert_array_almost_equal(sec_actual.points, sec_expected.points)
