"""Test neurots.morphmath.bifurcation code."""

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

from neurots.morphmath import bifurcation as _bf


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


def test_get_bif_symmetric():
    assert_array_almost_equal(
        _bf.symmetric([0, 0, 1], [1, 1, 1, 1]),
        [[0.0, -0.479426, 0.877583], [0.0, 0.479426, 0.877583]],
    )
