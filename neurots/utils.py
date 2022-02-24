"""NeuroTS utils used by multiple tools."""

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

import numpy as np


class NeuroTSError(Exception):
    """Raises NeuroTS error."""


def format_values(obj):
    """Format values of an object recursively."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, (np.bool8, np.bool_)):
        return bool(obj)
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = format_values(v)
    if isinstance(obj, list):
        for num, i in enumerate(obj):
            obj[num] = format_values(i)
    return obj


def _check(data):
    """Checks if data in dictionary are empty."""
    for key, val in data.items():
        if len(val) == 0:
            raise NeuroTSError(f"Empty distribution for diameter key: {key}")
