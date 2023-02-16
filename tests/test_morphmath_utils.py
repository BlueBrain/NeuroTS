"""Test neurots.morphmath.utils code."""

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
import numpy as np
from numpy import testing as npt

from neurots.morphmath import utils as tested


def test_norm():
    vector = np.array([0.24428195, 0.84795862, 0.70495863])
    npt.assert_allclose(tested.norm(vector), np.linalg.norm(vector))

    vector = np.zeros(3)
    npt.assert_allclose(tested.norm(vector), 0.0)


def test_from_to_direction():
    point = np.array([0.51374375, 0.39753749, 0.27568173])
    target = np.array([0.5932438, 0.96379423, 0.49277981])

    expected_length = 0.6116359455469541
    expected_direction = np.array([0.12997936, 0.92580684, 0.35494657])

    direction = tested.from_to_direction(point, target, return_length=False)
    npt.assert_allclose(direction, expected_direction)

    direction, length = tested.from_to_direction(point, target, return_length=True)
    npt.assert_allclose(direction, expected_direction)
    npt.assert_allclose(length, expected_length)


def test_in_same_halfspace():
    points = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]])

    ref_point = np.array([0.5, 0.5, 0.5])

    direction = -np.array([1.0, 1.0, 1.0])
    direction /= np.linalg.norm(direction)

    mask = tested.in_same_halfspace(points - ref_point, direction)
    npt.assert_array_equal(mask, [True, False, False])

    mask, dots = tested.in_same_halfspace(points - ref_point, direction, return_dots=True)
    npt.assert_array_equal(mask, [True, False, False])

    npt.assert_allclose(dots, -np.dot(ref_point, direction))


def test_in_squared_proximity():
    point1 = np.array([0.0, 0.0, 1.0])
    point2 = np.array([0.0, 0.0, 3.0])

    squared_proximity = 4.0
    assert tested.in_squared_proximity(point1, point2, squared_proximity)

    squared_proximity = 3.9
    assert not tested.in_squared_proximity(point1, point2, squared_proximity)


def test_ball_query():
    points = np.array(
        [
            [0.0, 0.0, -2.0],
            [0.0, 0.0, -1.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 2.0],
        ]
    )

    ids = tested.ball_query(points, np.array([0.0, 0.0, 0.0]), 1.0)
    npt.assert_array_equal(ids, [1, 2, 3])


def test_upper_half_ball_query():
    points = np.array([[10.0, 10.0, 10.0], [11.0, 11.0, 11.0]])
    ids = tested.upper_half_ball_query(points, np.zeros(3), 0.1, np.array([1.0, 0.0, 0.0]))
    assert ids.size == 0

    points = np.array(
        [
            [0.0, 0.0, -2.0],
            [0.0, 0.0, -1.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 2.0],
        ]
    )

    ids = tested.upper_half_ball_query(
        points, np.array([0.0, 0.0, 0.0]), 1.0, np.array([-1.0, 0.0, -1.0])
    )
    npt.assert_array_equal(ids, [1])
