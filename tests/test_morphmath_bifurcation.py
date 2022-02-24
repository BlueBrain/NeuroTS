"""Test neurots.morphmath.bifurcation code."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
