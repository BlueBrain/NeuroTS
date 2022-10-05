"""Test the neurots.preprocess functions."""
import json
from pathlib import Path

import pytest

from neurots import preprocess
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
