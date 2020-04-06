'''A JSON schema validator for parameters and distributions

Visit https://json-schema.org/understanding-json-schema/ for more information about JSON schemas
'''
import json
from pathlib import Path

from jsonschema import validate


with (Path(__file__).parent.parent.resolve() / 'schemas' / 'parameters.json').open() as f:
    PARAMS_SCHEMA = json.load(f)

with (Path(__file__).parent.parent.resolve() / 'schemas' / 'distributions.json').open() as f:
    DISTRIBS_SCHEMA = json.load(f)


def validate_neuron_params(data):
    '''Validate parameter dictionary'''
    validate(data, PARAMS_SCHEMA)


def validate_neuron_distribs(data):
    '''Validate distribution dictionary'''
    validate(data, DISTRIBS_SCHEMA)
