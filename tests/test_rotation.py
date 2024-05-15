"""Test neurots.morphmath.rotation code."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
