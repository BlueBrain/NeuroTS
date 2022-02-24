"""Test NeuroTS.utils code."""

# Copyright (C) 2022  Blue Brain Project, EPFL
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
from copy import deepcopy

import dictdiffer  # pylint: disable=import-error
import numpy as np
import pytest

from neurots import utils


def test_format_values():
    data = {
        "array_int": np.array([1, 2]),
        "array_float": np.array([1.1, 2.2]),
        "array_obj": np.array(["a", [1, 2]]),
        "2d_array_int": np.array([[1, 2]], ndmin=2),
        "2d_array_float": np.array([[1.1, 2.2]], ndmin=2),
        "2d_array_obj": np.array([["a", [1, 2]]], ndmin=2),
        "float32": np.float32(1.1),
        "float64": np.float64(1.1),
        "int32": np.int32(1),
        "bool8": np.bool8(True),
    }
    data["sub_dict"] = deepcopy(data)
    data["sub_list"] = [deepcopy(data), deepcopy(data)]

    expected = {
        "array_int": [1, 2],
        "array_float": [1.1, 2.2],
        "array_obj": ["a", [1, 2]],
        "2d_array_int": [[1, 2]],
        "2d_array_float": [[1.1, 2.2]],
        "2d_array_obj": [["a", [1, 2]]],
        "float32": 1.1,
        "float64": 1.1,
        "int32": 1,
        "bool8": True,
    }
    expected["sub_dict"] = deepcopy(expected)
    expected["sub_list"] = [deepcopy(expected), deepcopy(expected)]

    with pytest.raises(AssertionError):
        assert not list(dictdiffer.diff(utils.format_values(data), expected))
    assert not list(dictdiffer.diff(utils.format_values(data, decimals=6), expected))
