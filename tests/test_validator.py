import json
from pathlib import Path

import pytest
from jsonschema.exceptions import ValidationError

import neurots.validator as tested

DATA = Path(__file__).parent.resolve() / 'data'


@pytest.fixture
def dummy_params():
    with (DATA / 'params2.json').open() as f:
        data = json.load(f)
    return data


@pytest.fixture
def dummy_distribs():
    with (DATA / 'dummy_distribution.json').open() as f:
        data = json.load(f)
    return data


@pytest.fixture
def interneuron_distribs():
    with (DATA / 'dummy_interneuron_distribution.json').open() as f:
        data = json.load(f)
    return data


class TestValidateParams:
    def test_default(self, dummy_params):
        tested.validate_neuron_params(dummy_params)

    def test_none_orientation(self, dummy_params):
        dummy_params['apical']['orientation'] = None
        tested.validate_neuron_params(dummy_params)

    def test_different_external_method(self, dummy_params):
        # If method != external it should not have any other entry than 'method'
        dummy_params['diameter_params'] = {
            "method": "default"
        }
        tested.validate_neuron_params(dummy_params)

    def test_default_diameter_unknown_key(self, dummy_params):
        dummy_params['diameter_params'] = {
            "method": "default",
            "other key": "any value"
        }
        with pytest.raises(ValidationError):
            tested.validate_neuron_params(dummy_params)

    def test_M1_diameter_unknown_key(self, dummy_params):
        dummy_params['diameter_params'] = {
            "method": "M1",
            "other key": "any value"
        }
        with pytest.raises(ValidationError):
            tested.validate_neuron_params(dummy_params)

    def test_external_diameter(self, dummy_params):
        # If method == external it may have any other entry than 'method'
        dummy_params['diameter_params'] = {
            "method": "external"
        }
        tested.validate_neuron_params(dummy_params)

    def test_external_diameter_unknown_key(self, dummy_params):
        dummy_params['diameter_params'] = {
            "method": "external",
            "other key": "any value"
        }
        tested.validate_neuron_params(dummy_params)

    def test_orientation(self, dummy_params):
        # It must be a list of vectors, not a single one
        dummy_params['apical']['orientation'] = [0, 0, 0]
        with pytest.raises(ValidationError):
            tested.validate_neuron_params(dummy_params)

    def test_unknown_root_key(self, dummy_params):
        # Unknown parameters can be added at the root
        dummy_params["unknown_param"] = 0
        tested.validate_neuron_params(dummy_params)


def test_empty_params_raises():
    data = {'apical': {},
            'axon': {},
            'basal': {},
            'diameter_params': {'method': 'M5'},
            'grow_types': [],
            'origin': [0.0, 0.0, 0.0]}
    with pytest.raises(ValidationError):
        tested.validate_neuron_params(data)


def test_validate_neuron_distribs(dummy_distribs, interneuron_distribs):
    tested.validate_neuron_distribs(dummy_distribs)
    tested.validate_neuron_distribs(interneuron_distribs)
