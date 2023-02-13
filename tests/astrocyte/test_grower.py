"""Test neurots.astrocyte.grower code."""

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

import json
from pathlib import Path

import numpy as np
import pytest
from morph_tool import diff
from numpy import testing as npt

from neurots.astrocyte.grower import AstrocyteGrower

_path = Path(__file__).parent / "data"


def _parameters():
    return {
        "basal": {
            "metric": "path_distances",
            "randomness": 0.0,
            "targeting": 0.2,
            "radius": 0.3,
            "orientation": None,
            "growth_method": "tmd_space_colonization",
            "branching_method": "bio_oriented",
            "modify": None,
            "tree_type": 3,
            "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
            "modify_target": None,
            "barcode_scaling": False,
        },
        "axon": {
            "metric": "path_distances",
            "randomness": 0.0,
            "targeting": 0.2,
            "radius": 0.3,
            "target_ids": [0, 1],
            "growth_method": "tmd_space_colonization_target",
            "branching_method": "bio_oriented",
            "modify": None,
            "tree_type": 2,
            "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
            "modify_target": None,
            "barcode_scaling": False,
            "bias": 0.9,
        },
        "apical": {
            "metric": "path_distances",
            "randomness": 0.0,
            "targeting": 0.2,
            "radius": 0.3,
            "orientation": [[1.0, 0.0, 0.0], [0.1, 0.1, 0.1]],
            "growth_method": "tmd_space_colonization",
            "branching_method": "bio_oriented",
            "modify": None,
            "tree_type": 4,
            "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
            "modify_target": None,
            "barcode_scaling": False,
        },
        "origin": [0.0, 0.0, 0.0],
        "grow_types": ["basal", "axon", "apical"],
        "diameter_params": {"method": "default"},
    }


def _distributions():
    path = _path / "bio_path_distribution.json"
    with open(path, "r", encoding="utf-8") as f:
        distributions = json.load(f)
    return distributions


def _context():
    return {
        "field": {"type": "logit", "slope": 0.11832134, "intercept": 0.36720545},
        "collision_handle": lambda *args: False,
        "space_colonization": {
            "point_cloud": np.array(
                [
                    [0.5488135, 0.71518937, 0.60276338],
                    [0.54488318, 0.4236548, 0.64589411],
                    [0.43758721, 0.891773, 0.96366276],
                    [0.38344152, 0.79172504, 0.52889492],
                    [0.56804456, 0.92559664, 0.07103606],
                    [0.0871293, 0.0202184, 0.83261985],
                    [0.77815675, 0.87001215, 0.97861834],
                    [0.79915856, 0.46147936, 0.78052918],
                    [0.11827443, 0.63992102, 0.14335329],
                    [0.94466892, 0.52184832, 0.41466194],
                    [0.26455561, 0.77423369, 0.45615033],
                    [0.56843395, 0.0187898, 0.6176355],
                    [0.61209572, 0.616934, 0.94374808],
                    [0.6818203, 0.3595079, 0.43703195],
                    [0.6976312, 0.06022547, 0.66676672],
                    [0.67063787, 0.21038256, 0.1289263],
                    [0.31542835, 0.36371077, 0.57019677],
                    [0.43860151, 0.98837384, 0.10204481],
                    [0.20887676, 0.16130952, 0.65310833],
                    [0.2532916, 0.46631077, 0.24442559],
                    [0.15896958, 0.11037514, 0.65632959],
                    [0.13818295, 0.19658236, 0.36872517],
                    [0.82099323, 0.09710128, 0.83794491],
                    [0.09609841, 0.97645947, 0.4686512],
                    [0.97676109, 0.60484552, 0.73926358],
                    [0.03918779, 0.28280696, 0.12019656],
                    [0.2961402, 0.11872772, 0.31798318],
                    [0.41426299, 0.0641475, 0.69247212],
                    [0.56660145, 0.26538949, 0.52324805],
                    [0.09394051, 0.5759465, 0.9292962],
                    [0.31856895, 0.66741038, 0.13179786],
                    [0.7163272, 0.28940609, 0.18319136],
                    [0.58651293, 0.02010755, 0.82894003],
                    [0.00469548, 0.67781654, 0.27000797],
                    [0.73519402, 0.96218855, 0.24875314],
                    [0.57615733, 0.59204193, 0.57225191],
                    [0.22308163, 0.95274901, 0.44712538],
                    [0.84640867, 0.69947928, 0.29743695],
                    [0.81379782, 0.39650574, 0.8811032],
                    [0.58127287, 0.88173536, 0.69253159],
                    [0.72525428, 0.50132438, 0.95608363],
                    [0.6439902, 0.42385505, 0.60639321],
                    [0.0191932, 0.30157482, 0.66017354],
                    [0.29007761, 0.61801543, 0.4287687],
                    [0.13547406, 0.29828233, 0.56996491],
                    [0.59087276, 0.57432525, 0.65320082],
                    [0.65210327, 0.43141844, 0.8965466],
                    [0.36756187, 0.43586493, 0.89192336],
                    [0.80619399, 0.70388858, 0.10022689],
                    [0.91948261, 0.7142413, 0.99884701],
                    [0.1494483, 0.86812606, 0.16249293],
                    [0.61555956, 0.12381998, 0.84800823],
                    [0.80731896, 0.56910074, 0.4071833],
                    [0.069167, 0.69742877, 0.45354268],
                    [0.7220556, 0.86638233, 0.97552151],
                    [0.85580334, 0.01171408, 0.35997806],
                    [0.72999056, 0.17162968, 0.52103661],
                    [0.05433799, 0.19999652, 0.01852179],
                    [0.7936977, 0.22392469, 0.34535168],
                    [0.92808129, 0.7044144, 0.03183893],
                    [0.16469416, 0.6214784, 0.57722859],
                    [0.23789282, 0.934214, 0.61396596],
                    [0.5356328, 0.58990998, 0.73012203],
                    [0.311945, 0.39822106, 0.20984375],
                    [0.18619301, 0.94437239, 0.7395508],
                    [0.49045881, 0.22741463, 0.25435648],
                    [0.05802916, 0.43441663, 0.31179588],
                    [0.69634349, 0.37775184, 0.17960368],
                    [0.02467873, 0.06724963, 0.67939277],
                    [0.45369684, 0.53657921, 0.89667129],
                    [0.99033895, 0.21689698, 0.6630782],
                    [0.26332238, 0.020651, 0.75837865],
                    [0.32001715, 0.38346389, 0.58831711],
                    [0.83104846, 0.62898184, 0.87265066],
                    [0.27354203, 0.79804683, 0.18563594],
                    [0.95279166, 0.68748828, 0.21550768],
                    [0.94737059, 0.73085581, 0.25394164],
                    [0.21331198, 0.51820071, 0.02566272],
                    [0.20747008, 0.42468547, 0.37416998],
                    [0.46357542, 0.27762871, 0.58678435],
                    [0.86385561, 0.11753186, 0.51737911],
                    [0.13206811, 0.71685968, 0.3960597],
                    [0.56542131, 0.18327984, 0.14484776],
                    [0.48805628, 0.35561274, 0.94043195],
                    [0.76532525, 0.74866362, 0.90371974],
                    [0.08342244, 0.55219247, 0.58447607],
                    [0.96193638, 0.29214753, 0.24082878],
                    [0.10029394, 0.01642963, 0.92952932],
                    [0.66991655, 0.78515291, 0.28173011],
                    [0.58641017, 0.06395527, 0.4856276],
                    [0.97749514, 0.87650525, 0.33815895],
                    [0.96157015, 0.23170163, 0.94931882],
                    [0.9413777, 0.79920259, 0.63044794],
                    [0.87428797, 0.29302028, 0.84894356],
                    [0.61787669, 0.01323686, 0.34723352],
                    [0.14814086, 0.98182939, 0.47837031],
                    [0.49739137, 0.63947252, 0.36858461],
                    [0.13690027, 0.82211773, 0.18984791],
                    [0.51131898, 0.22431703, 0.09784448],
                    [0.86219152, 0.97291949, 0.96083466],
                ],
            ),
            "kill_distance_factor": 15.0,
            "influence_distance_factor": 25.0,
        },
        "endfeet_targets": [[0.5, 0.5, 0.5], [1.0, 0.0, 1.0]],
    }


def _global_rng():
    np.random.seed(0)
    return np.random


def _legacy_rng():
    # pylint: disable=protected-access
    mt = np.random.MT19937()
    mt._legacy_seeding(0)  # Use legacy seeding to get the same result as with np.random.seed()
    return np.random.RandomState(mt)


def _check_neurots_soma(soma):
    expected_points = np.array(
        [
            [-5.760930017396721, 14.022942101967232, -1.909993715025774],
            [-8.776987059455903, -3.6071655668748166, 11.979480580641654],
            [5.277860312875229, -2.2110910286946135, 14.164513390631141],
            [-5.5573577403571255, 13.780668646687944, -3.560228284808043],
            [8.818575915415094, 8.819907456966908, 8.831811076714088],
            [10.800253467208064, 0.0, 10.802924714483499],
            [15.279949720206192, 0.0, 0.0],
            [8.818575915415094, 8.819907456966908, 8.831811076714088],
        ]
    )

    npt.assert_allclose(soma.points, expected_points, atol=1e-6, rtol=1e-6)
    npt.assert_equal(soma.radius, 15.279949720206192)


_default_cos = np.cos
_default_arccos = np.arccos


def _rounded_cos(x):
    return np.round(_default_cos(x), 3)


def _rounded_arccos(x):
    return np.round(_default_arccos(x), 3)


@pytest.mark.parametrize(
    "rng_type",
    [
        pytest.param("global", id="Use global numpy random seed"),
        pytest.param("legacy", id="Use RNG instance with legacy constructor"),
    ],
)
def test_grow__run(rng_type, monkeypatch):
    """Test the astrocyte grower."""
    parameters = _parameters()
    distributions = _distributions()

    context = _context()

    if rng_type == "global":
        rng = _global_rng()
    elif rng_type == "legacy":
        rng = _legacy_rng()
    else:
        raise ValueError("Bad rng_type")

    # In this test all the cos and arccos values are rounded because np.cos and np.arccos
    # functions can return different value, depending on the system libraries used to actually
    # compute these values.
    monkeypatch.setattr(np, "cos", _rounded_cos)
    monkeypatch.setattr(np, "arccos", _rounded_arccos)

    astro_grower = AstrocyteGrower(
        input_distributions=distributions,
        input_parameters=parameters,
        context=context,
        rng_or_seed=rng,
    )
    astro_grower.grow()

    _check_neurots_soma(astro_grower.soma_grower.soma)

    difference = diff(astro_grower.neuron, _path / "astrocyte.h5")
    assert not difference, difference.info
