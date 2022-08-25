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

import warnings
from copy import deepcopy

import numpy as np


class NeuroTSError(Exception):
    """Raises NeuroTS error."""


def format_values(obj, decimals=None):
    """Format values of an object recursively."""
    if isinstance(obj, np.ndarray):
        obj = obj.tolist()
    elif isinstance(obj, np.floating):
        obj = float(obj)
        if decimals is not None:
            obj = round(obj, ndigits=decimals)
    elif isinstance(obj, np.integer):
        obj = int(obj)
    elif isinstance(obj, (np.bool8, np.bool_)):
        obj = bool(obj)
    elif isinstance(obj, dict):
        obj = {k: format_values(v, decimals=decimals) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        obj = type(obj)([format_values(i, decimals=decimals) for i in obj])
    return obj


def neurite_type_warning(key):
    """Print a deprecation warning for old neurite_type key."""
    warnings.warn(
        f"The '{key}' property is deprecated, please use '{key}_dendrite' instead",
        DeprecationWarning,
    )


def convert_from_legacy_neurite_type(data):
    """Convert legacy neurite type names, basal -> basal_dendrite and apical -> apical_dendrite."""
    old_data = deepcopy(data)
    for key, _data in old_data.items():

        if key == "apical":
            neurite_type_warning(key)
            data["apical_dendrite"] = data.pop("apical")
            key = "apical_dendrite"
        if key == "basal":
            neurite_type_warning(key)
            data["basal_dendrite"] = data.pop("basal")
            key = "basal_dendrite"

        if isinstance(_data, dict):
            data[key] = convert_from_legacy_neurite_type(data[key])

        if isinstance(_data, list):
            for i, d in enumerate(_data):
                if d == "apical":
                    neurite_type_warning(key)
                    data[key][i] = "apical_dendrite"
                if d == "basal":
                    neurite_type_warning(key)
                    data[key][i] = "basal_dendrite"

    return data
