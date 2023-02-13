"""Test the neurots.preprocess functions."""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
import json
import logging
from collections import defaultdict
from pathlib import Path

import pytest

from neurots import preprocess
from neurots.preprocess.exceptions import NeuroTSValidationError
from neurots.preprocess.utils import register_preprocessor
from neurots.preprocess.utils import register_validator
from neurots.utils import convert_from_legacy_neurite_type

DATA_PATH = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    "params_file, distrs_file",
    [
        pytest.param("axon_trunk_parameters.json", "axon_trunk_distribution.json", id="axon trunk"),
        pytest.param(
            "axon_trunk_parameters_orientation_manager.json",
            "axon_trunk_distribution.json",
            id="axon trunk using orientation manager",
        ),
        pytest.param(
            "axon_trunk_parameters_absolute.json",
            "axon_trunk_distribution.json",
            id="axon trunk absolute",
        ),
        pytest.param(
            "axon_trunk_parameters_absolute_orientation_manager.json",
            "axon_trunk_distribution.json",
            id="axon trunk absolute using orientation manager",
        ),
        pytest.param("trunk_parameters.json", "bio_trunk_distribution.json", id="bio trunk"),
        pytest.param("bio_path_params.json", "bio_distribution.json", id="bio path"),
        pytest.param(
            "bio_path_params_orientation_manager.json",
            "bio_distribution.json",
            id="bio path using orientation manager",
        ),
        pytest.param("bio_gradient_path_params.json", "bio_distribution.json", id="bio gradient"),
        pytest.param(
            "bio_gradient_path_params_orientation_manager.json",
            "bio_distribution.json",
            id="bio gradient using orientation manager",
        ),
        pytest.param("params1.json", "bio_rat_L5_TPC_B_distribution.json", id="bio rat params1"),
        pytest.param(
            "params1_orientation_manager.json",
            "bio_rat_L5_TPC_B_distribution.json",
            id="bio rat params1 using orientation manager",
        ),
        pytest.param("params2.json", "bio_rat_L5_TPC_B_distribution.json", id="bio rat params2"),
        pytest.param(
            "params2_orientation_manager.json",
            "bio_rat_L5_TPC_B_distribution.json",
            id="bio rat params2 using orientation manager",
        ),
        pytest.param("params3.json", "bio_rat_L5_TPC_B_distribution.json", id="bio rat params3"),
        pytest.param(
            "params3_orientation_manager.json",
            "bio_rat_L5_TPC_B_distribution.json",
            id="bio rat params3 using orientation manager",
        ),
        pytest.param("params4.json", "bio_rat_L5_TPC_B_distribution.json", id="bio rat params4"),
        pytest.param(
            "params4_orientation_manager.json",
            "bio_rat_L5_TPC_B_distribution.json",
            id="bio rat params4 using orientation manager",
        ),
    ],
)
def test_params_and_distrs(params_file, distrs_file):
    """Test preprocessing of params and distrs."""
    with (DATA_PATH / params_file).open(encoding="utf-8") as f:
        params = convert_from_legacy_neurite_type(json.load(f))

    with (DATA_PATH / distrs_file).open(encoding="utf-8") as f:
        distrs = convert_from_legacy_neurite_type(json.load(f))

    preprocess.preprocess_inputs(params, distrs)


def test_check_num_seg():
    """Check that the parametesr have a 'num_seg' entry.

    Note: The type is already checked in the validation step with the JSON schema.
    """
    params = {}

    with pytest.raises(
        NeuroTSValidationError,
        match=(
            "The parameters must contain a 'num_seg' entry when the "
            "'growth_method' entry in parameters is 'trunk'."
        ),
    ):
        preprocess.validity_checkers.check_num_seg(params, {})

    params["num_seg"] = 1
    preprocess.validity_checkers.check_num_seg(params, {})


def test_check_min_bar_length(caplog):
    """Check that the parametesr have a 'num_seg' entry.

    Note: The type is already checked in the validation step with the JSON schema.
    """

    with pytest.raises(
        NeuroTSValidationError,
        match=(
            r"The distributions must contain a 'min_bar_length' entry when the "
            r"'growth_method' entry in parameters is in \['tmd', 'tmd_apical', 'tmd_gradient'\]\."
        ),
    ):
        preprocess.validity_checkers.check_bar_length({}, {})

    distrs = {
        "min_bar_length": 1,
    }

    with pytest.raises(
        NeuroTSValidationError,
        match=(
            r"The parameters must contain a 'step_size' entry when the "
            r"'growth_method' entry in parameters is in \['tmd', 'tmd_apical', 'tmd_gradient'\]\."
        ),
    ):
        preprocess.validity_checkers.check_bar_length({}, distrs)

    params = {
        "step_size": {
            "norm": {
                "mean": 999,
            }
        }
    }
    caplog.clear()
    with caplog.at_level(logging.DEBUG):
        preprocess.validity_checkers.check_bar_length(params, distrs)
    assert caplog.record_tuples == [
        (
            "neurots.preprocess.relevance_checkers",
            30,
            "Selected step size 999.000000 is too big for bars of size 1.000000",
        )
    ]

    params = {
        "step_size": {
            "norm": {
                "mean": 0.1,
            }
        }
    }
    caplog.clear()
    with caplog.at_level(logging.DEBUG):
        preprocess.validity_checkers.check_bar_length(params, distrs)
    assert caplog.record_tuples == []


@pytest.fixture
def dummy_register(monkeypatch):
    """Monkeypatch the registered functions and reset it at the end of the test."""
    monkeypatch.setattr(
        preprocess.utils,
        "_REGISTERED_FUNCTIONS",
        {
            "preprocessors": defaultdict(set),
            "validators": defaultdict(set),
            "global_preprocessors": set(),
            "global_validators": set(),
        },
    )


def test_register_validator(dummy_register):
    """Test validator registering."""
    with (DATA_PATH / "axon_trunk_parameters.json").open(encoding="utf-8") as f:
        params = convert_from_legacy_neurite_type(json.load(f))
    with (DATA_PATH / "axon_trunk_distribution.json").open(encoding="utf-8") as f:
        distrs = convert_from_legacy_neurite_type(json.load(f))

    @register_validator("axon_trunk")
    def dummy_validator(params, distrs):
        assert params["randomness"] == 0
        assert distrs["num_trees"]["data"]["bins"] == [1]

    assert params["axon"]["randomness"] == 0
    assert distrs["axon"]["num_trees"]["data"]["bins"] == [1]

    preprocessed_params, preprocessed_distrs = preprocess.preprocess_inputs(params, distrs)

    assert preprocessed_params == params
    assert preprocessed_distrs == distrs


def test_register_preprocessor(dummy_register):
    """Test preprocessor registering."""
    with (DATA_PATH / "axon_trunk_parameters.json").open(encoding="utf-8") as f:
        params = convert_from_legacy_neurite_type(json.load(f))
    with (DATA_PATH / "axon_trunk_distribution.json").open(encoding="utf-8") as f:
        distrs = convert_from_legacy_neurite_type(json.load(f))

    @register_preprocessor("axon_trunk")
    def dummy_preprocessor(params, distrs):
        params["randomness"] = 999
        distrs["num_trees"]["data"]["bins"] = [999]

    assert params["axon"]["randomness"] == 0
    assert distrs["axon"]["num_trees"]["data"]["bins"] == [1]

    preprocessed_params, preprocessed_distrs = preprocess.preprocess_inputs(params, distrs)

    assert preprocessed_params["axon"]["randomness"] == 999
    assert preprocessed_distrs["axon"]["num_trees"]["data"]["bins"] == [999]
