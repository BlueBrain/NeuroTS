import numpy as np
from numpy import testing as npt

from neurots.astrocyte import context as tested


TARGET_POINTS = np.array([
    [0., 1., 2.],
    [2., 3., 4.],
    [5., 6., 7.]
])


def test_constructor():
    targets = tested.EndfeetTargets(TARGET_POINTS)
    npt.assert_allclose(targets.points, TARGET_POINTS)
    npt.assert_array_equal(targets.active, True)
    npt.assert_equal(len(targets), 3)


def test_active_points():
    targets = tested.EndfeetTargets(TARGET_POINTS)

    targets.active[1] = False
    npt.assert_allclose(targets.active_points, TARGET_POINTS[(0, 2), :])

    targets.active[:] = False
    npt.assert_equal(len(targets.active_points), 0)
