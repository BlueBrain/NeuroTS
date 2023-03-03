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


def test_orientation_manager__mode_uniform():
    parameters = {
        "grow_types": ["basal_dendrite"],
        "basal_dendrite": {
            "orientation": {
                "mode": "uniform",
                "values": {},
            }
        },
    }

    distributions = {
        "basal_dendrite": {
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

    actual = om.get_tree_type_orientations("basal_dendrite")
    expected = np.array([[-0.199474, 0.967017, 0.158396], [-0.368063, 0.248455, 0.895991]])

    npt.assert_allclose(actual, expected, rtol=1e-5)


def test_orientation_manager__mode_normal_pia_constraint():
    """Test mode normal_pia_constraint."""
    # make one near pia
    parameters = {
        "grow_types": ["apical_dendrite"],
        "apical_dendrite": {
            "orientation": {
                "mode": "normal_pia_constraint",
                "values": {"direction": {"mean": 0, "std": 0.1}},
            }
        },
    }

    distributions = {
        "apical_dendrite": {
            "num_trees": {
                "data": {"bins": [1], "weights": [1]},
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

    actual = om.get_tree_type_orientations("apical_dendrite")
    expected = np.array([[-0.0084249, 0.99768935, 0.06741643]])
    npt.assert_allclose(actual, expected, rtol=1e-5)

    # make one along pia
    parameters["apical_dendrite"]["orientation"]["values"]["direction"] = {"mean": 0.0, "std": 0.0}
    om = tested.OrientationManager(
        soma=None,
        parameters=parameters,
        distributions=distributions,
        context=None,
        rng=np.random.default_rng(seed=0),
    )

    for tree_type in parameters["grow_types"]:
        om.compute_tree_type_orientations(tree_type)

    actual = om.get_tree_type_orientations("apical_dendrite")
    expected = np.array([[0, 1.0, 0.0]])
    npt.assert_allclose(actual, expected, rtol=1e-5)

    # make one away from pia
    parameters["apical_dendrite"]["orientation"]["values"]["direction"] = {"mean": 1.0, "std": 0.1}
    om = tested.OrientationManager(
        soma=None,
        parameters=parameters,
        distributions=distributions,
        context=None,
        rng=np.random.default_rng(seed=0),
    )

    for tree_type in parameters["grow_types"]:
        om.compute_tree_type_orientations(tree_type)

    actual = om.get_tree_type_orientations("apical_dendrite")
    expected = np.array([[-0.10517952, 0.52968005, 0.84165095]])
    npt.assert_allclose(actual, expected, rtol=1e-5)


def test_orientation_manager__pia_constraint():
    parameters = {
        "grow_types": ["basal_dendrite"],
        "basal_dendrite": {
            "orientation": {
                "mode": "pia_constraint",
                "values": {"form": "step", "params": [1.5, 0.25]},
            }
        },
    }

    # params obtained from fit to an L5_TPC:A population
    distributions = {
        "basal_dendrite": {
            "num_trees": {
                "data": {"bins": [2], "weights": [1]},
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

    actual = om.get_tree_type_orientations("basal_dendrite")
    expected = np.array([[-0.896702, -0.441664, 0.029284], [-0.14969, -0.852409, -0.500992]])

    npt.assert_allclose(actual, expected, rtol=2e-5)


def test_check_3d_angles():
    parameters = {
        "grow_types": ["apical_dendrite", "basal_dendrite"],
        "apical_dendrite": {
            "orientation": {
                "mode": "pia_constraint",
                "values": {"orientations": [[0.0, 1.0, 0.0]]},
            }
        },
        "basal_dendrite": {
            "orientation": {
                "mode": "apical_constraint",
                "values": {"form": "step", "params": [1.5, 0.25]},
            }
        },
    }
    assert tested.check_3d_angles(parameters)
    parameters["apical_dendrite"]["orientation"] = None
    with pytest.raises(NeuroTSError):
        tested.check_3d_angles(parameters)

    parameters["apical_dendrite"]["orientation"] = parameters["basal_dendrite"]["orientation"]
    parameters["basal_dendrite"]["orientation"] = None
    with pytest.raises(NeuroTSError):
        tested.check_3d_angles(parameters)


def test_orientation_manager__apical_constraint():
    parameters = {
        "grow_types": ["apical_dendrite", "basal_dendrite"],
        "apical_dendrite": {
            "orientation": {
                "mode": "use_predefined",
                "values": {"orientations": [[0.0, 1.0, 0.0]]},
            }
        },
        "basal_dendrite": {
            "orientation": {
                "mode": "apical_constraint",
                "values": {"form": "step", "params": [1.5, 0.25]},
            }
        },
    }

    # params obtained from fit to an L5_TPC:A population
    distributions = {
        "apical_dendrite": {
            "num_trees": {
                "data": {"bins": [1], "weights": [1]},
            }
        },
        "basal_dendrite": {
            "num_trees": {
                "data": {"bins": [2], "weights": [1]},
            },
        },
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
    tested._sample_trunk_from_3d_angle(
        parameters, om._rng, "basal_dendrite", [0, 0, 1], max_tries=-1
    )

    actual = om.get_tree_type_orientations("basal_dendrite")
    expected = np.array([[0.761068, 0.124662, -0.636581], [0.741505, 0.538547, -0.400171]])

    npt.assert_allclose(actual, expected, rtol=2e-5)


def test_probability_function():
    func = tested.get_probability_function(form="flat")
    npt.assert_equal(func(1.0), 0.8414709848078965)

    func = tested.get_probability_function(form="step")
    npt.assert_equal(func(2.1, 0.5, 5), 0.7949219421515932)

    func = tested.get_probability_function(form="double_step")
    npt.assert_equal(func(2.1, 0.5, 5, -0.5, 1), 0.5877841415613994)

    func = tested.get_probability_function(form="flat", with_density=False)
    npt.assert_equal(func(1.0), 1.0)

    func = tested.get_probability_function(form="step", with_density=False)
    npt.assert_equal(func(2.1, 0.5, 5), 0.9208912378205718)

    func = tested.get_probability_function(form="double_step", with_density=False)
    npt.assert_equal(func(2.1, 0.5, 5, -0.5, 1), 0.6809288270854589)

    with pytest.raises(ValueError):
        tested.get_probability_function(form="UNKNOWN")


# pylint:disable=unsubscriptable-object
def test_fit_3d_angles():
    parameters = {
        "grow_types": ["apical_dendrite", "basal_dendrite"],
        "apical_dendrite": {
            "orientation": {
                "mode": "use_predefined",
                "values": {"orientations": [[0.0, 1.0, 0.0]]},
            }
        },
        "basal_dendrite": {
            "orientation": {
                "mode": "apical_constraint",
                "values": {},
            }
        },
    }

    # params obtained from fit to an L5_TPC:A population
    distributions = {
        "apical_dendrite": {
            "num_trees": {
                "data": {"bins": [1], "weights": [1]},
            }
        },
        "basal_dendrite": {
            "num_trees": {
                "data": {"bins": [2], "weights": [1]},
            },
            "trunk": {
                "apical_3d_angles": {"data": {"bins": [0, 0.5, 1], "weights": [0.2, 0.8, 0.2]}}
            },
        },
    }
    expected_params = [3.1415926535803003, 2.9065466158869935]

    new_parameters = tested.fit_3d_angles(parameters, distributions)

    assert new_parameters["basal_dendrite"]["orientation"]["values"]["form"] == "step"
    npt.assert_almost_equal(
        new_parameters["basal_dendrite"]["orientation"]["values"]["params"], expected_params
    )
    parameters["basal_dendrite"]["orientation"]["values"]["form"] = "step"
    new_parameters = tested.fit_3d_angles(parameters, distributions)
    npt.assert_almost_equal(
        new_parameters["basal_dendrite"]["orientation"]["values"]["params"], expected_params
    )

    parameters = {
        "grow_types": ["apical_dendrite", "basal_dendrite"],
        "apical_dendrite": {
            "orientation": {
                "mode": "use_predefined",
                "values": {"orientations": [[0.0, 1.0, 0.0]]},
            }
        },
        "basal_dendrite": {
            "orientation": {
                "mode": "apical_constraint",
                "values": {"form": "flat"},
            },
        },
    }

    new_parameters = tested.fit_3d_angles(parameters, distributions)
    assert new_parameters["basal_dendrite"]["orientation"]["values"]["form"] == "flat"
    assert new_parameters["basal_dendrite"]["orientation"]["values"]["params"] == []
