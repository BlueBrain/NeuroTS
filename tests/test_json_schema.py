"""Test JSON schema validation."""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

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
