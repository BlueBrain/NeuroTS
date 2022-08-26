"""Test JSON schema validation."""

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

import json
import os
from pathlib import Path

from neurots import validator
from neurots.utils import convert_from_legacy_neurite_type

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _validation(file, func, kind, data):
    try:
        func(data)
    except Exception as err:
        raise ValueError(f"The file {file} is not valid according to the {kind} schema") from err


def test_json_schema():
    """Test all JSON schemas."""
    for i in Path(_PATH).iterdir():
        if i.suffix != ".json" or "persistence_diagram" in str(i):
            continue

        with i.open(encoding="utf-8") as f:
            data = convert_from_legacy_neurite_type(json.load(f))

        if "param" in str(i):
            _validation(i, validator.validate_neuron_params, "parameters", data)
        elif "distr" in str(i):
            _validation(i, validator.validate_neuron_distribs, "distributions", data)
        else:
            raise ValueError(f"The file {i} does not contain 'param' nor 'distr'")
