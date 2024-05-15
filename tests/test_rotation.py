"""Test neurots.morphmath.rotation code."""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=missing-function-docstring
import numpy as np
from numpy.testing import assert_array_almost_equal

import neurots.morphmath.rotation as test_module


def test_vector_from_spherical():
    assert_array_almost_equal(
        test_module.vector_from_spherical(1, 1), [0.454649, 0.708073, 0.540302]
    )


def test_rotate_vector():
    assert_array_almost_equal(
        test_module.rotate_vector([1, 1, 1], [2, 3, 4], 2),
        [0.293989, 1.240039, 1.172976],
    )


def test_angle3D():
    assert_array_almost_equal(test_module.angle3D([1, 1, 1], [2, 3, 4]), 0.265729)


def test_rotation_matrix_from_vectors():
    vec1 = np.array([0, 1, 0])
    vec2 = np.array([1, 1, 1])
    rot = test_module.rotation_matrix_from_vectors(vec1, vec2)
    assert_array_almost_equal(
        rot,
        np.array(
            [
                [0.78867513, 0.57735027, -0.21132487],
                [-0.57735027, 0.57735027, -0.57735027],
                [-0.21132487, 0.57735027, 0.78867513],
            ]
        ),
    )

    rot = test_module.rotation_matrix_from_vectors(vec1, vec1)
    assert_array_almost_equal(rot, np.eye(3))
