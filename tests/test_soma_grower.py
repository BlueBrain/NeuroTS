"""Test neurots.generate.soma code."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
import json
import os

import morphio
import numpy as np
import pytest
from mock import patch
from numpy.testing import assert_allclose
from numpy.testing import assert_almost_equal
from numpy.testing import assert_array_almost_equal
from numpy.testing import assert_array_equal
from numpy.testing import assert_equal

from neurots import NeuronGrower
from neurots.generate import soma as tested
from neurots.utils import NeuroTSError

_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def test_constructors():
    inputs = [
        [np.array([1.0, 2.0, 3.0]), 2.0],
        [np.array([1, 2, 3]), 2],
        [[1.0, 2.0, 3.0], 2.0],
        [[1, 2, 3], 2.0],
        [(1.0, 2.0, 3.0), 2],
        [(1, 2, 3), 2.0],
    ]

    for center, radius in inputs:
        soma = tested.Soma(center, radius)

        assert_equal(len(soma.points), 0)

        assert_equal(type(soma.radius), float)
        assert_almost_equal(soma.radius, 2.0)

        assert_allclose(soma.center, [1.0, 2.0, 3.0])
        assert_equal(type(soma.center), np.ndarray)

    soma = tested.Soma((1.0, 2.0, 3.0), 2.0, points=None)
    assert len(soma.points) == 0

    soma = tested.Soma((1.0, 2.0, 3.0), 2.0, points=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert_allclose(soma.points, [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])

    soma = tested.Soma((1.0, 2.0, 3.0), 2.0)
    rng = np.random.default_rng()
    context = "some_context"
    soma_grower = tested.SomaGrower(soma=soma, context=context, rng=rng)

    assert soma_grower.soma is soma
    assert soma_grower.context == "some_context"
    assert soma_grower._rng is rng


def test_soma_point_from_trunk_direction():
    soma = tested.Soma((1.0, 2.0, 3.0), 2.0)

    phi = 4.5
    theta = 1.2

    point = soma.point_from_trunk_direction(phi, theta)

    expected = np.array([-0.3929398485, -1.822192555, 0.724715509]) + soma.center

    assert_array_almost_equal(point, expected)


def test_soma_orientation_from_point():
    soma = tested.Soma((1.0, 2.0, 3.0), 2.0)

    point = np.array([0.32764176, 0.53033757, 0.74690682])

    vector = point - soma.center

    expected_orientation = vector / np.linalg.norm(vector)

    result = soma.orientation_from_point(point)
    assert_array_almost_equal(expected_orientation, result)


def test_soma_orientation_from_point_exception():
    soma = tested.Soma((1.0, 2.0, 3.0), 2.0)

    point = np.array([1.0, 2.0, 3.0])

    with pytest.raises(ValueError):
        soma.orientation_from_point(point)


def test_soma_contour_point():
    soma = tested.Soma((1.0, 2.0, 3.0), 2.0)

    point = [4.0, 5.0, 6.0]

    expected = [4.0, 5.0, 3.0]

    result = soma.contour_point(point)

    assert_array_almost_equal(expected, result)


def test_soma_grower_one_point_soma():
    soma = tested.Soma((1.0, 2.0, 3.0), 2.0)
    soma_grower = tested.SomaGrower(soma)

    soma_points, soma_diameters = soma_grower._one_point_soma()

    assert_array_equal(soma_points, [soma.center])
    assert_array_equal(soma_diameters, [4.0])


def test_soma_grower_contour_soma():
    soma = tested.Soma((1.0, 2.0, 3.0), 2.0)
    soma_grower = tested.SomaGrower(soma)

    soma.points = [(3.0, 4.0, 1000000.0)]

    expected_pts = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 3.0]])

    # bypass interpolate
    def bypassing_interpolate(points, interpolation=10):
        # pylint: disable=unused-argument
        return expected_pts

    soma_grower.interpolate = bypassing_interpolate

    soma_pts, diameters = soma_grower._contour_soma()

    assert_array_almost_equal(soma_pts, expected_pts)
    assert_allclose(diameters, 0.0)


def test_soma_grower_original_soma():
    soma = tested.Soma((1.0, 2.0, 3.0), 2.0)
    soma_grower = tested.SomaGrower(soma)

    points, diameters = soma_grower._original_soma()

    assert_equal(len(points), 0)
    assert_equal(len(diameters), 0)


def test_soma_grower_interpolate():
    soma = tested.Soma((0.0, 0.0, 0.0), 6.0)
    soma_grower = tested.SomaGrower(soma)

    soma.center = np.asarray([0.0, 0.0, 0.0], dtype=float)
    soma.points = [[0, 0, 0], [1, 0, 0], [0, 1, 1], [1, 0, 0]]

    np.random.seed(0)

    result = soma_grower.interpolate(soma.points, interpolation=4)
    assert_array_equal(
        result,
        [[0, 0, 0], [1, 0, 0], [0, 1, 1]],
    )

    result = soma_grower.interpolate(soma.points, interpolation=7)

    expected = [
        [-1.8115102245941463, -5.720002684106964, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 1.0],
        [-5.857053738900479, -1.3018915083953513, 0.0],
        [-3.6104565197299623, -4.792139785016648, 0.0],
    ]

    assert_array_almost_equal(result, expected)


def test_soma_grower_interpolate_from_neuron():
    np.random.seed(0)

    g = NeuronGrower(
        {
            "origin": [0, 0, 0],
            "grow_types": [],
            "diameter_params": {"method": "default"},
        },
        {
            "soma": {"size": {"norm": {"mean": 6, "std": 0}}},
            "diameter": {"method": "default"},
        },
    )

    g.soma_grower.soma.points = [[0, 0, 0], [1, 0, 0], [0, 1, 1], [1, 0, 0]]

    assert_array_equal(
        g.soma_grower.interpolate(g.soma_grower.soma.points, interpolation=4),
        [[0, 0, 0], [1, 0, 0], [0, 1, 1]],
    )

    result = g.soma_grower.interpolate(g.soma_grower.soma.points, interpolation=7)

    expected = [
        [-1.8115102245941463, -5.720002684106964, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 1.0],
        [-5.857053738900479, -1.3018915083953513, 0.0],
        [-3.6104565197299623, -4.792139785016648, 0.0],
    ]

    assert_array_almost_equal(result, expected)


def test_soma_interpolate_from_neuron_2():
    np.random.seed(0)
    g = NeuronGrower(
        {
            "origin": [0, 0, 0],
            "grow_types": [],
            "diameter_params": {"method": "default"},
        },
        {
            "soma": {"size": {"norm": {"mean": 6, "std": 3}}},
            "diameter": {"method": "default"},
        },
    )

    soma = g.soma_grower.soma
    soma.points = [[0, 0, 0], [1, 0, 0], [0, 1, 1], [1, 0, 0]]

    assert_array_equal(
        g.soma_grower.interpolate(soma.points, interpolation=4),
        [[0, 0, 0], [1, 0, 0], [0, 1, 1]],
    )

    assert_array_almost_equal(
        g.soma_grower.interpolate(soma.points, interpolation=7),
        [
            [0.0, 1.0, 1.0],
            [-6.794973666551906, -9.018932499998446, 0.0],
            [-3.1424513796161775, -10.846096528033044, 0.0],
            [5.211388179030298, -10.017696532443242, 0.0],
            [1.0, 0.0, 0.0],
        ],
    )


def test_soma_interpolate_exception():
    soma = tested.Soma((0.0, 0.0, 0.0), 6.0)
    soma_grower = tested.SomaGrower(soma)

    soma.center = np.asarray([0.0, 0.0, 0.0], dtype=float)

    soma.points = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]

    with pytest.raises(NeuroTSError):
        soma_grower.interpolate(soma.points, interpolation=1)


def test_add_points_from_trunk_angles():
    soma = tested.Soma((1.0, 2.0, 3.0), 2.0)
    soma_grower = tested.SomaGrower(soma)

    trunk_angle_deviations = [0.1, 0.1, 0.1]

    z_angles = [1.0, 1.0, 1.0]

    points = soma_grower.add_points_from_trunk_angles(trunk_angle_deviations, z_angles)

    expected = np.array(
        [
            [0.017229, 3.366182, 4.080605],
            [0.308237, 0.465804, 4.080605],
            [2.674534, 2.168014, 4.080605],
        ]
    )

    assert_array_almost_equal(points, expected)
    assert_array_almost_equal(soma.points, expected)

    # Test with interval [1, 4]
    interval = [1, 4]
    points = soma_grower.add_points_from_trunk_angles(trunk_angle_deviations, z_angles, interval)

    expected = np.array(
        [
            [0.1503733, 3.45273127, 4.08060461],
            [-0.68148648, 2.06997784, 4.08060461],
            [0.03260466, 0.62288711, 4.08060461],
        ]
    )


def test_add_points_from_trunk_absolute_orientation():
    soma = tested.Soma((1.0, 2.0, 3.0), 2.0)

    # Test with trivial orientation
    soma_grower = tested.SomaGrower(soma)

    orientation = np.array([0, 1, 0])
    trunk_absolute_angles = np.array([0.75, 1.0, 0.75])
    z_angles = np.array([1.48090896530732, 1.7240863537476048, 1.2747004358482887])

    points = soma_grower.add_points_from_trunk_absolute_orientation(
        orientation, trunk_absolute_angles, z_angles
    )

    expected = np.array(
        [
            [2.457469863016131, 3.3577737648609998, 3.179532731987588],
            [2.399695853613939, 3.3039517022251426, 3.5835764522666245],
            [2.067933519838869, 3.6632079132149533, 2.694619197355619],
        ]
    )

    assert_array_almost_equal(points, expected)
    assert_array_almost_equal(soma.points, expected)

    soma = tested.Soma((1.0, 2.0, 3.0), 2.0)

    # Test with non trivial orientation
    soma_grower = tested.SomaGrower(soma)

    base_orientation = [0.25, 0.5, 0.75]
    orientation = np.array(base_orientation) / np.linalg.norm(base_orientation)
    trunk_absolute_angles = [0.75, 1.0, 1.0]
    z_angles = [1.806078056398836, 0.947826003221246, 1.512974272395405]

    points = soma_grower.add_points_from_trunk_absolute_orientation(
        orientation, trunk_absolute_angles, z_angles
    )

    expected = np.array(
        [
            [2.473567419532686, 2.4338840563147373, 4.280759027205216],
            [1.0301730699570344, 2.0179373519813315, 4.999691935587396],
            [1.9460185698129842, 2.5623911684086043, 4.6699595921054495],
        ]
    )

    assert_array_almost_equal(points, expected)
    assert_array_almost_equal(soma.points, expected)


def test_add_points_from_orientations():
    soma = tested.Soma((1.0, 2.0, 3.0), 2.0)
    soma_grower = tested.SomaGrower(soma)

    vectors = np.array(
        [
            [0.87112168, 0.45651245, 0.42912960],
            [0.43898550, 0.16391644, 0.03717331],
            [0.42663795, 0.79006525, 0.85176434],
            [0.36492627, 0.54107164, 0.83189980],
        ]
    )

    vectors /= np.linalg.norm(vectors, axis=1)[:, np.newaxis]

    points = soma_grower.add_points_from_orientations(vectors)

    expected = [soma.center + soma.radius * (v / np.linalg.norm(v)) for v in vectors]

    assert_array_almost_equal(points, expected)
    assert_array_almost_equal(soma.points, expected)


def test_build():
    soma_grower = tested.SomaGrower(tested.Soma((1.0, 2.0, 3.0), 2.0))

    soma_grower._contour_soma = lambda: "contour_function"
    soma_grower._one_point_soma = lambda: "one_point_soma_function"
    soma_grower._original_soma = lambda: "original_soma_function"

    assert_equal(soma_grower.build(method="contour"), "contour_function")
    assert_equal(soma_grower.build(method="one_point"), "one_point_soma_function")
    assert_equal(soma_grower.build(method="original"), "original_soma_function")


def test_grow_soma_types():
    np.random.seed(0)
    g = NeuronGrower(
        {
            "origin": [0, 0, 0],
            "grow_types": [],
            "diameter_params": {"method": "default"},
        },
        {
            "soma": {"size": {"norm": {"mean": 6, "std": 3}}},
            "diameter": {"method": "default"},
        },
    )

    with patch.object(g, "_grow_trunks"):
        # test one soma point
        g._grow_soma(soma_type="one_point")
        assert_array_equal(g.neuron.soma.points, [[0.0, 0.0, 0.0]])
        assert_array_almost_equal(g.neuron.soma.diameters, [22.584314])

        # normal case
        g.soma_grower.soma.points = [[0, 0, 0], [1, 0, 0], [0, 1, 1], [1, 0, 0]]
        g._grow_soma(soma_type="original")
        assert_array_equal(
            g.neuron.soma.points,
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
        )
        assert_array_equal(g.neuron.soma.diameters, [0, 0, 0, 0])
        g._grow_soma(soma_type="contour")
        assert_array_almost_equal(
            g.neuron.soma.points,
            [
                [-7.10052, 8.7804, 0.0],
                [-8.961295, -6.870808, 0.0],
                [-6.794974, -9.018932, 0.0],
                [-3.1424513, -10.846097, 0.0],
                [4.315604, -10.434959, 0.0],
                [5.211388, -10.017696, 0.0],
                [1.0, 0.0, 0.0],
            ],
        )


def test_soma_grower():
    # pylint: disable=no-member
    # pylint: disable=unsubscriptable-object
    np.random.seed(0)
    with open(os.path.join(_path, "dummy_distribution.json"), encoding="utf-8") as f:
        distributions = json.load(f)

    with open(os.path.join(_path, "dummy_params.json"), encoding="utf-8") as f:
        params = json.load(f)

    grower = NeuronGrower(input_distributions=distributions, input_parameters=params).grow()

    expected = morphio.Morphology(os.path.join(_path, "dummy_neuron.asc"))

    assert_array_almost_equal(grower.soma.points, expected.soma.points)
    assert_array_almost_equal(grower.root_sections[0].points, expected.root_sections[0].points)
    for sec_actual, sec_expected in zip(grower.iter(), expected.iter()):
        assert_array_almost_equal(sec_actual.points, sec_expected.points)


def test_apical_points():
    # Found apical point
    np.random.seed(0)
    with open(os.path.join(_path, "bio_distribution.json"), encoding="utf-8") as f:
        distributions = json.load(f)

    with open(os.path.join(_path, "bio_path_params.json"), encoding="utf-8") as f:
        params = json.load(f)

    grower = NeuronGrower(input_distributions=distributions, input_parameters=params)
    grower.grow()

    apicals = grower.apical_sections
    expected = [127]
    assert_array_equal(apicals[0], expected)

    # Found apical point
    np.random.seed(0)
    with open(os.path.join(_path, "bio_path_distribution.json"), encoding="utf-8") as f:
        distributions = json.load(f)

    with open(os.path.join(_path, "bio_path_params.json"), encoding="utf-8") as f:
        params = json.load(f)

    grower = NeuronGrower(input_distributions=distributions, input_parameters=params)
    grower.grow()

    apicals = grower.apical_sections
    expected = [47]
    assert_array_equal(apicals, expected)

    # Apical point not found so keep the last bifurcation
    np.random.seed(0)
    with open(os.path.join(_path, "bio_distribution_apical_point.json"), encoding="utf-8") as f:
        distributions = json.load(f)

    with open(os.path.join(_path, "bio_path_params.json"), encoding="utf-8") as f:
        params = json.load(f)

    grower = NeuronGrower(input_distributions=distributions, input_parameters=params)
    grower.grow()

    apicals = grower.apical_sections
    expected = [23]
    assert_array_equal(apicals, expected)


def test_null_orientation():
    np.random.seed(1)
    with open(os.path.join(_path, "dummy_params.json"), encoding="utf-8") as f:
        params = json.load(f)
    params["apical_dendrite"]["orientation"] = [[0, 0, 0], [1, 0, 0]]
    with open(os.path.join(_path, "dummy_distribution.json"), encoding="utf-8") as f:
        distributions = json.load(f)
    N = NeuronGrower(input_distributions=distributions, input_parameters=params)
    with pytest.raises(AssertionError):
        N.grow()
