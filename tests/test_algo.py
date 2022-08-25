"""Test neurots.generate.section code."""

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
import json
import os

import numpy as np
from numpy.testing import assert_array_almost_equal
from numpy.testing import assert_equal

from neurots.generate.algorithms.basicgrower import TrunkAlgo
from neurots.generate.algorithms.common import TMDStop
from neurots.generate.algorithms.tmdgrower import TMDAlgo
from neurots.generate.algorithms.tmdgrower import TMDApicalAlgo
from neurots.generate.algorithms.tmdgrower import TMDGradientAlgo
from neurots.generate.section import SectionGrowerPath
from neurots.generate.section import SectionGrowerTMD
from neurots.generate.tree import SectionParameters
from neurots.morphmath import sample

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _setup_test(Algo, Grower, custom_parameters=None):
    with open(os.path.join(_PATH, "dummy_distribution.json"), encoding="utf-8") as f:
        distributions = json.load(f)["basal_dendrite"]

    with open(os.path.join(_PATH, "dummy_params.json"), encoding="utf-8") as f:
        parameters = json.load(f)["basal_dendrite"]
    parameters["bias_length"] = 0.5
    parameters["bias"] = 0.5
    parameters["has_apical_tuft"] = True

    if custom_parameters is not None:
        parameters.update(custom_parameters)

    np.random.seed(42)
    algo = Algo(distributions, parameters, [0, 0, 1])
    seg_len = sample.Distr(parameters["step_size"])

    section_parameters = SectionParameters(
        randomness=0.2, targeting=0.3, history=1.0 - 0.2 - 0.3, scale_prob=1.0
    )

    grower = Grower(
        parent=None,
        children=None,
        first_point=[1.1, 0.0, 0.0],
        direction=[0.57735, 0.57735, 0.57735],
        parameters=section_parameters,
        process="major",
        stop_criteria={"TMD": TMDStop(bif_id=1, bif=9.7747, term_id=0, term=159.798, ref=0.0)},
        step_size_distribution=seg_len,
        pathlength=0.0,
    )

    return algo, grower


def _assert_dict_or_array(dict1, dict2):
    assert_equal(set(dict1.keys()), set(dict2.keys()))
    for key in dict1.keys():
        if isinstance(dict1[key], np.ndarray):
            assert_array_almost_equal(dict1[key], dict2[key])
        elif isinstance(dict1[key], dict):
            _assert_dict_or_array(dict1[key], dict2[key])
        else:
            assert_equal(dict1[key], dict2[key], f"Error for key: {key}")


def test_TrunkAlgo():
    np.random.seed(0)
    custom_parameters = {
        "num_seg": 10,
        "branching_method": "random",
    }
    algo, grower = _setup_test(TrunkAlgo, SectionGrowerPath, custom_parameters)

    stop, num_sec = algo.initialize()
    assert stop == {"num_seg": 10}
    assert_equal(num_sec, 1)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(
        s1,
        {
            "direction": [-0.30524033, 0.30700944, 0.90142861],
            "process": "major",
            "first_point": [1.1, 0.0, 0.0],
            "stop": {"TMD": TMDStop(bif_id=1, bif=9.7747, term_id=0, term=159.798, ref=0.0)},
        },
    )

    _assert_dict_or_array(
        s2,
        {
            "direction": [-0.11067468, -0.97407245, 0.19731697],
            "process": "major",
            "first_point": [1.1, 0.0, 0.0],
            "stop": {"TMD": TMDStop(bif_id=1, bif=9.7747, term_id=0, term=159.798, ref=0.0)},
        },
    )


def test_TMDAlgo():
    algo, grower = _setup_test(TMDAlgo, SectionGrowerPath)

    stop, num_sec = algo.initialize()
    assert stop == {"TMD": TMDStop(bif_id=1, bif=9.7747, term_id=0, term=159.798, ref=0.0)}
    assert_equal(num_sec, 10)
    assert_equal(grower.get_val(), 0)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(
        s1,
        {
            "direction": [0.0, 0.0, 0.0],
            "process": "major",
            "first_point": [1.1, 0.0, 0.0],
            "stop": {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=0, term=159.798, ref=0.0)},
        },
    )

    _assert_dict_or_array(
        s2,
        {
            "direction": [0.0, 0.0, 0.0],
            "process": "major",
            "first_point": [1.1, 0.0, 0.0],
            "stop": {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=1, term=124.8796, ref=0.0)},
        },
    )

    algo, grower = _setup_test(TMDAlgo, SectionGrowerTMD)

    stop, num_sec = algo.initialize()
    assert stop == {"TMD": TMDStop(bif_id=1, bif=9.7747, term_id=0, term=159.798, ref=0.0)}
    assert_equal(num_sec, 10)
    assert_equal(grower.get_val(), 1.1)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(
        s1,
        {
            "direction": [0.0, 0.0, 0.0],
            "process": "major",
            "first_point": [1.1, 0.0, 0.0],
            "stop": {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=0, term=159.798, ref=0.0)},
        },
    )

    _assert_dict_or_array(
        s2,
        {
            "direction": [0.0, 0.0, 0.0],
            "process": "major",
            "first_point": [1.1, 0.0, 0.0],
            "stop": {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=1, term=124.8796, ref=0.0)},
        },
    )


def test_TMDAlgo_modify():
    def tmd_scale(barcode, thickness):
        # only the two first points of each bar are modified
        # because they correspond to spatial dimensions
        scaling_factor = np.ones(len(barcode[0]), dtype=float)
        scaling_factor[:2] = thickness
        return np.multiply(barcode, scaling_factor).tolist()

    def modify_barcode(ph, context, thickness=1150.0, thickness_reference=1150.0):
        # pylint: disable=unused-argument
        max_p = np.max(ph)
        scaling_reference = 1.0
        if 1 - max_p / thickness_reference < 0:  # If cell is larger than the layers
            scaling_reference = thickness_reference / max_p
        return tmd_scale(ph, scaling_reference * thickness / thickness_reference)

    custom_parameters = {
        "modify": {
            "funct": modify_barcode,
            "kwargs": {"thickness": 100, "thickness_reference": 1000},
        }
    }

    algo, grower = _setup_test(TMDAlgo, SectionGrowerPath, custom_parameters)

    stop, num_sec = algo.initialize()
    assert stop == {"TMD": TMDStop(bif_id=1, bif=0.9775, term_id=0, term=15.9798, ref=0.0)}
    assert_equal(num_sec, 10)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(
        s1,
        {
            "direction": [0.0, 0.0, 0.0],
            "process": "major",
            "first_point": [1.1, 0.0, 0.0],
            "stop": {"TMD": TMDStop(bif_id=2, bif=1.8525, term_id=0, term=159.798, ref=0.0)},
        },
    )

    _assert_dict_or_array(
        s2,
        {
            "direction": [0.0, 0.0, 0.0],
            "process": "major",
            "first_point": [1.1, 0.0, 0.0],
            "stop": {"TMD": TMDStop(bif_id=2, bif=1.8525, term_id=1, term=12.488, ref=0.0)},
        },
    )


def test_TMDApicalAlgo():
    algo, grower = _setup_test(TMDApicalAlgo, SectionGrowerPath)

    stop, num_sec = algo.initialize()
    expected_stop = {"TMD": TMDStop(bif_id=1, bif=9.7747, term_id=0, term=159.798, ref=0.0)}
    assert stop == expected_stop
    assert_equal(num_sec, 10)

    grower.id = 1
    s1, s2 = algo.bifurcate(grower)
    assert_equal(algo.apical_section, 1)
    _assert_dict_or_array(
        s1,
        {
            "direction": [0.57735, 0.57735, 0.57735],
            "process": "major",
            "first_point": [1.1, 0.0, 0.0],
            "stop": {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=0, term=159.798, ref=0.0)},
        },
    )

    _assert_dict_or_array(
        s2,
        {
            "direction": np.array([0.20348076, 0.54109933, 0.81597003]),
            "process": "secondary",
            "first_point": [1.1, 0.0, 0.0],
            "stop": {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=1, term=124.8796, ref=0.0)},
        },
    )

    grower.stop_criteria["TMD"].bif_id = 2
    grower.stop_criteria["TMD"].bif = 18.5246
    grower.points[-1] *= 2
    grower.id = 2
    algo.bifurcate(grower)
    assert_equal(algo.apical_section, 2)

    # Find last bifurcation in secondary branch
    algo, grower = _setup_test(TMDApicalAlgo, SectionGrowerPath)
    grower.pathlength = 9999
    grower.process = "secondary"
    stop, num_sec = algo.initialize()
    grower.id = 3
    s1, s2 = algo.bifurcate(grower)
    assert_equal(algo.apical_section, 3)

    grower.stop_criteria["TMD"].bif_id = 2
    grower.stop_criteria["TMD"].bif = 18.5246
    grower.points[-1] *= 2
    grower.id = 4
    algo.bifurcate(grower)
    # This time the apical section was not updated
    assert_equal(algo.apical_section, 3)


def test_TMDGradientAlgo():
    algo, grower = _setup_test(TMDGradientAlgo, SectionGrowerPath)

    stop, num_sec = algo.initialize()
    expected_stop = {"TMD": TMDStop(bif_id=1, bif=9.7747, term_id=0, term=159.798, ref=0.0)}
    assert stop == expected_stop
    assert_equal(num_sec, 10)

    s1, s2 = algo.bifurcate(grower)
    _assert_dict_or_array(
        s1,
        {
            "direction": [0.57735, 0.57735, 0.57735],
            "process": "major",
            "first_point": [1.1, 0.0, 0.0],
            "stop": {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=0, term=159.798, ref=0.0)},
        },
    )

    _assert_dict_or_array(
        s2,
        {
            "direction": np.array([0.400454, 0.573604, 0.714573]),
            "process": "major",
            "first_point": [1.1, 0.0, 0.0],
            "stop": {"TMD": TMDStop(bif_id=2, bif=18.5246, term_id=1, term=124.8796, ref=0.0)},
        },
    )
