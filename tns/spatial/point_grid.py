""" Point grid data structure and helpers
"""
import numpy as np


def squared_distance(p0, p1):
    """ returns the squared distance of the two points """
    vector = p1 - p0
    return vector.dot(vector)


def shell_neighborhood(level):
    """ Returns the ijk indices that correspond to
    a cubic shell of specific level. For example level 1
    will return the ijk for the 26 grid neighbors from the
    grid origin, level 2 the next cell of 98 neighbors etc.
    It does not include the ijk of the previous level (I.e. it's a shell).

               2
      1    . . . . .
    . . .  .       .
    .   .  .       .
    . . .  .       .
           . . . . .

    """
    if level == 0:
        yield (0, 0, 0)
        return

    n_range = list(range(-level, level + 1))

    for i in (-level, level):
        for j in n_range:
            for k in n_range:
                yield (i, j, k)

    r_range = list(range(-level + 1, level))

    for j in (-level, level):
        for i in r_range:
            for k in n_range:
                yield (i, j, k)

    for k in (-level, level):
        for i in r_range:
            for j in r_range:
                yield (i, j, k)


class PointGrid(object):
    """ Grid datastructure to store points

    Args:
        cutoff_distance: float
            The distance which will be used to calculate
            the voxel width

    Attributes:
        data:
            The array of the points stored in the grid.
        store:
            Dictionary of the grid cells where the point ids are stored.
    """

    def __init__(self, cutoff_distance):

        # cutoff radius is the diagonal of the voxel
        voxel_width = 2. * cutoff_distance / np.sqrt(3)

        self._inv_dl = 1. / voxel_width

        self.data = np.empty((0, 3), dtype=np.float)
        self.data_cell_ids = np.empty((0, 3), dtype=np.uintp)

        self._n_points = 0

        self.store = {}

    def __contains__(self, point_id):
        """ Check if point_id or array of ids are inside the grid """
        return np.all(np.isin(point_id, self.available_ids))

    def _number_of_indices(self):
        """ Number of available indices """
        return sum(len(p_set) for p_set in self.store.values())

    @property
    def number_of_points(self):
        """ Number of available points """
        return self._n_points

    @property
    def voxel_width(self):
        """ Grid voxel width """
        return 1. / self._inv_dl

    @property
    def cutoff_distance(self):
        """ input cutoff distance """
        return np.sqrt(3) * 0.5 * self.voxel_width

    @property
    def available_ids(self):
        """ Available point ids in the grid """
        return np.fromiter((i for i_set in self.store.values() for i in i_set), np.uintp)

    @property
    def available_points(self):
        """ Available points in the grid """
        return self.data[self.available_ids]

    def add_points(self, points):
        """ Add point array to the grid
        """
        cells_ijk = [self._point_to_ijk(point) for point in points]

        self.store = {ijk: set() for ijk in set(cells_ijk)}

        index_offset = len(self.data)

        for (i, ijk) in enumerate(cells_ijk):
            self.store[ijk].add(i + index_offset)

        self.data = np.vstack((self.data, points))
        self.data_cell_ids = np.vstack((self.data_cell_ids, cells_ijk))
        self._n_points = self._number_of_indices()

    def _point_to_ijk(self, point):
        """ Convert point to i, j, k """
        ijk_float = point * self._inv_dl
        return int(ijk_float[0]), int(ijk_float[1]), int(ijk_float[2])

    def upper_level_from_radius(self, radius):
        """ Get the level that includes the radius """
        return int(np.ceil(2. * radius * self._inv_dl))

    def _level_query(self, point, radius, levels):
        """ Get the points in the neighborhood cell defined by the level
        which are inside the sphere (point, radius)
        """
        squared_radius = radius ** 2
        i_c, j_c, k_c = self._point_to_ijk(point)
        for level in levels:
            for i, j, k in shell_neighborhood(level):
                new_ijk = (i_c + i, j_c + j, k_c + k)
                if new_ijk not in self.store:
                    continue
                for point_id in self.store[new_ijk]:
                    sq_dist = squared_distance(point, self.data[point_id])
                    if sq_dist < squared_radius:
                        yield point_id

    def ball_query(self, point, radius):
        """ Retreive all the points in the sphere (point, radius)
        Note: generator
        """
        levels = range(self.upper_level_from_radius(radius) + 1)
        return np.fromiter(self._level_query(point, radius, levels), dtype=np.intp)

    def expanding_ball_query(self, point, number_of_points):
        """ Expand the neighborhood and find the closest point ids to the
        given point
        """
        number_of_points = min(number_of_points, self.number_of_points)
        results = np.empty(number_of_points, dtype=np.intp)
        i_c, j_c, k_c = self._point_to_ijk(point)

        n = 0
        level = 0

        while n < number_of_points:
            level_ids = []

            for i, j, k in shell_neighborhood(level):
                new_ijk = (i_c + i, j_c + j, k_c + k)
                if new_ijk in self.store:
                    level_ids.extend(self.store[new_ijk])

            dists = np.linalg.norm(self.data[level_ids] - point, axis=1)

            for index in np.argsort(dists):
                results[n] = level_ids[index]
                n += 1
                if n == number_of_points:
                    return results

            level += 1

        return results[:n]

    def nearest_neighbor(self, point):
        """ Return the id and the distance of the closest
        neighbor to the point
        """
        i_c, j_c, k_c = self._point_to_ijk(point)

        closest_sq_distance = np.inf
        closest_point_id = None

        for level in [0, 1]:

            for i, j, k in shell_neighborhood(level):

                ijk = (i_c + i, j_c + j, k_c + k)

                if ijk in self.store:
                    for point_id in self.store[ijk]:
                        sq_dist = squared_distance(point, self.data[point_id])
                        if sq_dist < closest_sq_distance:
                            closest_sq_distance = sq_dist
                            closest_point_id = point_id

            if closest_point_id is not None:
                return closest_point_id, np.sqrt(closest_sq_distance)

        return closest_point_id, np.sqrt(closest_sq_distance)

    def remove(self, point_id):
        """ Remove a point from the grid if it exists
        """
        ijk = tuple(self.data_cell_ids[point_id])

        point_set = self.store[ijk]
        point_set.remove(point_id)

        self._n_points -= 1

        # if set is empty, delete the cell altogether
        if not point_set:
            del self.store[ijk]
