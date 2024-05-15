"""Point array class."""

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

import numpy as np


class DynamicPointArray:
    """Store points in a numpy array and automatically resizes when its capacity is reached.

    It is used by algorithms that require the points as a :class:`numpy.array` and append points
    incrementally.

    Args:
        initial_capacity (int): The initial capacity of the array.
        resize_factor (float): The factor used to increase the capacity of the array.
    """

    def __init__(self, initial_capacity=100000, resize_factor=2.0):
        self._size = 0
        self._capacity = initial_capacity
        self._resize_factor = resize_factor
        self._data = np.empty((initial_capacity, 3), dtype=np.float32)

    def __len__(self):
        """Return the length of the array."""
        return self._size

    @property
    def capacity(self):
        """Returns the current capacity of the array."""
        return self._capacity

    @property
    def data(self):
        """Return filled data."""
        return self._data[: self._size]

    def _resize_capacity(self):
        """Resizes the capacity when the size equals capacity."""
        self._capacity = int(self._resize_factor * self._capacity)
        self._data = np.resize(self._data, (self._capacity, 3))

    def append(self, point):
        """Append a point to the array."""
        if self._size == self._capacity:
            self._resize_capacity()

        self._data[self._size] = point
        self._size += 1
