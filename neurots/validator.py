"""A JSON schema validator for parameters and distributions.

Visit https://json-schema.org/understanding-json-schema/ for more information about JSON schemas.
"""

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
