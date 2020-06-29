""" AStrocyte section growers """
import logging
from collections import namedtuple

import numpy as np

from tns.generate.section import SectionGrowerPath
from tns.astrocyte.math_utils import normalize_inplace
from tns.astrocyte.math_utils import in_squared_proximity
from tns.morphmath.utils import get_random_point
from tns.astrocyte.math_utils import from_to_direction


L = logging.getLogger(__name__)


NextPointData = namedtuple('NextPointData', ['point', 'direction', 'segment_length'])


def grow_to_target(point, direction, target_point, segment_length, p=0.5):
    """Starting from given point and direction grow towards the target_point
    with a segment_length step.

    Args:
        point (np.ndarray): Starting point of the grower
        direction (np.ndarray): Normalized initial direction
        target_point (np.nadarray): Target point to grow to
        segment_length (np.ndarray): The step size of the grower
        p (float, optional): Influence from the target.
            If zero the grower will grow a straight line
            from the start point along the initial direction, and if 1.0 it will grow
            a straight line from the start point to the target point. Defaults to 0.5

    Returns:
        list: A list of np.ndarray representing the generated 3D points
    """
    target_proximity = (1.5 * segment_length) ** 2

    points = []
    while not in_squared_proximity(point, target_point, target_proximity):

        direction = normalize_inplace(
            (1. - p) * direction + p * from_to_direction(point, target_point)
        )

        point = point + segment_length * direction
        points.append(point)

    # add the target point if the new point does not coincide
    if not np.allclose(point, target_point):
        points.append(target_point)

    return points


class SectionSpatialGrower(SectionGrowerPath):
    '''Section grower that is influenced by a point cloud. The main difference with
    a regular grower is that randomness is calculated by the nearest neighbor in the
    point cloud. This way there is a local influence by the distribution of the seeds.
    As the seeds get removed when a new point is created, the new points are influenced
    only by the seeds that area available. This leads to a more spread out occupancy of
    space.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._influence_distance = self.context.influence_distance(
            self.step_size_distribution.params['mean'])

    @property
    def point_cloud(self):
        """Returns point cloud from context"""
        return self.context.point_cloud

    @property
    def morphology_points(self):
        """Returns entire morphology's points from context"""
        return self.context.morphology_points

    def _add_new_data(self, point, direction, segment_length):
        """Following a next point action, make an update of the relevant data
        and remove a hemisphere of seed points around center point, directed backwards
        to direction."""
        self.update_pathlength(segment_length)

        self.points.append(point)
        self.morphology_points.append(point)
        self.latest_directions.append(direction)

        kill_distance = self.context.kill_distance(segment_length)
        self.point_cloud.remove_hemisphere(point, -direction, kill_distance)

        return NextPointData(point, direction, segment_length)

    def first_point(self):
        """Generates the first point of the section, depending
        on the growth method and the previous point. This gives
        flexibility to implement a specific computation for the
        first point, and ensures the section has at least one point.
        Warning! The first point should be always called from the initialization
        when the section grower is added in the active list. It guarrantees at
        least two point sections."""
        new_direction = normalize_inplace(0.8 * self.direction + 0.2 * self.history())
        segment_length = self.step_size_distribution.draw_positive()
        new_point = self.last_point + segment_length * new_direction
        self._add_new_data(new_point, new_direction, segment_length)

    def _neighbor_contribution(self, current_point):
        """Random contribution has a two case component: the influence from the closest
        seed attractor if any, otherwise a random direction
        """
        pcloud_direction = self.point_cloud.nearest_neighbor_direction(
            current_point, self._influence_distance)

        if pcloud_direction is not None:
            return pcloud_direction

        return get_random_point()

    def next_direction(self, current_point):
        '''Given a starting point, find the new direction taking into account
        three contributions: the targeting, history and random contributions. Space
        colonization random contribution is calculated by the closest seed point
        in the point cloud.

        Args:
            current_point (np.ndarray)
        Returns:
            normalized direction (np.ndarray)
        '''
        return normalize_inplace(
            self.params.targeting * self.direction +
            self.params.history * self.history() +
            self.params.randomness * self._neighbor_contribution(current_point)
        )

    def _next_point(self, current_point):
        """Create the next point and update if no collision takes place or if the section
        type is endfoot. In addition, if the section type is endfoot, grow all points until
        the endfoot target and return None, to terminate"""
        segment_length = self.step_size_distribution.draw_positive()

        new_direction = self.next_direction(current_point)
        new_point = current_point + segment_length * new_direction

        if self.process == 'endfoot':
            self._add_new_data(new_point, new_direction, segment_length)
            self._grow_endfoot_section(new_point, new_direction, segment_length)
            return None

        if self.context.collision_handle(new_point, segment_length):
            return None

        return self._add_new_data(new_point, new_direction, segment_length)

    def _grow_endfoot_section(self, initial_point, initial_direction, segment_length):
        """Creates all the points of the endfoot section in one go and makes the relevant
        updates.
        """
        target_point = self.context.endfeet_targets.points[self.stop_criteria['target_id']]

        grown_points = grow_to_target(
            initial_point, initial_direction, target_point, segment_length)

        for p in grown_points:
            self.points.append(p)
            self.morphology_points.append(p)
            self.point_cloud.remove_points_around(p, segment_length)

    def next(self):
        '''Creates one point and returns the next state.
           bifurcate, terminate or continue.
        '''
        if not self._next_point(self.last_point):
            self.children = 0
            return 'terminate'

        if self.check_stop():
            return 'continue'

        if self.children == 0:
            return 'terminate'

        return 'bifurcate'