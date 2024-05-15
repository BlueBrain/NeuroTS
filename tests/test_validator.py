"""Test neurots.validator code."""

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
# pylint: disable=redefined-outer-name
import json
from pathlib import Path

import pytest

import neurots.validator as tested

DATA = Path(__file__).parent.resolve() / "data"


@pytest.fixture
def dummy_params():
    with (DATA / "params2.json").open(encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.fixture
def dummy_distribs():
    with (DATA / "dummy_distribution.json").open(encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.fixture
def interneuron_distribs():
    with (DATA / "dummy_interneuron_distribution.json").open(encoding="utf-8") as f:
        data = json.load(f)
    return data


def test_validate_params(dummy_params):
    tested.validate_neuron_params(dummy_params)
    dummy_params["apical_dendrite"]["orientation"] = None
    tested.validate_neuron_params(dummy_params)


class TestValidateParams:
    """Test the parameter validation."""

    def test_default(self, dummy_params):
        tested.validate_neuron_params(dummy_params)

    def test_none_orientation(self, dummy_params):
        dummy_params["apical_dendrite"]["orientation"] = None
        tested.validate_neuron_params(dummy_params)

    def test_different_external_method(self, dummy_params):
        # If method != external it should not have any other entry than 'method'
        dummy_params["diameter_params"] = {"method": "default"}
        tested.validate_neuron_params(dummy_params)

    def test_M1_diameter_unknown_key(self, dummy_params):
        dummy_params["diameter_params"] = {"method": "M1", "other key": "any value"}
        with pytest.raises(tested.ValidationError):
            tested.validate_neuron_params(dummy_params)

    def test_external_diameter(self, dummy_params):
        # If method == external it may have any other entry than 'method'
        dummy_params["diameter_params"] = {"method": "external"}
        tested.validate_neuron_params(dummy_params)

    def test_external_diameter_unknown_key(self, dummy_params):
        dummy_params["diameter_params"] = {
            "method": "external",
            "other key": "any value",
        }
        tested.validate_neuron_params(dummy_params)

    def test_orientation(self, dummy_params):
        # It must be a list of vectors, not a single one
        dummy_params["apical_dendrite"]["orientation"] = [0, 0, 0]
        with pytest.raises(tested.ValidationError):
            tested.validate_neuron_params(dummy_params)

    def test_unknown_root_key(self, dummy_params):
        # Unknown parameters can be added at the root
        dummy_params["unknown_param"] = 0
        tested.validate_neuron_params(dummy_params)

    def test_error_in_list(self, dummy_params):
        # Wrong element in lists should be reported correctly
        dummy_params["grow_types"] = ["UNKNOWN TYPE"]
        with pytest.raises(
            tested.ValidationError, match=r"In \[grow_types->0\]: 'UNKNOWN TYPE' is not one of"
        ):
            tested.validate_neuron_params(dummy_params)


def test_empty_params():
    data = {
        "apical_dendrite": {},
        "axon": {},
        "basal_dendrite": {},
        "diameter_params": {"method": "M5"},
        "grow_types": [],
        "origin": [0.0, 0.0, 0.0],
    }
    tested.validate_neuron_params(data)


def test_validate_neuron_distribs(dummy_distribs, interneuron_distribs):
    tested.validate_neuron_distribs(dummy_distribs)
    tested.validate_neuron_distribs(interneuron_distribs)
