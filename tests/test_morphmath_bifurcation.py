"""Test neurots.morphmath.bifurcation code."""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=missing-function-docstring
import numpy as np
from numpy.testing import assert_array_almost_equal

from neurots.morphmath import bifurcation as _bf
from neurots.morphmath import rotation
from neurots.utils import Y_DIRECTION


def test_get_bif_directional():
    assert_array_almost_equal(
        _bf.directional([0.0, 1.0, 0.0], [0.0, 0.0, 0.0, np.pi / 2]),
        (np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0])),
    )
    assert_array_almost_equal(
        _bf.directional([0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 0]),
        (np.array([0.0, 1.0, 0.0]), np.array([0.0, 1.0, 0.0])),
    )
    assert_array_almost_equal(
        _bf.directional([0.0, 1.0, 0.0], [0.0, 0.0, 0.0, np.pi]),
        (np.array([0.0, 1.0, 0.0]), np.array([0.0, -1.0, 0.0])),
    )
    assert_array_almost_equal(
        _bf.directional([0.0, 1.0, 0.0], [0.0, 0.0, 0.0, np.pi / 4]),
        (
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 1.0 / np.sqrt(2), 1.0 / np.sqrt(2)]),
        ),
    )
    rot = rotation.rotation_matrix_from_vectors(Y_DIRECTION, [1, 0, 0]).T

    assert_array_almost_equal(
        _bf.directional([0.0, 1.0, 0.0], [0.0, 0.0, 0.0, np.pi / 4], y_rotation=rot),
        (
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
        ),
    )


def test_get_bif_bio_oriented():
    assert_array_almost_equal(
        _bf.bio_oriented([0.0, 1.0, 0.0], [0.0, 0.0, 0.0, np.pi / 4]),
        (
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 1.0 / np.sqrt(2), 1.0 / np.sqrt(2)]),
        ),
    )
    assert_array_almost_equal(
        _bf.bio_oriented([0.0, 1.0, 0.0], [0.0, np.pi / 4, 0.0, np.pi / 4]),
        (np.array([0.0, 1.0 / np.sqrt(2), 1.0 / np.sqrt(2)]), np.array([0.0, 0, 1])),
    )

    rot = rotation.rotation_matrix_from_vectors(Y_DIRECTION, [1, 0, 0]).T
    assert_array_almost_equal(
        _bf.bio_oriented([0.0, 1.0, 0.0], [0.0, np.pi / 4, 0.0, np.pi / 4], y_rotation=rot),
        (np.array([0.0, 1.0, 0.0]), np.array([0.0, 1.0, 0.0])),
    )


def test_get_bif_symmetric():
    assert_array_almost_equal(
        _bf.symmetric([0, 0, 1], [1, 1, 1, 1]),
        [[0.0, -0.479426, 0.877583], [0.0, 0.479426, 0.877583]],
    )
    rot = rotation.rotation_matrix_from_vectors(Y_DIRECTION, [1, 0, 0]).T
    assert_array_almost_equal(
        _bf.symmetric([0, 0, 1], [1, 1, 1, 1], y_rotation=rot),
        [[0.479426, 0.0, 0.877583], [-0.479426, 0.0, 0.877583]],
    )
