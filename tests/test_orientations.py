"""Test neurots.generate.orientations code."""

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
import inspect

import numpy as np
import pytest
from numpy import testing as npt

from neurots.generate import orientations as tested
from neurots.generate.soma import Soma
from neurots.utils import NeuroTSError


def test_orientation_manager__constructor():

    soma = "soma"
    parameters = "parameters"
    distributions = "distributions"
    context = "context"
    rng = "rng"

    om = tested.OrientationManager(
        soma=soma,
        parameters=parameters,
        distributions=distributions,
        context=context,
        rng=rng,
    )

    assert om._parameters is parameters
    assert om._distributions is distributions
    assert om._context is context
    assert om._rng is rng

    assert len(om._orientations) == 0

    # check if all methods are bound
    methods = inspect.getmembers(om)
    mode_methods = [(name, method) for name, method in methods if name.startswith("_mode_")]
    expected_modes = {name.replace("_mode_", ""): method for name, method in mode_methods}

    # check that the correct names have been bound to the
    # respective method names
    for mode, method in om._modes.items():
        assert mode == method.__name__.replace(
            "_mode_", ""
        ), f"Mode name mismatch: {mode} -> {method.__name__}"

    # then check that all there are no new methods that are unregistered
    str_modes = "\n".join(om._modes)
    str_expected_modes = "\n".join(expected_modes)

    assert om._modes == expected_modes, (
        "Not all modes are bound.\n"
        f"\nActual   :\n{str_modes}\n"
        f"\nExpected :\n{str_expected_modes}\n"
    )

    assert set(om.mode_names) == set(expected_modes.keys())


def test_orientation_manager__mode_use_predefined():

    parameters = {
        "grow_types": ["john"],
        "john": {
            "orientation": {
                "mode": "use_predefined",
                "values": {"orientations": [[0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]},
            }
        },
    }

    distributions = {
        "john": {
            "num_trees": {
                "data": {"bins": [2], "weights": [1]},
            }
        }
    }

    om = tested.OrientationManager(
        soma=None,
        parameters=parameters,
        distributions=distributions,
        context=None,
        rng=np.random.default_rng(seed=0),
    )

    for tree_type in parameters["grow_types"]:
        om.compute_tree_type_orientations(tree_type)

    actual = om.get_tree_type_orientations("john")
    expected = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0]])

    npt.assert_allclose(actual, expected)


def test_orientation_manager__tree_type_method_values():

    parameters = {
        "grow_types": ["john"],
        "john": {
            "orientation": {
                "mode": "use_predefined",
                "values": {"orientations": [[0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]},
            }
        },
    }

    om = tested.OrientationManager(
        soma=None, parameters=parameters, distributions=None, context=None, rng=None
    )

    method, values = om._tree_type_method_values("john")

    assert method == om._mode_use_predefined  # pylint: disable=comparison-with-callable
    assert values == {"orientations": [[0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]}

    # check that method exists
    parameters["john"]["orientation"]["mode"] = "non_existent_method"
    with pytest.raises(NeuroTSError):
        om.compute_tree_type_orientations("john")

    # check that config keys are correct
    parameters["john"]["orientation"]["random_key"] = "lol"
    with pytest.raises(NeuroTSError):
        om.compute_tree_type_orientations("john")

    # check that config is not empty
    parameters["john"]["orientation"] = {}
    with pytest.raises(NeuroTSError):
        om.compute_tree_type_orientations("john")

    # check that orientation is not None
    parameters["john"]["orientation"] = None
    with pytest.raises(NeuroTSError):
        om.compute_tree_type_orientations("john")


def test_orientation_manager__mode_sample_around_primary_orientation():

    parameters = {
        "grow_types": ["john"],
        "john": {
            "orientation": {
                "mode": "sample_around_primary_orientation",
                "values": {"primary_orientation": [0.0, 0.0, 1.0]},
            }
        },
    }

    distributions = {
        "john": {
            "num_trees": {
                "data": {"bins": [2], "weights": [1]},
            },
            "trunk": {
                "azimuth": {"data": {"bins": [np.pi], "weights": [1]}},
                "absolute_elevation_deviation": {"data": {"bins": [np.pi * 0.5], "weights": [1]}},
            },
        }
    }

    om = tested.OrientationManager(
        soma=None,
        parameters=parameters,
        distributions=distributions,
        context=None,
        rng=np.random.default_rng(seed=0),
    )

    for tree_type in parameters["grow_types"]:
        om.compute_tree_type_orientations(tree_type)

    actual = om.get_tree_type_orientations("john")
    expected = np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])

    npt.assert_allclose(actual, expected, atol=1e-6)


def test_orientation_manager__mode_sample_pairwise_angles():

    parameters = {
        "grow_types": ["john"],
        "john": {"orientation": {"mode": "sample_pairwise_angles", "values": {}}},
    }

    distributions = {
        "john": {
            "num_trees": {
                "data": {"bins": [3], "weights": [1]},
            },
            "trunk": {
                "azimuth": {"data": {"bins": [np.pi / 2], "weights": [1]}},
                "orientation_deviation": {"data": {"bins": [0], "weights": [1]}},
            },
        }
    }

    om = tested.OrientationManager(
        soma=None,
        parameters=parameters,
        distributions=distributions,
        context=None,
        rng=np.random.default_rng(seed=0),
    )

    for tree_type in parameters["grow_types"]:
        om.compute_tree_type_orientations(tree_type)

    actual = om.get_tree_type_orientations("john")
    expected = np.array([[-0.5, np.sin(np.pi / 3), 0], [-0.5, -np.sin(np.pi / 3), 0], [1, 0, 0]])

    npt.assert_allclose(actual, expected, atol=1e-6)

    # Test with existing neurites in soma
    soma = Soma(
        (0.0, 0.0, 0.0),
        6.0,
        [
            [-6.0, 0.0, 0.0],
            [6.0, 0.0, 0.0],
            [0.0, 6.0, 0.0],
            [0.0, -6.0, 0.0],
        ],
    )

    om = tested.OrientationManager(
        soma=soma,
        parameters=parameters,
        distributions=distributions,
        context=None,
        rng=np.random.default_rng(seed=0),
    )

    for tree_type in parameters["grow_types"]:
        om.compute_tree_type_orientations(tree_type)

    actual = om.get_tree_type_orientations("john")
    expected = np.array(
        [
            [0.5, -np.sin(2 * np.pi / 6), 0],
            [np.sin(2 * np.pi / 6), -0.5, 0],
            [np.sin(np.pi / 4), np.sin(np.pi / 4), 0],
        ]
    )

    npt.assert_allclose(actual, expected, atol=1e-6)


def test_spherical_angles_to_orientations():

    phis = [0.5 * np.pi, np.pi, np.pi]

    thetas = [0.5 * np.pi, np.pi, 0.5 * np.pi]

    expected_orientations = [[0.0, 1.0, 0.0], [0.0, 0.0, -1.0], [-1.0, 0.0, 0.0]]

    npt.assert_allclose(
        tested.spherical_angles_to_orientations(phis, thetas),
        expected_orientations,
        atol=1e-6,
    )


def test_points_to_orientations():

    origin = np.array([0.0, 0.0, 0.0])
    points = np.array([[2.0, 0.0, 0.0], [0.0, 0.0, 3.0]])

    actual = tested.points_to_orientations(origin, points)
    npt.assert_allclose(actual, [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])


def test_orientations_to_sphere_points():

    sphere_center = np.array([0.0, 0.0, 1.0])
    sphere_radius = 0.2

    oris = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])

    expected_points = np.array([[0.2, 0.0, 1.0], [0.0, 0.2, 1.0], [0.0, 0.0, 1.2]])

    npt.assert_allclose(
        tested.orientations_to_sphere_points(oris, sphere_center, sphere_radius),
        expected_points,
    )
