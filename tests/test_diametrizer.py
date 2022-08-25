"""Test neurots.generate.diametrizer code."""

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
# pylint: disable=no-member
# pylint: disable=redefined-outer-name
import copy
import os

import morphio
import numpy as np
import pytest
from morphio import SectionType
from numpy.testing import assert_array_almost_equal
from numpy.testing import assert_equal

from neurots.generate import diametrizer

_path = os.path.dirname(os.path.abspath(__file__))
NEU_PATH1 = os.path.join(_path, "../test_data/diam_simple.swc")
NEU_PATH2 = os.path.join(_path, "../test_data/simple.swc")
NEU_PATH3 = os.path.join(_path, "../test_data/diam_simple_axon.swc")

MODEL = {
    "basal_dendrite": {
        "Rall_ratio": 2.0 / 3.0,
        "siblings_ratio": 1.0,
        "taper": [0.1],
        "term": [0.6],
        "trunk": [4.0, 3.0],
        "trunk_taper": [0.6],
    },
    "axon": {
        "Rall_ratio": 2.0 / 3.0,
        "siblings_ratio": 1.0,
        "taper": [0.1],
        "term": [0.6],
        "trunk": [4.0, 3.0],
        "trunk_taper": [0.6],
    },
}


@pytest.fixture
def neu1():
    return morphio.mut.Morphology(NEU_PATH1)


@pytest.fixture
def neu2():
    return morphio.mut.Morphology(NEU_PATH2)


@pytest.fixture
def neu3():
    return morphio.mut.Morphology(NEU_PATH3)


def test_sample():
    assert diametrizer.sample([0.0]) == 0.0
    np.random.seed(0)
    assert diametrizer.sample([1.0, 1.0, 1.0, 2.0, 2.0, 3.0]) == 2.0


def test_bifurcator():
    d1 = diametrizer.bifurcator(1.0, 2.0, 3.0 / 2.0, 1.0)
    assert d1 == 0.6299605249474366
    d1 = diametrizer.bifurcator(1.0, 2.0, 1.0, 1.0)
    assert d1 == 0.5
    d1 = diametrizer.bifurcator(1.0, 2.0, 1.0, 0.5)
    assert d1 == 0.6666666666666666


def test_taper_section_diam_from_root(neu1):
    section = neu1.root_sections[0]

    diametrizer.taper_section_diam_from_root(section, 4.0, 0.6, 0.07, 100.0)

    assert_array_almost_equal(section.diameters, [4.0, 3.9, 3.8, 3.7, 3.6, 3.5, 3.4])

    section1 = section.children[0]
    diametrizer.taper_section_diam_from_root(section1, 4.0, 0.5, 0.07, 100.0)
    assert_array_almost_equal(section1.diameters, [4.0, 4.0, 3.9, 3.8, 3.7, 3.6])

    section2 = section.children[0]
    diametrizer.taper_section_diam_from_root(section2, 4.0, 0.5, 99, 100.0)
    assert_array_almost_equal(section2.diameters, [4, 99, 99, 99, 99, 99])


def test_taper_section_diam_from_tips(neu1):
    section = neu1.root_sections[0]

    diametrizer.taper_section_diam_from_tips(section, 4.0, 0.6, 0.07, 100.0)

    assert_array_almost_equal(section.diameters, [4.6, 4.5, 4.4, 4.3, 4.2, 4.1, 4.0])

    section1 = section.children[0]
    diametrizer.taper_section_diam_from_tips(section1, 4.0, 0.5, 0.07, 100.0)
    assert_array_almost_equal(section1.diameters, [4.5, 4.4, 4.3, 4.2, 4.1, 4.0])

    section2 = section.children[0]
    diametrizer.taper_section_diam_from_tips(section2, 4.0, 0.5, 99, 99.2)
    assert_array_almost_equal(section2.diameters, [99.2, 99.2, 99.2, 99.1, 99, 4.0], decimal=5)


def test_diametrize_constant_per_section(neu2):
    diametrizer.diametrize_constant_per_section(neu2)
    assert_array_almost_equal(
        morphio.Morphology(neu2).diameters,
        [2.0, 2.0, 2.5, 2.5, 2.5, 2.5, 2.0, 2.0, 3.0, 3.0, 3.0, 3.0],
    )


def test_diametrize_constant_per_neurite(neu2):
    diametrizer.diametrize_constant_per_neurite(neu2)
    assert_array_almost_equal(
        morphio.Morphology(neu2).diameters,
        [
            2.333333,
            2.333333,
            2.333333,
            2.333333,
            2.333333,
            2.333333,
            2.666667,
            2.666667,
            2.666667,
            2.666667,
            2.666667,
            2.666667,
        ],
    )


def test_diametrize_smoothing(neu1):
    diametrizer.diametrize_smoothing(neu1)
    assert_array_almost_equal(
        morphio.Morphology(neu1).diameters,
        [
            4.0,
            3.9,
            3.8,
            3.7,
            3.6,
            3.5,
            3.4,
            2.8,
            2.8,
            2.704,
            2.608,
            2.512,
            2.416,
            2.8,
            2.8,
            2.76,
            2.72,
            2.68,
            2.64,
        ],
    )


def test_diametrize_from_root(neu1):
    np.random.seed(0)  # ensure constant random number for sampling
    diametrizer.diametrize_from_root(neu1, model_params=MODEL)
    assert_array_almost_equal(
        morphio.Morphology(neu1).diameters,
        [
            4.0,
            3.9,
            3.8,
            3.7,
            3.6,
            3.5,
            3.4,
            3.4,
            1.202082,
            1.182082,
            1.162082,
            1.142082,
            1.122082,
            3.4,
            1.202082,
            1.182082,
            1.162082,
            1.142082,
            1.122082,
        ],
    )


def test_diametrize_from_root_axon(neu3):
    np.random.seed(0)  # ensure constant random number for sampling
    diametrizer.diametrize_from_root(neu3, SectionType.axon, model_params=MODEL)
    assert_array_almost_equal(
        morphio.Morphology(neu3).diameters,
        [
            4.0,
            3.8,
            3.6,
            3.4,
            3.2,
            3.0,
            2.8,
            2.8,
            2.8,
            2.6,
            2.4,
            2.2,
            2.0,
            2.8,
            2.0,
            2.4,
            2.0,
            2.2,
            2.0,
            4.0,
            3.9142857,
            3.8285713,
            3.7428572,
            3.6571429,
            3.5714285,
            3.4857142,
            3.4,
        ],
    )


def test_diametrize_from_tips(neu1):
    np.random.seed(0)  # ensure constant random number for sampling
    diametrizer.diametrize_from_tips(neu1, model_params=MODEL)
    assert_array_almost_equal(
        morphio.Morphology(neu1).diameters,
        [
            2.52333,
            2.423331,
            2.32333,
            2.22333,
            2.12333,
            2.02333,
            1.92333,
            1.92333,
            0.68,
            0.66,
            0.64,
            0.62,
            0.6,
            1.92333,
            0.68,
            0.66,
            0.64,
            0.62,
            0.6,
        ],
    )


def test_diametrize_from_tips_axon(neu3):
    np.random.seed(0)  # ensure constant random number for sampling
    diametrizer.diametrize_from_tips(neu3, model_params=MODEL, neurite_type=SectionType.axon)
    assert_array_almost_equal(
        morphio.Morphology(neu3).diameters,
        [
            4.0,
            3.8,
            3.6,
            3.4,
            3.2,
            3.0,
            2.8,
            2.8,
            2.8,
            2.6,
            2.4,
            2.2,
            2.0,
            2.8,
            2.0,
            2.4,
            2.0,
            2.2,
            2.0,
            1.2,
            1.1142857,
            1.0285715,
            0.94285715,
            0.85714287,
            0.7714286,
            0.6857143,
            0.6,
        ],
    )


def test_redefine_diameter_section(neu1):
    section = neu1.root_sections[0]
    assert_equal(section.diameters[0], 4)
    diametrizer.redefine_diameter_section(section, 0, 999)
    assert_equal(section.diameters[0], 999)

    section.points = np.array([[0, 1, 2]])
    with pytest.raises(Exception):
        diametrizer.redefine_diameter_section(section, 1, 2)


def test_build_M1(neu1):
    diametrizer.build(neu1, diam_method="M1")
    diameters = [i.diameters for i in neu1.sections.values()]
    assert_array_almost_equal(diameters[0], [2.7368422] * 7)
    assert_array_almost_equal(diameters[1], diameters[2])
    assert_array_almost_equal(diameters[2], [2.7368422] * 6)


def test_build_M2(neu1):
    diametrizer.build(neu1, diam_method="M2")
    diameters = [i.diameters for i in neu1.sections.values()]
    assert_array_almost_equal(diameters[0], [3.4] * 7)
    assert_array_almost_equal(diameters[1], [2.4666667] * 6)
    assert_array_almost_equal(diameters[2], [2.2333333] * 6)


def test_build_M3(neu1):
    diametrizer.build(neu1, diam_method="M3")
    diameters = [i.diameters for i in neu1.sections.values()]
    assert_array_almost_equal(diameters[0], [4, 3.9, 3.8, 3.7, 3.6, 3.5, 3.4])
    assert_array_almost_equal(diameters[1], [2.8, 2.8, 2.704, 2.608, 2.512, 2.416])
    assert_array_almost_equal(diameters[2], [2.8, 2.8, 2.76, 2.72, 2.68, 2.64])


def test_build_M4(neu1):
    np.random.seed(1)  # ensure constant random number for sampling
    diametrizer.build(neu1, input_model=MODEL, diam_method="M4")
    diameters = [i.diameters for i in neu1.sections.values()]
    assert_array_almost_equal(diameters[0], [3, 2.9, 2.8, 2.7, 2.6, 2.5, 2.4])
    assert_array_almost_equal(diameters[1], diameters[2])
    assert_array_almost_equal(
        diameters[2], [2.4, 0.84852815, 0.82852817, 0.8085281, 0.78852814, 0.76852816]
    )


def test_build_M5(neu1):
    np.random.seed(0)  # ensure constant random number for sampling
    diametrizer.build(neu1, input_model=MODEL, diam_method="M5")
    diameters = [i.diameters for i in neu1.sections.values()]
    assert_array_almost_equal(
        diameters[0],
        [2.5233305, 2.4233305, 2.3233304, 2.2233305, 2.1233304, 2.0233305, 1.923330],
    )
    assert_array_almost_equal(diameters[1], diameters[2])
    assert_array_almost_equal(diameters[2], [1.9233304, 0.68, 0.66, 0.64, 0.62, 0.6])


def test_build_diam_method(neu1):
    def diam_method(neuron, tree_type, **kwargs):
        # pylint: disable=unused-argument
        diametrizer.diametrize_constant_per_neurite(neuron)

    diametrizer.build(neu1, diam_method=diam_method)
    diameters = [i.diameters for i in neu1.sections.values()]
    assert_array_almost_equal(
        diameters[0],
        [2.7368424, 2.7368424, 2.7368424, 2.7368424, 2.7368424, 2.7368424, 2.7368424],
    )
    assert_array_almost_equal(diameters[1], diameters[2])
    assert_array_almost_equal(
        diameters[2], [2.7368424, 2.7368424, 2.7368424, 2.7368424, 2.7368424, 2.7368424]
    )


def test_build_M1_basal_axon(neu2):
    diametrizer.build(neu2, diam_method="M1", neurite_types=["basal_dendrite", "axon"])
    diameters = [i.diameters for i in neu2.sections.values()]
    assert_array_almost_equal(diameters[0], [2.3333333, 2.3333333])
    assert_array_almost_equal(diameters[1], diameters[2])
    assert_array_almost_equal(diameters[3], [2.6666667, 2.6666667])
    assert_array_almost_equal(diameters[3], diameters[4])
    assert_array_almost_equal(diameters[4], diameters[5])


def test_build_M1_axon(neu2):
    diametrizer.build(neu2, diam_method="M1", neurite_types=["axon"])
    diameters = [i.diameters for i in neu2.sections.values()]
    assert_array_almost_equal(diameters[0], [2.0, 2.0])
    assert_array_almost_equal(diameters[1], [2.0, 3.0])
    assert_array_almost_equal(diameters[1], diameters[2])
    assert_array_almost_equal(diameters[3], [2.6666667, 2.6666667])
    assert_array_almost_equal(diameters[3], diameters[4])
    assert_array_almost_equal(diameters[4], diameters[5])


def test_build_M4_rng(neu1):
    # Test with custom random generator
    test_model = copy.deepcopy(MODEL)
    test_model["basal_dendrite"]["trunk_taper"] = np.arange(0, 10, 0.3)
    diametrizer.build(
        neu1,
        input_model=test_model,
        diam_method="M4",
        random_generator=np.random.default_rng(3),
    )
    diameters = [i.diameters for i in neu1.sections.values()]
    assert_array_almost_equal(diameters[0], [3, 2.9, 2.8, 2.7, 2.6, 2.5, 2.4])
    assert_array_almost_equal(diameters[1], diameters[2])
    assert_array_almost_equal(
        diameters[2], [2.4, 0.84852815, 0.82852817, 0.8085281, 0.78852814, 0.76852816]
    )


def test_build_unknown_model(neu1):
    with pytest.raises(
        KeyError,
        match=(
            "The name of the diametrization method is unknown: 'UNKNOWN' is not in "
            r"\['M1', 'M2', 'M3', 'M4', 'M5'\]"
        ),
    ):
        diametrizer.build(neu1, None, None, "UNKNOWN")


def test_build_empty_model(neu1):
    with pytest.raises(ValueError):
        diametrizer.build(neu1, None, None, object())
