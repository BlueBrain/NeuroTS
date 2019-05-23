from numpy.testing import assert_allclose, assert_equal
from nose.tools import ok_
import numpy as np
from tns.spatial.point_grid import squared_distance
from tns.spatial.point_grid import shell_neighborhood
from tns.spatial.point_grid import PointGrid


def point_array():
    return np.array([[-10., -10., -10.],
                     [ -9.,  -9.,  -9.],
                     [ -8.,  -8.,  -8.],
                     [ -7.,  -7.,  -7.],
                     [ -6.,  -6.,  -6.],
                     [ -5.,  -5.,  -5.],
                     [ -4.,  -4.,  -4.],
                     [ -3.,  -3.,  -3.],
                     [ -2.,  -2.,  -2.],
                     [ -1.,  -1.,  -1.],
                     [  0.,   0.,   0.],
                     [  1.,   1.,   1.],
                     [  2.,   2.,   2.],
                     [  3.,   3.,   3.],
                     [  4.,   4.,   4.],
                     [  5.,   5.,   5.],
                     [  6.,   6.,   6.],
                     [  7.,   7.,   7.],
                     [  8.,   8.,   8.],
                     [  9.,   9.,   9.],
                     [ 10.,  10.,  10.]], dtype=np.float)


def _default_grid():
    points = point_array()
    cutoff_distance = 2.0
    point_grid = PointGrid(cutoff_distance)
    point_grid.add_points(points)

    return point_grid


def test_squared_distance():
    p1 = np.array((1., 1., 1.))
    p2 = np.array((2., 1., 1.))
    sq_dist = squared_distance(p1, p2)
    assert_allclose(sq_dist, 1.0), sq_dist


def test_shell_neighborhood():
    expected_level_1 = \
    np.array([(-1, -1, -1),
              (-1, -1, 0),
              (-1, -1, 1),
              (-1, 0, -1),
              (-1, 0, 0),
              (-1, 0, 1),
              (-1, 1, -1),
              (-1, 1, 0),
              (-1, 1, 1),
              (1, -1, -1),
              (1, -1, 0),
              (1, -1, 1),
              (1, 0, -1),
              (1, 0, 0),
              (1, 0, 1),
              (1, 1, -1),
              (1, 1, 0),
              (1, 1, 1),
              (0, -1, -1),
              (0, -1, 0),
              (0, -1, 1),
              (0, 1, -1),
              (0, 1, 0),
              (0, 1, 1),
              (0, 0, -1),
              (0, 0, 1)], dtype=np.int)

    res_0 = np.asarray(list(shell_neighborhood(0)), dtype=np.int)
    res_1 = np.asarray(list(shell_neighborhood(1)), dtype=np.int)

    assert np.all(expected_level_1 == res_1), res_1
    assert np.all(np.array([[0, 0, 0]]) ==  res_0), res_0


def test_properties():
    default_grid = _default_grid()

    assert_equal(default_grid.number_of_points, 21)
    assert_allclose(default_grid.cutoff_distance, 2.0)


def test_point_to_ijk():
    default_grid = _default_grid()
    point = np.array([1., 2., 3.])
    bucket_ijk = np.asarray(point / default_grid.voxel_width, dtype=np.int)
    assert_equal(default_grid._point_to_ijk(point),
                 bucket_ijk)


def test_ball_query_1():
    default_grid = _default_grid()
    point = np.array([-10., -10., -11.])
    radius = 1.0
    ids = default_grid.ball_query(point, radius)
    points = default_grid.data[ids]
    expected_points = np.array([[-10., -10., -10.]])

    assert np.allclose(points, expected_points), (points, expected_points)


def test_ball_query_2():
    default_grid = _default_grid()
    points = default_grid.data
    point = points[0]
    radius = np.linalg.norm(points[2] - points[0]) + 0.1
    point_ids = default_grid.ball_query(point, radius)

    assert_equal(set(point_ids), set([0, 1, 2]))


def test_ball_query_3():
    default_grid = _default_grid()
    points = default_grid.data
    point = np.array([0., 0., 0.])
    radius =  np.linalg.norm(points[0] - point)
    point_set = set(default_grid.ball_query(point, radius))
    expected_set = set(range(len(points)))

    assert_equal(point_set, expected_set)


def test_expanding_ball_query():
    default_grid = _default_grid()
    point = np.array([-11.,-11., -11.])
    step_radius = 1.0
    number_of_points = 100
    point_ids = default_grid.expanding_ball_query(point, number_of_points)

    ok_(np.all(point_ids == np.arange(21, dtype=np.intp)))


def test_nearest_neighbor():
    default_grid = _default_grid()
    point = np.array([-11.,-11., -11.])
    closest_point_id, closest_distance = default_grid.nearest_neighbor(point)
    expected_distance = np.linalg.norm([1., 1., 1.])

    assert_equal(closest_point_id, 0)


def test_nearest_neighbor_after_point_removal():
    default_grid = _default_grid()
    point = np.array([-11.,-11., -11.])
    default_grid.remove(0)
    closest_point_id, closest_distance = default_grid.nearest_neighbor(point)
    expected_distance = 2. * np.linalg.norm([1., 1., 1.])

    assert_allclose(closest_distance, expected_distance)
    assert_equal(closest_point_id, 1)


def test_remove_point():
    default_grid = _default_grid()
    points = default_grid.data
    point_ids = list(range(len(points)))
    to_remove = point_ids[::2]
    remaining_set = set(point_ids).difference(to_remove)

    for point_id in to_remove:
        default_grid.remove(point_id)

    assert_equal(set(default_grid.available_ids), remaining_set)
    assert_equal(default_grid.number_of_points, len(remaining_set))

    for point in remaining_set:
        default_grid.remove(point)

    assert_equal(len(default_grid.available_ids), 0)
    ok_(not default_grid.store)
    assert_equal(default_grid.number_of_points, 0)
