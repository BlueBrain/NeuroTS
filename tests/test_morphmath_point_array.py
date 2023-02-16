"""Test neurots.morphmath.point_array code."""

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
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import numpy as np
import pytest
from numpy import testing as npt

from neurots.morphmath import point_array as _pa


@pytest.fixture
def dynamic_array():
    initial_capacity = 3
    resize_factor = 2

    array = _pa.DynamicPointArray(initial_capacity, resize_factor)

    return array


def test_dynamic_point_array_contructor(dynamic_array):
    assert len(dynamic_array) == 0

    npt.assert_allclose(dynamic_array.data, np.empty(shape=(0, 3)))

    assert dynamic_array._size == 0
    assert dynamic_array._capacity == 3


def test_dynamic_point_array_append(dynamic_array):
    p0 = np.random.random(3)
    dynamic_array.append(p0)
    npt.assert_allclose(dynamic_array.data, [p0])
    assert len(dynamic_array) == 1
    assert dynamic_array.capacity == 3

    p1 = np.random.random(3)
    dynamic_array.append(p1)
    npt.assert_allclose(dynamic_array.data, np.vstack((p0, p1)))
    assert len(dynamic_array) == 2
    assert dynamic_array.capacity == 3

    p2 = np.random.random(3)
    dynamic_array.append(p2)
    npt.assert_allclose(dynamic_array.data, np.vstack((p0, p1, p2)))
    assert len(dynamic_array) == 3
    assert dynamic_array.capacity == 3

    p3 = np.random.random(3)
    dynamic_array.append(p3)
    npt.assert_allclose(dynamic_array.data, np.vstack((p0, p1, p2, p3)))
    assert len(dynamic_array) == 4
    assert dynamic_array.capacity == 6
