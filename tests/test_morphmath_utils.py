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
    target = np.array([0.5932438 , 0.96379423, 0.49277981])

    expected_length = 0.6116359455469541
    expected_direction = np.array([0.12997936, 0.92580684, 0.35494657])

    direction = tested.from_to_direction(point, target, return_length=False)
    npt.assert_allclose(direction, expected_direction)

    direction, length = tested.from_to_direction(point, target, return_length=True)
    npt.assert_allclose(direction, expected_direction)
    npt.assert_allclose(length, expected_length)


def test_in_same_halfspace():

    points = np.array([[0., 0., 0.], [1., 1., 1.], [2., 2., 2.]])

    ref_point = np.array([0.5, 0.5, 0.5])

    direction = -np.array([1., 1., 1.])
    direction /= np.linalg.norm(direction)

    mask = tested.in_same_halfspace(points - ref_point, direction)
    npt.assert_array_equal(mask, [True, False, False])

    mask, dots = tested.in_same_halfspace(points - ref_point, direction, return_dots=True)
    npt.assert_array_equal(mask, [True, False, False])

    npt.assert_allclose(dots, - np.dot(ref_point, direction))


def test_in_squared_proximity():
    point1 = np.array([0., 0., 1.])
    point2 = np.array([0., 0., 3.])

    squared_proximity = 4.
    assert tested.in_squared_proximity(point1, point2, squared_proximity)

    squared_proximity = 3.9
    assert not tested.in_squared_proximity(point1, point2, squared_proximity)


def test_ball_query():

    points = np.array([
        [0., 0., -2.],
        [0., 0., -1.],
        [0., 0., 0.],
        [0., 0., 1.],
        [0., 0., 2.]

    ])

    ids = tested.ball_query(points, np.array([0., 0., 0.]), 1.0)
    npt.assert_array_equal(ids, [1, 2, 3])


def test_upper_half_ball_query():

    points = np.array([[10., 10., 10.], [11., 11., 11.]])
    ids = tested.upper_half_ball_query(
        points, np.zeros(3), 0.1, np.array([1., 0., 0.]))
    assert ids.size == 0

    points = np.array([
        [0., 0., -2.],
        [0., 0., -1.],
        [0., 0., 0.],
        [0., 0., 1.],
        [0., 0., 2.]

    ])

    ids = tested.upper_half_ball_query(points, np.array([0., 0., 0.]), 1.0, np.array([-1., 0., -1.]))
    npt.assert_array_equal(ids, [1])


