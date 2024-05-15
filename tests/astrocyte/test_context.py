"""Test neurots.astrocyte.context code."""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
import numpy as np
from numpy import testing as npt

from neurots.astrocyte import context as tested


def _input_params():
    return {
        "endfeet_targets": np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]),
        "space_colonization": {
            "point_cloud": np.array([[2.0, 0.0, 0.0], [2.0, 1.0, 1.0]]),
            "kill_distance_factor": 15.0,
            "influence_distance_factor": 2.0,
        },
        "field": {"type": "logit", "slope": 1.5, "intercept": 0.1},
        "collision_handle": "collision_handle",
    }


def test_constructor():
    c = tested.SpaceColonizationContext(_input_params())

    npt.assert_equal(len(c.endfeet_targets.points), 2)
    npt.assert_equal(len(c.point_cloud.points), 2)

    assert c.collision_handle == "collision_handle"

    npt.assert_equal(c._params["kill_distance_factor"], 15.0)
    npt.assert_equal(c._params["influence_distance_factor"], 2.0)

    npt.assert_equal(len(c.morphology_points), 0)


def test_methods():
    c = tested.SpaceColonizationContext(_input_params())

    npt.assert_allclose(c.kill_distance(0.1), 15.0 * 0.1)
    npt.assert_allclose(c.influence_distance(0.1), 2.0 * 0.1)
