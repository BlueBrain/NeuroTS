"""A JSON schema validator for parameters and distributions.

Visit https://json-schema.org/understanding-json-schema/ for more information about JSON schemas
"""
import json
from pathlib import Path

import pkg_resources
from jsonschema import validate

SCHEMA_PATH = pkg_resources.resource_filename("neurots", "schemas")

with Path(SCHEMA_PATH, "parameters.json").open() as f:
    PARAMS_SCHEMA = json.load(f)

with Path(SCHEMA_PATH, "distributions.json").open() as f:
    DISTRIBS_SCHEMA = json.load(f)


def validate_neuron_params(data):
    """Validate parameter dictionary."""
    validate(data, PARAMS_SCHEMA)


def validate_neuron_distribs(data):
    """Validate distribution dictionary."""
    validate(data, DISTRIBS_SCHEMA)
