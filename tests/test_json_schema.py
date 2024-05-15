"""Test JSON schema validation."""

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

import json
import os
from pathlib import Path

import pytest

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
            if i.stem.endswith("_legacy"):
                with pytest.warns(DeprecationWarning):
                    data = convert_from_legacy_neurite_type(json.load(f))
            else:
                data = convert_from_legacy_neurite_type(json.load(f))

        if "param" in str(i):
            _validation(i, validator.validate_neuron_params, "parameters", data)
        elif "distr" in str(i):
            _validation(i, validator.validate_neuron_distribs, "distributions", data)
        else:
            raise ValueError(f"The file {i} does not contain 'param' nor 'distr'")
