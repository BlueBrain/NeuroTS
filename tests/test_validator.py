import json
import tns.validator as tested
from jsonschema.exceptions import ValidationError
from nose.tools import assert_raises

from pathlib import Path

DATA = Path(__file__).parent.resolve() / 'data'


def dummy_params():
    with (DATA / 'params2.json').open() as f:
        data = json.load(f)
    return data

def dummy_distribs():
    with (DATA / 'dummy_distribution.json').open() as f:
        data = json.load(f)
    return data

def interneuron_distribs():
    with (DATA / 'dummy_interneuron_distribution.json').open() as f:
        data = json.load(f)
    return data

def test_validate_params():
    tested.validate_neuron_params(dummy_params())
    data = dummy_params()
    data['apical']['orientation'] = None
    tested.validate_neuron_params(data)

    # It must be a list of vectors, not a single one
    data['apical']['orientation'] = [0, 0, 0]
    assert_raises(ValidationError, tested.validate_neuron_params, data)

def test_empty_params_raises():
    data = {'apical': {},
            'axon': {},
            'basal': {},
            'diameter_params': {'method': 'M5'},
            'grow_types': [],
            'origin': [0.0, 0.0, 0.0]}
    assert_raises(ValidationError, tested.validate_neuron_params, data)


def test_validate_neuron_distribs():
    tested.validate_neuron_distribs(dummy_distribs())
    tested.validate_neuron_distribs(interneuron_distribs())