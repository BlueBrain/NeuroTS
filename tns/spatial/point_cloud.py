""" Point cloud class for synapses
"""

import numpy as np
from .point_grid import PointGrid


class PointCloud(PointGrid):
    """ Point cloud data structure with internal gridding for ball and
    nearest neighbor queries.

    The points that are removed are not removed from memory, but invalidated.

    Args:
        point_array: float[N, 3]
            Array of 3D points to store in the point cloud.
        cutoff_radius: float
            The radius from which the bin size of the grid will be calculated.
        removal_radius: float
            Radius that will be used for default removal. See attribute below.

    Attributes:
        default_removal_radius: float
            A default radius that will be used for the remove_points_around if
            an explicit value is not passed in the method.
        default_radius_of_influence: float
            A default radius for the calculation of the average direction if
            an explicit value is not passed in the method.
    """
    def __init__(self, point_array, cutoff_radius, removal_radius):
        super(PointCloud, self).__init__(cutoff_radius)

        self.add_points(point_array)
        self.default_removal_radius = removal_radius
        self.default_radius_of_influence = cutoff_radius

    def average_direction(self, point,
                          radius_of_influence=None):
        """ Get average direction from the points around the given point
        which lie inside the incluence_radius
        """
        radius_of_influence = \
            self.default_radius_of_influence if radius_of_influence is None else \
            radius_of_influence

        point_ids = self.ball_query(point, radius_of_influence)

        if point_ids.size == 0:
            return None

        vectors = self.data[point_ids] - point
        vectors /= np.linalg.norm(vectors, axis=1)[:, np.newaxis]

        average_direction = vectors.mean(axis=0)
        average_direction /= np.linalg.norm(average_direction)

        return average_direction

    def nearest_neighbor_direction(self, point):
        """ Get nearest neighbor direction
        """
        point_id, _ = self.nearest_neighbor(point)

        if point_id is None:
            return None

        vector = self.data[point_id] - point
        return vector / np.linalg.norm(vector)

    def at_least_n_points_around(self, point, radius, n_points):
        """ Check if there are n_points in the ball located at point with
        radius.
        """
        return len(self.ball_query(point, radius)) >= n_points

    def remove_points_around(self, point, removal_radius=None):
        """ Remove the points in the sphere located at point with removal_radius """
        removal_radius = \
            self.default_removal_radius if removal_radius is None else removal_radius

        point_ids = self.ball_query(point, removal_radius)

        for point_id in point_ids:
            self.remove(point_id)

        return point_ids
