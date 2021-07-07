"""A JSON schema validator for parameters and distributions.

Visit https://json-schema.org/understanding-json-schema/ for more information about JSON schemas
"""
import json
from pathlib import Path

import jsonschema
import pkg_resources

SCHEMA_PATH = pkg_resources.resource_filename("neurots", "schemas")

with Path(SCHEMA_PATH, "parameters.json").open() as f:
    PARAMS_SCHEMA = json.load(f)

with Path(SCHEMA_PATH, "distributions.json").open() as f:
    DISTRIBS_SCHEMA = json.load(f)


class ValidationError(Exception):
    """Exception raised when a JSON object is not valid according to a given schema."""


def _format_error(error):
    return f"""In [{"->".join(error.absolute_path)}]: {error.message}"""


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
