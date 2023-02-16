"""Test neurots.astrocyte.context code."""

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
