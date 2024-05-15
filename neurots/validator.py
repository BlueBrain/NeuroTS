"""A JSON schema validator for parameters and distributions.

Visit https://json-schema.org/understanding-json-schema/ for more information about JSON schemas.
"""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

import json

try:
    import importlib_resources as resources
except ImportError:
    from importlib import resources

import jsonschema

SCHEMA_PATH = resources.files("neurots") / "schemas"

with (SCHEMA_PATH / "parameters.json").open(encoding="utf-8") as f:
    PARAMS_SCHEMA = json.load(f)

with (SCHEMA_PATH / "distributions.json").open(encoding="utf-8") as f:
    DISTRIBS_SCHEMA = json.load(f)


class ValidationError(Exception):
    """Exception raised when a JSON object is not valid according to a given schema."""


def _format_error(error):
    return f"""In [{"->".join([str(i) for i in error.absolute_path])}]: {error.message}"""


def validate(instance, schema):
    """Validate a JSON object according to a given schema."""
    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    messages = []
    for error in errors:
        if error.context:
            for suberror in error.context:
                messages.append(_format_error(suberror))
        else:
            messages.append(_format_error(error))

    if messages:
        raise ValidationError("\n".join(messages))


def validate_neuron_params(data):
    """Validate parameter dictionary."""
    validate(data, PARAMS_SCHEMA)


def validate_neuron_distribs(data):
    """Validate distribution dictionary."""
    validate(data, DISTRIBS_SCHEMA)
