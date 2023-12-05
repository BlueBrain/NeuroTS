"""Astrocyte section growers."""

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
from collections import namedtuple

import numpy as np

from neurots.generate.section import SectionGrowerPath
from neurots.morphmath.utils import from_to_direction
from neurots.morphmath.utils import get_random_point
from neurots.morphmath.utils import in_squared_proximity
from neurots.morphmath.utils import normalize_inplace

L = logging.getLogger(__name__)


NextPointData = namedtuple("NextPointData", ["point", "direction", "segment_length"])


def grow_to_target(start_point, start_direction, target_point, segment_length, p=0.5):
    """Grow towards the target_point with segment_length step from the given point and direction.

    Args:
        start_point (numpy.ndarray): Starting point of the grower.
        start_direction (numpy.ndarray): Normalized initial direction.
        target_point (numpy.ndarray): Target point to grow to.
        segment_length (numpy.ndarray): The step size of the grower.
        p (float, optional): Influence from the target.
            If zero the grower will grow a straight line
            from the start point along the initial direction, and if 1.0 it will grow
            a straight line from the start point to the target point. Defaults to 0.5

    Returns:
        list[numpy.ndarray]: A list of the generated 3D points.
    """
    target_proximity = (1.5 * segment_length) ** 2

    point = start_point.copy()
    direction = start_direction.copy()

    points = []
    while not in_squared_proximity(point, target_point, target_proximity):
        target_direction = from_to_direction(point, target_point)
        direction = (1.0 - p) * direction + p * target_direction

        # zeros direction results from an initial direction which opposite to the target one
        # and the p = 0.5 . In that case the target_direction is used instead.
        direction = (
            target_direction if np.allclose(direction, 0.0) else normalize_inplace(direction)
        )

        point += segment_length * direction
        points.append(point)

    # add the target point if the new point does not coincide
    if not np.allclose(point, target_point):
        points.append(target_point)

    return points


class SectionSpatialGrower(SectionGrowerPath):
    """Section grower that is influenced by a point cloud.

    .. note::
        The main difference with a regular grower is that randomness is calculated by the nearest
        neighbor in the point cloud. This way there is a local influence by the distribution of the
        seeds. As the seeds get removed when a new point is created, the new points are influenced
        only by the seeds that area available. This leads to a more spread out occupancy of space.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._influence_distance = self.context.influence_distance(self.step_size_distribution.loc)

    @property
    def point_cloud(self):
        """Returns point cloud from context."""
        return self.context.point_cloud

    @property
    def morphology_points(self):
        """Returns entire morphology's points from context."""
        return self.context.morphology_points

    def _add_new_data(self, point, direction, segment_length):
        """Update relevant data after a next point action.

        Following a next point action, make an update of the relevant data and remove a hemisphere
        of seed points around center point, directed backwards to direction.
        """
        self.update_pathlength(segment_length)

        self.points.append(point)
        self.morphology_points.append(point)
        self.latest_directions.append(direction)

        kill_distance = self.context.kill_distance(segment_length)
        self.point_cloud.remove_hemisphere(point, -direction, kill_distance)

        return NextPointData(point, direction, segment_length)

    def first_point(self):
        """Generates the first point of the section.

        The generation depends on the growth method and the previous point. This gives
        flexibility to implement a specific computation for the first point, and ensures the
        section has at least one point.

        .. warning::
            The first point should be always called from the initialization when the section grower
            is added in the active list. It guarantees at least two point sections.
        """
        new_direction = normalize_inplace(0.8 * self.direction + 0.2 * self.history())
        segment_length = self.step_size_distribution.draw_positive()
        new_point = self.last_point + segment_length * new_direction
        self._add_new_data(new_point, new_direction, segment_length)

    def _neighbor_contribution(self, current_point):
        """Return the direction considering the nearest neighbor.

        Random contribution has a two case component: the influence from the closest
        seed attractor if any, otherwise a random direction.
        """
        pcloud_direction = self.point_cloud.nearest_neighbor_direction(
            current_point, self._influence_distance
        )

        if pcloud_direction is not None:
            return pcloud_direction

        return get_random_point(random_generator=self._rng)

    def next_direction(self, current_point):
        """Return the next direction.

        Given a starting point, find the new direction taking into account
        three contributions: the targeting, history and random contributions. Space
        colonization random contribution is calculated by the closest seed point
        in the point cloud.

        Args:
            current_point (numpy.ndarray): The current point.

        Returns:
            numpy.ndarray: The normalized direction.
        """
        return normalize_inplace(
            self.params.targeting * self.direction
            + self.params.history * self.history()
            + self.params.randomness * self._neighbor_contribution(current_point)
        )

    def _next_point(self, current_point):
        """Create the next point.

        Also update if no collision takes place or if the section type is endfoot.
        In addition, if the section type is endfoot, grow all points until
        the endfoot target and return None, to terminate.
        """
        segment_length = self.step_size_distribution.draw_positive()

        new_direction = self.next_direction(current_point)
        new_point = current_point + segment_length * new_direction

        if self.process == "endfoot":
            self._add_new_data(new_point, new_direction, segment_length)
            self._grow_endfoot_section(new_point, new_direction, segment_length)
            return None

        if self.context.collision_handle(new_point, segment_length):
            return None

        return self._add_new_data(new_point, new_direction, segment_length)

    def _grow_endfoot_section(self, initial_point, initial_direction, segment_length):
        """Creates all the points of the endfoot section at once and makes the relevant updates."""
        target_point = self.context.endfeet_targets.points[self.stop_criteria["target_id"]]

        grown_points = grow_to_target(
            initial_point, initial_direction, target_point, segment_length
        )

        for p in grown_points:
            self.points.append(p)
            self.morphology_points.append(p)
            self.point_cloud.remove_points_around(p, segment_length)

    def next(self):
        """Creates one point and returns the next state: bifurcate, terminate or continue."""
        if not self._next_point(self.last_point):
            self.children = 0
            return "terminate"

        if self.check_stop():
            return "continue"

        if self.children == 0:
            return "terminate"

        return "bifurcate"
