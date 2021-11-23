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
# pylint: disable=redefined-outer-name
import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal

from neurots.generate import section
from neurots.generate.algorithms.common import TMDStop
from neurots.morphmath import sample

EXPECTED_WEIGHTS = np.array([0.01831564, 0.04978707, 0.13533528, 0.36787944, 1.0])


@pytest.fixture
def SEG_LEN():
    return sample.Distr({"norm": {"mean": 1.0, "std": 0.2}})


def test_MEMORY_WEIGHTS():
    assert section.MEMORY == 5
    assert_array_almost_equal(section.WEIGHTS, EXPECTED_WEIGHTS)


def test_SectionGrower(SEG_LEN):
    # Create basic section for testing purposes
    s = section.SectionGrower(
        None, None, [0.0, 0.0, 0.0], [0.0, 1.0, 0.0], 0.0, 0.0, None, None, SEG_LEN, 0.0
    )
    # Test trivial history is zeros.
    assert_array_almost_equal(s.history(), np.zeros(3))
    # Test history of one point.
    s.points.append([0.0, 1.0, 0.0])
    s.latest_directions.append([0.0, 1.0, 0.0])
    assert_array_almost_equal(s.history(), np.array([0.0, 1.0, 0.0]))
    # Test history of two point.
    s.points.append([0.0, 1.0, 1.0])
    s.latest_directions.append([0.0, 0.0, 1.0])
    assert_array_almost_equal(s.history(), np.array([0.0, 0.34525776, 0.9385079]))
    s.points.append([0.0, 1.0, 2.0])
    s.latest_directions.append([0.0, 0.0, 1.0])
    assert_array_almost_equal(s.history(), np.array([0.0, 0.0984573, 0.99514128]))
    s.points.append([0.0, 1.0, 3.0])
    s.latest_directions.append([0.0, 0.0, 1.0])
    assert_array_almost_equal(s.history(), np.array([0.0, 0.03310225, 0.99945197]))
    s.points.append([1.0, 2.0, 4.0])
    s.latest_directions.append([1.0, 1.0, 1.0] / np.linalg.norm([1.0, 1.0, 1.0]))
    assert_array_almost_equal(s.history(), np.array([0.41177931, 0.42484243, 0.80619272]))

    tmd_stop = TMDStop(1, 26.3027, 0, 633.5966, 40.0)
    # Check small section
    s = section.SectionGrowerExponentialProba(
        None,
        None,
        [0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        0.0,
        0.0,
        tmd_stop,
        None,
        SEG_LEN,
        0.0,
    )
    # Check that the growth will continue for single point section
    assert s.check_stop()
    with pytest.raises(NotImplementedError):
        s.get_val()


def test_history(SEG_LEN):
    s = section.SectionGrower(
        None, None, [0.0, 0.0, 0.0], [0.0, 1.0, 0.0], 0.0, 0.0, None, None, SEG_LEN, 0.0
    )
    assert_array_almost_equal(s.history(), np.array([0.0, 0.0, 0.0]))
    s.latest_directions = np.array([[0.0, 0.0, 0.0]])
    assert_array_almost_equal(s.history(), np.array([0.0, 0.0, 0.0]))
    s.latest_directions = np.array([[0.0, 1.0, 0.0]])
    assert_array_almost_equal(s.history(), np.array([0.0, 1.0, 0.0]))
    s.latest_directions = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    assert_array_almost_equal(s.history(), np.array([0.0, 0.34525776, 0.9385079]))
    s.latest_directions = np.array([[0.0, 0.0, 0.00000001]])
    assert_array_almost_equal(s.history(), np.array([0.0e00, 0.0e00, 1.0e-08]))
