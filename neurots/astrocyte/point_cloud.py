"""Point cloud class for synapses."""

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

import logging

import numpy as np
from scipy.spatial import KDTree

from neurots.morphmath.utils import norm as vectorial_norm

L = logging.getLogger(__name__)


MIN_EPS = -1e-6

# pylint: disable=unsubscriptable-object


class PointCloud:
    """Point cloud data structure with internal gridding for ball and nearest neighbor queries.

    The points that are removed are not removed from memory, but invalidated.

    Args:
        point_array (np.ndarray):
            Array of 3D points to store in the point cloud.
        cutoff_radius (float):
            The radius from which the bin size of the grid will be calculated.
        removal_radius (float):
            Radius that will be used for default removal. See attribute below.

    Attributes:
        default_removal_radius (float):
            A default radius that will be used for the remove_points_around if
            an explicit value is not passed in the method.
        default_radius_of_influence (float):
            A default radius for the calculation of the average direction if
            an explicit value is not passed in the method.
    """

    def __init__(self, points):
        self._tree = KDTree(np.asarray(points, dtype=np.float32), copy_data=False)
        self._available = np.ones(len(points), dtype=bool)

    @property
    def points(self):
        """Returns point cloud points."""
        return self._tree.data

    @property
    def available_ids(self):
        """Returns ids of available points."""
        return np.where(self._available)[0]

    @property
    def removed_ids(self):
        """Returns ids of removed points."""
        return np.where(~self._available)[0]

    @property
    def removed_points(self):
        """Returns removed points."""
        return self.points[self.removed_ids]

    @property
    def available_points(self):
        """Returns available points."""
        return self.points[self.available_ids]

    def ball_query(self, point, radius):
        """Ball query around point with radius."""
        indices = np.fromiter(
            self._tree.query_ball_point(point, radius, return_sorted=False, return_length=False),
            dtype=np.int64,
        )
        return indices[self._available[indices]]

    def partial_ball_query(self, point, radius, direction, cap_angle_front, cap_angle_back):
        """Truncated ball query."""
        ids = self.ball_query(point, radius)

        if ids.size == 0:
            return ids

        dots = (self.points[ids] - point).dot(direction)

        dot_above = radius * np.cos(cap_angle_front)
        dot_below = -radius * np.cos(cap_angle_back)

        return ids[(dots > dot_below) & (dots < dot_above)]

    def upper_half_ball_query(self, point, radius, direction):
        """Hemisphere query around point directed to direction."""
        return self.partial_ball_query(point, radius, direction, 0.0, 0.5 * np.pi)

    def nearest_neighbor(self, point, radius):
        """Get the nearest neighbor to the point with cuttoff radius."""
        _, index = self._tree.query(point, k=1, distance_upper_bound=radius)
        if index < self._available.size and self._available[index]:
            return index
        return None

    def nearest_neighbor_direction(self, point, radius):
        """Get nearest neighbor direction."""
        point_id = self.nearest_neighbor(point, radius)

        if point_id is None:
            return None

        vector = self.points[point_id] - point
        return vector / vectorial_norm(vector)

    def remove_ids(self, point_ids):
        """Remove points ids."""
        self._available[point_ids] = False

    def remove_points_around(self, point, radius):
        """Remove the points in the sphere located at point with removal_radius."""
        point_ids = self.ball_query(point, radius)
        self.remove_ids(point_ids)
        return point_ids

    def remove_hemisphere(self, point, direction, radius):
        """Remove hemisphere that points to direction."""
        point_ids = self.ball_query(point, radius)

        vectors = self.points[point_ids] - point
        point_ids = point_ids[vectors.dot(direction) > MIN_EPS]

        self.remove_ids(point_ids)
        return point_ids
