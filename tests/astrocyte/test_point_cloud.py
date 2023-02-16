"""Test neurots.astrocyte.point_cloud code."""

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

from neurots.astrocyte.point_cloud import PointCloud


def point_array():
    return np.array(
        [
            [-10.0, -10.0, -10.0],  # 0
            [-8.0, -8.0, -8.0],  # 1
            [-6.0, -6.0, -6.0],  # 2
            [-4.0, -4.0, -4.0],  # 3
            [-2.0, -2.0, -2.0],  # 4
            [0.0, 0.0, 0.0],  # 5
            [2.0, 2.0, 2.0],  # 6
            [4.0, 4.0, 4.0],  # 7
            [6.0, 6.0, 6.0],  # 8
            [8.0, 8.0, 8.0],  # 9
            [10.0, 10.0, 10.0],  # 10
        ]
    )


def create_point_cloud():
    return PointCloud(point_array())


def test_constructor():
    point_cloud = create_point_cloud()
    npt.assert_allclose(point_cloud.points, point_array())

    n_points = len(point_cloud.points)

    npt.assert_array_equal(point_cloud.available_ids, np.arange(n_points, dtype=int))
    npt.assert_array_equal(point_cloud.removed_ids, [])
    npt.assert_array_equal(point_cloud.removed_points, np.empty((0, 3)))


def _assert_unordered_equal(arr1, arr2):
    npt.assert_array_equal(np.sort(arr1), np.sort(arr2))


def test_ball_query():
    point_cloud = create_point_cloud()

    ids = point_cloud.ball_query(np.array([1.0, 1.0, 1.0]), 0.001)
    npt.assert_array_equal(ids, [])

    ids = point_cloud.ball_query(np.array([1.0, 1.0, 1.0]), 2.0)

    _assert_unordered_equal(ids, [5, 6])


def test_upper_half_ball_query():
    point_cloud = create_point_cloud()

    ref_point = np.array([0.2, 0.2, 0.2])
    direction = -np.array([1.0, 1.0, 1.0])
    direction /= np.linalg.norm(direction)

    # ball_query will return [0, 1]
    ids = point_cloud.upper_half_ball_query(ref_point, 10.0, direction)

    _assert_unordered_equal(ids, [3, 4, 5])


def test_partial_ball_query():
    point_cloud = create_point_cloud()

    ref_point = -np.ones(3)
    direction = np.array([1.0, 1.0, 1.0])
    direction /= np.linalg.norm(direction)

    radius = np.linalg.norm(ref_point - np.array([5.0, 5.0, 5.0]))

    d1 = np.linalg.norm(ref_point - np.array([2.5, 2.5, 2.5]))
    d2 = np.linalg.norm(ref_point - np.array([-4.1, -4.1, -4.0]))

    cap_angle_front = np.arccos(d1 / radius)
    cap_angle_back = -np.arccos(d2 / radius)

    # ball_query will return [0, 1]
    ids = point_cloud.partial_ball_query(
        ref_point, radius, direction, cap_angle_front, cap_angle_back
    )

    _assert_unordered_equal(ids, [3, 4, 5, 6])


def test_remove_ids():
    to_remove = np.array([4, 3, 9, 1])

    point_cloud = create_point_cloud()
    point_cloud.remove_ids(to_remove)

    npt.assert_array_equal(point_cloud.removed_ids, [1, 3, 4, 9])


def test_nearest_neighbor_direction():
    point_cloud = create_point_cloud()

    point = np.ones(3) + 0.2

    expected_direction = np.ones(3) * 2.0 - point
    expected_direction /= np.linalg.norm(expected_direction)

    npt.assert_allclose(point_cloud.nearest_neighbor_direction(point, 2.0), expected_direction)

    assert point_cloud.nearest_neighbor_direction(point, 0.001) is None


def test_remove_points_around():
    point_cloud = create_point_cloud()
    point = np.array([0.1, 0.1, 0.1])

    all_ids = point_cloud.available_ids

    removed_ids_1 = point_cloud.remove_points_around(point, 0.2)

    assert np.intersect1d(removed_ids_1, point_cloud.available_ids).size == 0

    remaining_ids = np.setdiff1d(all_ids, removed_ids_1)
    npt.assert_array_equal(remaining_ids, point_cloud.available_ids)

    removed_ids_2 = point_cloud.remove_points_around(point, 0.3)
    assert np.intersect1d(removed_ids_2, point_cloud.available_ids).size == 0

    remaining_ids = np.setdiff1d(remaining_ids, removed_ids_2)
    npt.assert_array_equal(remaining_ids, point_cloud.available_ids)


def test_remove_hemisphere():
    point_cloud = create_point_cloud()

    point = np.zeros(3)
    radius = 100.0
    direction = -np.ones(3)
    direction /= np.linalg.norm(direction)

    point_cloud.remove_hemisphere(point, direction, radius)

    npt.assert_array_equal(point_cloud.removed_ids, [0, 1, 2, 3, 4, 5])
