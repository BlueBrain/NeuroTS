"""Test tree generation."""

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
# pylint: disable=protected-access
import json
import os

import numpy as np
import pytest
from numpy import testing as npt

from neurots import NeuronGrower
from neurots.generate.tree import TreeGrower
from neurots.generate.tree import _create_section_parameters
from neurots.utils import NeuroTSError

_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def test_create_section_parameters__normal_input():
    input_dict = {"randomness": 0.3, "targeting": 0.6}

    parameters = _create_section_parameters(input_dict)

    npt.assert_almost_equal(parameters.randomness, 0.3)
    npt.assert_almost_equal(parameters.targeting, 0.6)
    npt.assert_almost_equal(parameters.history, 1.0 - 0.6 - 0.3)


def test_create_section_parameters__exceed_bounds():
    input_dict = {"randomness": 1.1, "targeting": -0.1}
    parameters = _create_section_parameters(input_dict)

    npt.assert_almost_equal(parameters.randomness, 1.0)
    npt.assert_almost_equal(parameters.targeting, 0.0)
    npt.assert_almost_equal(parameters.history, 0.0)

    input_dict = {"randomness": -0.1, "targeting": 1.0}
    parameters = _create_section_parameters(input_dict)

    npt.assert_almost_equal(parameters.randomness, 0.0)
    npt.assert_almost_equal(parameters.targeting, 1.0)
    npt.assert_almost_equal(parameters.history, 0.0)


def test_create_section_parameters__sum_to_one_error():
    input_dict = {"randomness": 2.0, "targeting": 2.0}

    with pytest.raises(NeuroTSError):
        _create_section_parameters(input_dict)


def test_TreeGrower():
    np.random.seed(0)
    with open(os.path.join(_path, "bio_distribution.json"), encoding="utf-8") as f:
        distributions = json.load(f)

    with open(os.path.join(_path, "bio_path_params.json"), encoding="utf-8") as f:
        params = json.load(f)

    grower = NeuronGrower(input_distributions=distributions, input_parameters=params)
    grower._grow_soma()

    # Test order_per_process()
    sections = [i.active_sections[0] for i in grower.active_neurites]
    for num, i in enumerate(sections):
        i.process = str(len(sections) - num - 1)
    res = TreeGrower.order_per_process(sections)
    for num, i in enumerate(res):
        assert i == sections[len(sections) - num - 1], (
            i,
            sections[len(sections) - num - 1],
        )


def test_TreeGrower_3d_angles():
    np.random.seed(0)
    with open(os.path.join(_path, "bio_distribution_3d_angles.json"), encoding="utf-8") as f:
        distributions = json.load(f)

    with open(os.path.join(_path, "bio_parameters_3d_angles.json"), encoding="utf-8") as f:
        params = json.load(f)

    grower = NeuronGrower(input_distributions=distributions, input_parameters=params)
    grower._grow_soma()

    # Test order_per_process()
    sections = [i.active_sections[0] for i in grower.active_neurites]
    for num, i in enumerate(sections):
        i.process = str(len(sections) - num - 1)
    res = TreeGrower.order_per_process(sections)
    for num, i in enumerate(res):
        assert i == sections[len(sections) - num - 1], (
            i,
            sections[len(sections) - num - 1],
        )
