"""Test neurots.extract_input code."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import os

import neurom
import numpy as np
import pytest
import tmd
from neurom import load_morphologies
from numpy.testing import assert_array_almost_equal
from numpy.testing import assert_equal
from pkg_resources import parse_version

from neurots import NeuroTSError
from neurots import extract_input
from neurots import validator

_OLD_NUMPY = parse_version(np.__version__) < parse_version("1.21")

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_data")
POP_PATH = os.path.join(_PATH, "bio/")
NEU_PATH = os.path.join(_PATH, "diam_simple.swc")


@pytest.fixture
def POPUL():
    return load_morphologies(POP_PATH)


@pytest.fixture
def NEU():
    return load_morphologies(NEU_PATH)


def test_num_trees(POPUL):
    target_numBAS = {
        "num_trees": {"data": {"bins": [4, 5, 6, 7, 8, 9], "weights": [1, 0, 0, 0, 0, 1]}}
    }
    target_numAX = {"num_trees": {"data": {"bins": [1], "weights": [2]}}}

    numBAS = extract_input.from_neurom.number_neurites(POPUL)
    numAX = extract_input.from_neurom.number_neurites(POPUL, neurite_type=neurom.AXON)
    assert_equal(numBAS, target_numBAS)
    assert_equal(numAX, target_numAX)


def test_trunk_distr(POPUL, NEU):
    bins_BAS = [
        0.19391773616376634,
        0.4880704446023673,
        0.7822231530409682,
        1.076375861479569,
        1.3705285699181702,
        1.6646812783567713,
        1.9588339867953721,
        2.2529866952339734,
        2.547139403672574,
        2.841292112111175,
    ]

    absolute_elevation_deviation_BAS = {
        "data": {
            "weights": [2, 0, 0, 3, 1, 2, 1, 1, 1, 2],
        }
    }
    bins_absolute_ele_dev_BAS = [
        -0.7718245274301169,
        -0.6464835753472811,
        -0.5211426232644452,
        -0.39580167118160936,
        -0.27046071909877345,
        -0.1451197670159376,
        -0.019778814933101796,
        0.10556213714973406,
        0.23090308923256997,
        0.35624404131540577,
    ]
    bins_absolute_ele_dev_APIC = [1.03738723]

    target_trunkBAS = {
        "trunk": {
            "azimuth": {"uniform": {"max": 0.0, "min": np.pi}},
            "orientation_deviation": {"data": {"weights": [4, 3, 1, 2, 0, 1, 0, 0, 0, 2]}},
            "absolute_elevation_deviation": absolute_elevation_deviation_BAS,
            "pia_3d_angles": {
                "data": {
                    "weights": [
                        1.2274214110745432,
                        0.6137107055372726,
                        0.6137107055372716,
                        0.6137107055372716,
                        1.2274214110745432,
                        0.6137107055372716,
                        1.841132116611821,
                        0.0,
                        0.0,
                        1.2274214110745432,
                    ]
                }
            },
            "apical_3d_angles": {
                "data": {
                    "weights": [
                        1.0248077967009541,
                        0.0,
                        1.0248077967009541,
                        2.0496155934019082,
                        0.5124038983504771,
                        1.0248077967009541,
                        0.0,
                        0.0,
                        0.5124038983504771,
                        0.5124038983504771,
                    ]
                }
            },
        }
    }
    target_trunkAPIC = {
        "trunk": {
            "azimuth": {"uniform": {"max": 0.0, "min": np.pi}},
            "orientation_deviation": {"data": {"bins": [0.0], "weights": [2]}},
            "absolute_elevation_deviation": {"data": {"weights": [2]}},
            "pia_3d_angles": {"data": {"weights": [8.9044]}},
        }
    }

    trunkAP = extract_input.from_neurom.trunk_neurite(
        POPUL, neurite_type=neurom.APICAL_DENDRITE, bins=1
    )
    trunkBAS = extract_input.from_neurom.trunk_neurite(POPUL, bins=10)
    trunkNEU = extract_input.from_neurom.trunk_neurite(NEU, bins=10)
    assert "apical_3d_angles" not in trunkNEU

    assert_array_almost_equal(trunkBAS["trunk"]["orientation_deviation"]["data"]["bins"], bins_BAS)
    assert_array_almost_equal(
        trunkBAS["trunk"]["absolute_elevation_deviation"]["data"]["bins"],
        bins_absolute_ele_dev_BAS,
    )
    assert_array_almost_equal(
        trunkAP["trunk"]["absolute_elevation_deviation"]["data"]["bins"],
        bins_absolute_ele_dev_APIC,
    )
    del trunkBAS["trunk"]["orientation_deviation"]["data"]["bins"]
    del trunkBAS["trunk"]["absolute_elevation_deviation"]["data"]["bins"]
    del trunkBAS["trunk"]["pia_3d_angles"]["data"]["bins"]
    del trunkBAS["trunk"]["apical_3d_angles"]["data"]["bins"]
    del trunkAP["trunk"]["absolute_elevation_deviation"]["data"]["bins"]
    del trunkAP["trunk"]["pia_3d_angles"]["data"]["bins"]

    assert_equal(trunkBAS, target_trunkBAS)
    # this value is slightly unstable with python versions
    trunkAP["trunk"]["pia_3d_angles"]["data"]["weights"][0] = np.around(
        trunkAP["trunk"]["pia_3d_angles"]["data"]["weights"][0], 4
    )
    assert_equal(trunkAP, target_trunkAPIC)


def test_diameter_extract(POPUL, NEU):
    res = extract_input.from_diameter.model(NEU)
    assert_equal(set(res.keys()), {"basal_dendrite"})
    expected = {
        "Rall_ratio": 1.5,
        "siblings_ratio": 1.0,
        "taper": [0.24, 0.1],
        "term": [2.0, 2.0],
        "trunk": [3.9],
        "trunk_taper": [0.30],
    }

    assert_equal(set(res["basal_dendrite"]), set(expected))
    for key, value in expected.items():
        assert_array_almost_equal(res["basal_dendrite"][key], value)

    with pytest.raises(NeuroTSError):
        extract_input.from_diameter.model(load_morphologies(os.path.join(_PATH, "simple.swc")))

    # Test on Population
    res = extract_input.from_diameter.model(POPUL)
    assert_equal(set(res.keys()), {"axon", "basal_dendrite", "apical_dendrite"})
    expected = {
        "basal_dendrite": {
            "Rall_ratio": 1.5,
            "siblings_ratio": 1.0,
            "taper": [
                0.003361,
                0.009487,
                0.009931,
                0.016477,
                0.023878,
                0.024852,
                0.027809,
                0.027975,
            ],
            "term": [0.3] * 8,
            "trunk": [0.6, 0.6, 0.72, 0.84, 1.2, 1.5, 1.8, 2.4],
            "trunk_taper": [
                0,
                3.036411e-02,
                3.053287e-02,
                5.059035e-02,
                1.168936e-01,
                1.172027e-01,
                0.15,
                2.121002e-01,
            ],
        },
        "apical_dendrite": {
            "Rall_ratio": 1.5,
            "siblings_ratio": 1.0,
            "taper": [
                0.010331,
                0.02135,
                0.02264,
                0.033914,
                0.035313,
                0.041116,
                0.055751,
                0.056211,
            ],
            "term": [0.3] * 8,
            "trunk": [1.57, 7.51],
            "trunk_taper": [0.05324615, 0.65223652],
        },
        "axon": {
            "Rall_ratio": 1.5,
            "siblings_ratio": 1.0,
            "taper": [
                0.04079,
                0.055286,
                0.092382,
                0.099524,
                0.11986,
                0.140346,
                0.214172,
                0.407058,
            ],
            "term": [0.12] * 8,
            "trunk": [2.1, 3.0],
            "trunk_taper": [0.0435508, 0.0717109],
        },
    }

    for neurite_type in ["basal_dendrite", "apical_dendrite", "axon"]:
        for key in expected[neurite_type]:
            try:
                assert_equal(res[neurite_type].keys(), expected[neurite_type].keys())
                if key in ["taper", "term", "trunk", "trunk_taper"]:
                    tested = sorted(res[neurite_type][key])[:8]
                else:
                    tested = res[neurite_type][key]
                assert_array_almost_equal(tested, expected[neurite_type][key])
            except AssertionError as err:
                raise AssertionError(f"Failed for res[{neurite_type}][{key}]") from err


class TestDistributions:
    """Test distributions."""

    @pytest.fixture
    def filename(self):
        return os.path.join(_PATH, "bio/")

    def test_radial_distances(self, filename):
        distr = extract_input.distributions(filename, feature="radial_distances")
        assert_equal(
            set(distr.keys()), {"soma", "basal_dendrite", "apical_dendrite", "axon", "diameter"}
        )
        distr_legacy = extract_input.distributions(
            filename, feature="radial_distances", neurite_types=["basal", "apical", "axon"]
        )
        assert_equal(
            set(distr_legacy.keys()),
            {"soma", "basal_dendrite", "apical_dendrite", "axon", "diameter"},
        )
        assert_equal(
            distr["basal_dendrite"]["num_trees"],
            {"data": {"bins": [4, 5, 6, 7, 8, 9], "weights": [1, 0, 0, 0, 0, 1]}},
        )
        assert_equal(distr["basal_dendrite"]["filtration_metric"], "radial_distances")

        # Check that the returned distributions are valid according to the JSON schema
        validator.validate_neuron_distribs(distr)

    def test_path_distances(self, filename):
        distr = extract_input.distributions(filename, feature="path_distances")
        assert_equal(distr["basal_dendrite"]["filtration_metric"], "path_distances")
        validator.validate_neuron_distribs(distr)

    def test_threshold_too_small(self):
        with pytest.raises(
            NeuroTSError,
            match=(
                "The given threshold excluded all bars of the persistence diagram, please use a "
                "lower threshold value."
            ),
        ):
            extract_input.distributions(
                os.path.join(_PATH, "diam_simple.swc"),
                feature="path_distances",
                neurite_types=["basal_dendrite"],
            )

    def test_missing_neurite_type(self):
        with pytest.raises(
            NeuroTSError,
            match="The given population does contain any tree of axon type.",
        ):
            extract_input.distributions(
                os.path.join(_PATH, "diam_simple.swc"),
                feature="path_distances",
                neurite_types=["axon"],
            )

    def test_trunk_length(self, filename):
        distr = extract_input.distributions(filename, feature="trunk_length")
        assert "persistence_diagram" not in distr["basal_dendrite"]
        assert "filtration_metric" not in distr["basal_dendrite"]
        validator.validate_neuron_distribs(distr)

    def test_different_features(self, filename):
        # Test with different features for each neurite type
        distr = extract_input.distributions(
            filename,
            feature={
                "apical_dendrite": "radial_distances",
                "basal_dendrite": "trunk_length",
                "axon": "path_distances",
            },
        )
        assert "filtration_metric" not in distr["basal_dendrite"]
        assert distr["apical_dendrite"]["filtration_metric"] == "radial_distances"
        assert distr["axon"]["filtration_metric"] == "path_distances"
        assert "persistence_diagram" not in distr["basal_dendrite"]
        assert "persistence_diagram" in distr["apical_dendrite"]
        assert "persistence_diagram" in distr["axon"]
        validator.validate_neuron_distribs(distr)

    def test_diameter_model_none(self, filename):
        distr = extract_input.distributions(
            filename,
            feature="radial_distances",
            diameter_model=None,
        )
        assert_equal(
            set(distr.keys()), {"soma", "basal_dendrite", "apical_dendrite", "axon", "diameter"}
        )
        validator.validate_neuron_distribs(distr)

    def test_diameter_model_invalid(self, filename):
        with pytest.raises(NotImplementedError):
            extract_input.distributions(
                filename,
                feature="radial_distances",
                diameter_model="invalid",
            )

    def test_diameter_model_M5(self, filename):
        distr_M5 = extract_input.distributions(
            filename, feature="radial_distances", diameter_model="M5"
        )
        assert_equal(
            set(distr_M5.keys()), {"soma", "basal_dendrite", "apical_dendrite", "axon", "diameter"}
        )
        validator.validate_neuron_distribs(distr_M5)

    def test_external_diameter_model(self, filename):
        def diam_method(pop):
            return extract_input.from_diameter.model(pop)

        distr_external = extract_input.distributions(
            filename, feature="radial_distances", diameter_model=diam_method
        )
        assert_equal(
            set(distr_external.keys()),
            {"soma", "basal_dendrite", "apical_dendrite", "axon", "diameter"},
        )
        validator.validate_neuron_distribs(distr_external)

        distr_external_input = extract_input.distributions(
            filename,
            feature="radial_distances",
            diameter_model=diam_method,
            diameter_input_morph=filename,
        )
        assert distr_external == distr_external_input


def test_number_neurites(POPUL):
    res = extract_input.from_neurom.number_neurites(POPUL)
    assert_equal(
        res,
        {"num_trees": {"data": {"bins": [4, 5, 6, 7, 8, 9], "weights": [1, 0, 0, 0, 0, 1]}}},
    )


def test_number_neurites_cut_pop(POPUL):
    neurons = list(POPUL)
    if len(neurons[0].neurites) > len(neurons[1].neurites):
        smallest = 1
        biggest = 0
    else:
        smallest = 0
        biggest = 1

    for i in list(range(2, len(neurons[biggest].root_sections) - 1))[::-1]:
        neurons[biggest].delete_section(neurons[biggest].root_sections[i], recursive=True)

    POPUL = neurom.core.population.Population(neurons)
    assert_equal(len(neurons), 2)
    assert_equal(len(neurons[biggest].neurites), 3)
    assert_equal(len(neurons[smallest].neurites), 6)
    assert_equal(len(list(POPUL.neurites)), 9)
    res_cut = extract_input.from_neurom.number_neurites(POPUL)
    assert_equal(res_cut, {"num_trees": {"data": {"bins": [2, 3, 4], "weights": [1, 0, 1]}}})


def test_parameters():
    params = extract_input.parameters(
        neurite_types=["basal_dendrite", "apical_dendrite"],
        method="tmd",
        feature="radial_distances",
    )
    expected_params = {
        "basal_dendrite": {
            "randomness": 0.24,
            "targeting": 0.14,
            "radius": 0.3,
            "orientation": None,
            "growth_method": "tmd",
            "branching_method": "bio_oriented",
            "modify": None,
            "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
            "tree_type": 3,
            "metric": "radial_distances",
        },
        "apical_dendrite": {
            "randomness": 0.24,
            "targeting": 0.14,
            "radius": 0.3,
            "orientation": [[0.0, 1.0, 0.0]],
            "growth_method": "tmd_apical",
            "branching_method": "directional",
            "modify": None,
            "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
            "tree_type": 4,
            "metric": "radial_distances",
        },
        "axon": {},
        "origin": [0.0, 0.0, 0.0],
        "grow_types": ["basal_dendrite", "apical_dendrite"],
        "diameter_params": {"method": "default", "models": ["simpler"]},
    }
    assert_equal(params, expected_params)

    legacy_params = extract_input.parameters(
        neurite_types=["basal", "apical"],
        method="tmd",
        feature="radial_distances",
    )
    assert_equal(legacy_params, expected_params)

    default_params = extract_input.parameters(method="tmd", feature="radial_distances")
    expected_params["axon"] = {
        "randomness": 0.24,
        "targeting": 0.14,
        "radius": 0.3,
        "orientation": [[0.0, -1.0, 0.0]],
        "growth_method": "tmd",
        "branching_method": "bio_oriented",
        "modify": None,
        "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
        "metric": "radial_distances",
        "tree_type": 2,
    }
    expected_params["grow_types"].append("axon")
    assert_equal(default_params, expected_params)

    validator.validate_neuron_params(params)

    params_path = extract_input.parameters(
        neurite_types=["basal_dendrite", "apical_dendrite"], method="tmd"
    )

    assert_equal(
        params_path,
        {
            "basal_dendrite": {
                "randomness": 0.24,
                "targeting": 0.14,
                "radius": 0.3,
                "orientation": None,
                "growth_method": "tmd",
                "branching_method": "bio_oriented",
                "modify": None,
                "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                "tree_type": 3,
                "metric": "path_distances",
            },
            "apical_dendrite": {
                "randomness": 0.24,
                "targeting": 0.14,
                "radius": 0.3,
                "orientation": [[0.0, 1.0, 0.0]],
                "growth_method": "tmd_apical",
                "branching_method": "directional",
                "modify": None,
                "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                "tree_type": 4,
                "metric": "path_distances",
            },
            "axon": {},
            "origin": [0.0, 0.0, 0.0],
            "grow_types": ["basal_dendrite", "apical_dendrite"],
            "diameter_params": {"method": "default", "models": ["simpler"]},
        },
    )
    validator.validate_neuron_params(params_path)

    params_axon = extract_input.parameters(neurite_types=["axon"], method="tmd")

    assert_equal(
        params_axon,
        {
            "basal_dendrite": {},
            "apical_dendrite": {},
            "axon": {
                "randomness": 0.24,
                "targeting": 0.14,
                "radius": 0.3,
                "orientation": [[0.0, -1.0, 0.0]],
                "growth_method": "tmd",
                "branching_method": "bio_oriented",
                "modify": None,
                "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                "tree_type": 2,
                "metric": "path_distances",
            },
            "origin": [0.0, 0.0, 0.0],
            "grow_types": ["axon"],
            "diameter_params": {"method": "default", "models": ["simpler"]},
        },
    )
    validator.validate_neuron_params(params_axon)

    params_axon = extract_input.parameters(neurite_types=["axon"], method="trunk")

    assert_equal(
        params_axon,
        {
            "basal_dendrite": {},
            "apical_dendrite": {},
            "axon": {
                "randomness": 0.24,
                "targeting": 0.14,
                "radius": 0.3,
                "orientation": [[0.0, -1.0, 0.0]],
                "growth_method": "trunk",
                "branching_method": "random",
                "modify": None,
                "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                "tree_type": 2,
                "metric": "path_distances",
            },
            "origin": [0.0, 0.0, 0.0],
            "grow_types": ["axon"],
            "diameter_params": {"method": "default", "models": ["simpler"]},
        },
    )
    validator.validate_neuron_params(params)

    params_diameter = extract_input.parameters(
        neurite_types=["axon"], method="trunk", diameter_parameters="M1"
    )

    assert_equal(
        params_diameter,
        {
            "basal_dendrite": {},
            "apical_dendrite": {},
            "axon": {
                "randomness": 0.24,
                "targeting": 0.14,
                "radius": 0.3,
                "orientation": [[0.0, -1.0, 0.0]],
                "growth_method": "trunk",
                "branching_method": "random",
                "modify": None,
                "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                "tree_type": 2,
                "metric": "path_distances",
            },
            "origin": [0.0, 0.0, 0.0],
            "grow_types": ["axon"],
            "diameter_params": {"method": "M1"},
        },
    )
    validator.validate_neuron_params(params_diameter)

    params_diameter_dict = extract_input.parameters(
        neurite_types=["axon"],
        method="trunk",
        diameter_parameters={"a": 1, "b": 2},
    )

    assert_equal(
        params_diameter_dict,
        {
            "basal_dendrite": {},
            "apical_dendrite": {},
            "axon": {
                "randomness": 0.24,
                "targeting": 0.14,
                "radius": 0.3,
                "orientation": [[0.0, -1.0, 0.0]],
                "growth_method": "trunk",
                "branching_method": "random",
                "modify": None,
                "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                "tree_type": 2,
                "metric": "path_distances",
            },
            "origin": [0.0, 0.0, 0.0],
            "grow_types": ["axon"],
            "diameter_params": {"method": "external", "a": 1, "b": 2},
        },
    )
    validator.validate_neuron_params(params_diameter_dict)

    with pytest.raises(KeyError):
        extract_input.parameters(
            neurite_types=["axon"],
            method="UNKNOWN METHOD",
        )
    with pytest.raises(ValueError):
        extract_input.parameters(
            neurite_types=["axon"],
            method="trunk",
            diameter_parameters=object(),
        )

    params = extract_input.parameters(neurite_types=["basal_dendrite", "apical_dendrite"])
    assert_equal(
        params,
        {
            "basal_dendrite": {
                "randomness": 0.24,
                "targeting": 0.14,
                "radius": 0.3,
                "orientation": None,
                "growth_method": "tmd",
                "branching_method": "bio_oriented",
                "modify": None,
                "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                "metric": "path_distances",
                "tree_type": 3,
            },
            "apical_dendrite": {
                "randomness": 0.24,
                "targeting": 0.14,
                "radius": 0.3,
                "orientation": [[0.0, 1.0, 0.0]],
                "growth_method": "tmd_apical",
                "branching_method": "directional",
                "modify": None,
                "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                "metric": "path_distances",
                "tree_type": 4,
            },
            "axon": {},
            "origin": [0.0, 0.0, 0.0],
            "grow_types": ["basal_dendrite", "apical_dendrite"],
            "diameter_params": {"method": "default", "models": ["simpler"]},
        },
    )
    validator.validate_neuron_params(params_path)

    extract_input.parameters(
        neurite_types=["axon"],
        method="trunk",
        diameter_parameters={"some_external_diametrizer": None},
    )

    extract_input.parameters(
        neurite_types=["axon"],
        method="trunk",
        diameter_parameters="some_diametrizer",
    )


def test_from_TMD():
    files = sorted([os.path.join(POP_PATH, neuron_dir) for neuron_dir in os.listdir(POP_PATH)])
    pop = tmd.io.load_population(files)
    angles = extract_input.from_TMD.persistent_homology_angles(pop, neurite_type="basal_dendrite")
    expected = [
        [
            [39.8034782, 22.0587348, 0.2204977, -0.0031118, -0.7250693, 0.4353605],
            [47.0833969, 16.8049907, 0.4378265, 0.5057776, -1.4803076, 0.4328786],
            [142.8110504, 0, np.nan, np.nan, np.nan, np.nan],
        ],
        [
            [31.5143489, 13.1089029, -0.0196220, 0.0082083, -0.8850177, 0.0621305],
            [31.6991310, 4.0347867, 0.5645827, -1.2206746, -1.958114, 0.3290293],
            [37.1221504, 0, np.nan, np.nan, np.nan, np.nan],
        ],
        [
            [80.1259918, 45.2574195, 0.5985462, -0.7937724, -1.4556563, 0.2089598],
            [138.8324737, 137.2655334, 0.7664448, -0.5276853, -1.5705068, -0.1490920],
            [129.4999694, 58.3956718, -0.1864954, 0.2471917, -0.1825209, -0.8895693],
            [116.7485580, 29.0435256, 0.1938211, 0.8495636, -0.6798108, -0.3523395],
            [116.3598709, 4.6591954, -0.0381157, -0.5630145, -0.9937219, -0.0060555],
            [140.7718811, 0, np.nan, np.nan, np.nan, np.nan],
        ],
        [
            [108.1560363, 24.4956016, 0.0795795, -0.2466572, -0.818391, 0.4079079],
            [84.4512786, 73.8114471, -0.0682486, -0.1316394, 0.7043639, 0.3319016],
            [41.1267166, 22.6543693, 0.3379619, -0.3496508, 0.2551283, 0.1817587],
            [58.6278800, 55.9588279, 0.1952034, -0.6733589, 0.0355827, 0.2554649],
            [67.1058807, 67.8727340, -0.0696913, -0.1445076, 4.92025, -0.8872188],
            [78.9355468, 16.0958881, -0.3179875, 0.5255199, -1.5740335, -0.2523424],
            [92.3746414, 50.6163444, 0.0482639, 0.1450342, 0.8074381, -0.2487332],
            [88.7393646, 14.1915130, -0.1820048, 0.6027378, 0.7695344, 0.4431591],
            [107.2000274, 13.7320985, 0.4757962, -1.473934, -1.7596798, 1.2384288],
            [157.3328552, 0, np.nan, np.nan, np.nan, np.nan],
        ],
        [
            [124.3847961, 78.5777359, -0.2851194, 0.1851800, 0.7059138, -0.4451136],
            [67.1271133, 46.9302597, -0.0895297, 1.0650232, 6.1442575, -1.1252722],
            [50.9799156, 27.6712512, -5.344535, 0.164577, -0.0902247, 0.6043591],
            [147.5868072, 45.4994354, 0.0477559, -0.3307448, 0.5073497, -0.0292972],
            [125.9251632, 32.7475662, -0.3614119, 0.3678546, -0.4462253, -0.5532181],
            [119.1635360, 18.5245800, -0.0425105, 0.3792363, 0.3548733, -0.3755915],
            [115.0881805, 26.0076904, -0.1438069, -0.4749578, 5.3513756, -1.0207773],
            [44.8667869, 20.1308231, -0.5238513, 0.4554575, -0.3537357, 0.6082043],
            [124.8795852, 9.7746734, 0.1573835, -0.6259746, 0.5335315, 0.3545703],
            [159.7980194, 0, np.nan, np.nan, np.nan, np.nan],
        ],
        [
            [73.5007705, 44.1673202, -0.2861464, 0.6478886, 0.7622488, -0.6312206],
            [187.1019897, 185.1600341, 0.5756854, -0.9131198, 4.854946, -0.0758894],
            [111.3322906, 23.4609394, -1.1881468, 1.4903252, -0.7528698, 0.3027869],
            [110.6484298, 24.8346958, 0.8869759, -0.5435520, 0.1794759, -1.2358185],
            [82.1550140, 12.0827064, 0.5742538, -0.2249454, 4.78082, 0.0218874],
            [187.2543487, 0, np.nan, np.nan, np.nan, np.nan],
        ],
        [
            [128.7404022, 44.2018013, 0.1672787, 0.3934768, 0.4804887, -1.2018781],
            [202.8781890, 18.3915138, -0.4089744, 0.1219186, 5.5452833, 0.4808956],
            [219.8619384, 0, np.nan, np.nan, np.nan, np.nan],
        ],
        [
            [224.0865325, 10.8910417, 0.0639219, -0.2720557, -0.536548, 0.8312207],
            [196.6136322, 2.6748218, -0.5220707, -0.7471831, 3.6071417, 0.5896363],
            [265.9921875, 0, np.nan, np.nan, np.nan, np.nan],
        ],
    ]
    for a, b in zip(angles["persistence_diagram"], expected):
        for ai, bi in zip(a, b):
            assert_array_almost_equal(ai, bi, decimal=6 if not _OLD_NUMPY else 4)

    angles = extract_input.from_TMD.persistent_homology_angles(
        pop, neurite_type="basal_dendrite", threshold=9
    )
    expected = [
        [
            [108.1560363, 24.4956016, 0.0795795, -0.2466572, -0.818391, 0.4079079],
            [84.4512786, 73.8114471, -0.0682486, -0.1316394, 0.7043639, 0.3319016],
            [41.1267166, 22.6543693, 0.3379619, -0.3496508, 0.2551283, 0.1817587],
            [58.6278800, 55.9588279, 0.1952034, -0.6733589, 0.0355827, 0.2554649],
            [67.1058807, 67.8727340, -0.0696913, -0.1445076, 4.92025, -0.8872188],
            [78.9355468, 16.0958881, -0.3179875, 0.5255199, -1.5740335, -0.2523424],
            [92.3746414, 50.6163444, 0.0482639, 0.1450342, 0.8074381, -0.2487332],
            [88.7393646, 14.1915130, -0.1820048, 0.6027378, 0.7695344, 0.4431591],
            [107.2000274, 13.7320985, 0.4757962, -1.473934, -1.7596798, 1.2384288],
            [157.3328552, 0, np.nan, np.nan, np.nan, np.nan],
        ],
        [
            [124.3847961, 78.5777359, -0.2851194, 0.1851800, 0.7059138, -0.4451136],
            [67.1271133, 46.9302597, -0.0895297, 1.0650232, 6.1442575, -1.1252722],
            [50.9799156, 27.6712512, -5.344535, 0.164577, -0.0902247, 0.6043591],
            [147.5868072, 45.4994354, 0.0477559, -0.3307448, 0.5073497, -0.0292972],
            [125.9251632, 32.7475662, -0.3614119, 0.3678546, -0.4462253, -0.5532181],
            [119.1635360, 18.5245800, -0.0425105, 0.3792363, 0.3548733, -0.3755915],
            [115.0881805, 26.0076904, -0.1438069, -0.4749578, 5.3513756, -1.0207773],
            [44.8667869, 20.1308231, -0.5238513, 0.4554575, -0.3537357, 0.6082043],
            [124.8795852, 9.7746734, 0.1573835, -0.6259746, 0.5335315, 0.3545703],
            [159.7980194, 0, np.nan, np.nan, np.nan, np.nan],
        ],
    ]
    for a, b in zip(angles["persistence_diagram"], expected):
        for ai, bi in zip(a, b):
            assert_array_almost_equal(ai, bi, decimal=6 if not _OLD_NUMPY else 5)


def test_trunk_neurite_3d_angles(POPUL):
    all_angles = extract_input.from_neurom.trunk_neurite(POPUL, neurom.APICAL_DENDRITE, bins=10)
    angles = extract_input.from_neurom.trunk_neurite_3d_angles(
        POPUL, neurom.APICAL_DENDRITE, bins=10
    )

    assert all_angles["trunk"]["pia_3d_angles"] == angles["trunk"]["pia_3d_angles"]
    assert_array_almost_equal(
        angles["trunk"]["pia_3d_angles"]["data"]["bins"],
        [
            0.4828722567123299,
            0.49410265776120743,
            0.5053330588100851,
            0.5165634598589626,
            0.5277938609078402,
            0.5390242619567178,
            0.5502546630055953,
            0.5614850640544728,
            0.5727154651033505,
            0.5839458661522281,
        ],
    )
    assert_array_almost_equal(
        angles["trunk"]["pia_3d_angles"]["data"]["weights"],
        [44.52200752438604, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 44.52200752438582],
    )

    angles = extract_input.from_neurom.trunk_neurite(POPUL, neurom.BASAL_DENDRITE, bins=10)
    assert angles["trunk"]["pia_3d_angles"] == {
        "data": {
            "bins": [
                1.2145526099759574,
                1.3398935503066864,
                1.4652344906374157,
                1.590575430968145,
                1.7159163712988743,
                1.8412573116296036,
                1.9665982519603327,
                2.0919391922910617,
                2.217280132621791,
                2.3426210729525203,
            ],
            "weights": [
                1.2274214110745432,
                0.6137107055372726,
                0.6137107055372716,
                0.6137107055372716,
                1.2274214110745432,
                0.6137107055372716,
                1.841132116611821,
                0.0,
                0.0,
                1.2274214110745432,
            ],
        }
    }


def test_transform_distr():
    np.random.seed(42)
    data = np.random.uniform(0, 1, 100)

    ss = neurom.stats.fit(data, distribution="norm")
    res = extract_input.from_neurom.transform_distr(ss)
    assert_equal(res, {"norm": {"mean": 0.47018074337820936, "std": 0.29599822663249037}})

    ss = neurom.stats.fit(data, distribution="uniform")
    res = extract_input.from_neurom.transform_distr(ss)
    assert_equal(res, {"uniform": {"min": 0.005522117123602399, "max": 0.9868869366005173}})

    ss = neurom.stats.fit(data, distribution="expon")
    res = extract_input.from_neurom.transform_distr(ss)
    assert_equal(res, {"expon": {"loc": 0.005522117123602399, "lambda": 2.1521175837421254}})
