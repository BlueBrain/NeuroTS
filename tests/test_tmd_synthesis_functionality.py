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

import json
import os

import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal
from numpy.testing import assert_array_equal
from numpy.testing import assert_equal

from neurots.generate.algorithms.barcode import Barcode
from neurots.generate.algorithms.common import TMDStop
from neurots.generate.algorithms.common import checks_bif_term
from neurots.utils import NeuroTSError

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def test_barcode():
    """Tests the barcode functionality"""

    with open(os.path.join(_PATH, "dummy_distribution.json"), encoding="utf-8") as f:
        ph_angles = json.load(f)["apical_dendrite"]["persistence_diagram"][0]

    barcode_test = Barcode(ph_angles)
    assert_equal(barcode_test.get_term_between(999), (None, -np.inf))
    assert_array_equal(barcode_test.min_bif(np.inf), (1, 26.3027))
    assert_array_equal(barcode_test.min_term(np.inf), (2, 155.8809))

    assert_equal(len(barcode_test.bifs), 7)
    assert_equal(len(barcode_test.terms), 8)
    assert_equal(len(barcode_test.angles), 8)
    assert_array_almost_equal(barcode_test.angles[0], [np.nan, np.nan, np.nan, np.nan])

    assert_equal(barcode_test.bifs[1], 26.3027)
    assert_equal(barcode_test.terms[1], 204.0442)
    assert_array_almost_equal(barcode_test.angles[1], [-0.279172, -0.138322, 1.598153, 0.672246])

    assert_array_almost_equal(barcode_test.get_bar(0), (0, 633.5966))
    assert_array_almost_equal(barcode_test.get_bar(1), (26.3027, 204.0442))

    assert_array_almost_equal(barcode_test.min_bif(), (1, 26.3027))
    assert_array_almost_equal(barcode_test.min_term(), (2, 155.8809))
    assert_array_almost_equal(barcode_test.max_term(), (0, 633.5966))

    barcode_test.remove_bif(1)
    assert_array_almost_equal(barcode_test.min_bif(), (2, 52.4013))

    barcode_test.remove_term(2)
    assert_array_almost_equal(barcode_test.min_term(), (1, 204.0442))


def test_barcode_validate_persistence():
    """Tests the barcode functionality"""

    with open(os.path.join(_PATH, "dummy_distribution.json"), encoding="utf-8") as f:
        ph_angles = json.load(f)["apical_dendrite"]["persistence_diagram"][0]
    assert Barcode.validate_persistence(ph_angles)
    ph_angles[0][0] = 0
    assert not Barcode.validate_persistence(ph_angles)


def test_checks_bif_term():
    """Test the checks_bif_term() function"""
    assert checks_bif_term(0, 1, 2, 10)
    assert not checks_bif_term(2, 1, 0, 10)

    assert checks_bif_term(0, np.inf, 2, 10)
    assert not checks_bif_term(2, np.inf, 0, 10)

    assert not checks_bif_term(0, 1, 2, 0.5)
    assert not checks_bif_term(0, np.inf, 2, 0.5)

    assert checks_bif_term(0, 1, 2, 2)
    assert not checks_bif_term(2, 1, 0, 2)


def test_TMDStop():
    """Test the TMDStop class"""
    tmd_stop = TMDStop(1, 26.3027, 0, 633.5966, 10.0)
    assert str(tmd_stop) == "(Ref: 10.0, BifID: 1, Bif: 26.3027, TermID: 0, Term: 633.5966)"
    assert_equal(tmd_stop.bif_id, 1)
    assert_equal(tmd_stop.term_id, 0)
    assert_equal(tmd_stop.bif, 26.3027)
    assert_equal(tmd_stop.term, 633.5966)
    assert_equal(tmd_stop.ref, 10.0)
    assert_equal(tmd_stop.child_length(), 607.2939)
    assert_equal(tmd_stop.expected_termination_length(), 623.5966)
    # Comparison should pass for same TMDstop
    assert tmd_stop == TMDStop(1, 26.3027, 0, 633.5966, 10.0)
    # Comparison should fail for not same TMDstop
    assert tmd_stop != TMDStop(1, 20, 0, 633.5966, 10.0)
    # Comparison should fail for other object
    assert tmd_stop != 10

    tmd_stop.update_bif(0, 11.0)
    assert_equal(tmd_stop.bif_id, 0)
    assert_equal(tmd_stop.bif, 11.0)

    tmd_stop.update_term(10, 110.0)
    assert_equal(tmd_stop.term_id, 10)
    assert_equal(tmd_stop.term, 110.0)

    assert tmd_stop.verify()
    assert_equal(tmd_stop.expected_bifurcation_length(), 1)

    tmd_stop.bif = np.inf
    assert tmd_stop.verify()
    assert_equal(tmd_stop.expected_bifurcation_length(), 0)

    tmd_stop.ref = 99999
    assert not tmd_stop.verify()

    tmd_stop.term = np.inf
    assert_equal(tmd_stop.expected_termination_length(), 0)

    with open(os.path.join(_PATH, "dummy_distribution.json"), encoding="utf-8") as f:
        ph_angles = json.load(f)["apical_dendrite"]["persistence_diagram"][0]

    barcode_test = Barcode(ph_angles)

    parent_stop = TMDStop(1, 26.3027, 0, 10, 10.0)
    child_stop = TMDStop(1, 26.3027, 0, 999999, 10.0)
    with pytest.raises(NeuroTSError):
        barcode_test.curate_stop_criterion(parent_stop, child_stop)

    child_stop = TMDStop(1, 26.3027, 999999, 5, 10.0)
    with pytest.raises(NeuroTSError):
        barcode_test.curate_stop_criterion(parent_stop, child_stop)
