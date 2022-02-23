"""Test neurots.morphmath.rotation code."""

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
