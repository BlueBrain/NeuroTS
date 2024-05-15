"""Test neurots.generate.section code."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
