"""Test neurots.astrocyte.context.EndfeetTargets code."""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=missing-function-docstring
import numpy as np
from numpy import testing as npt

from neurots.astrocyte import context as tested

TARGET_POINTS = np.array([[0.0, 1.0, 2.0], [2.0, 3.0, 4.0], [5.0, 6.0, 7.0]])


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
