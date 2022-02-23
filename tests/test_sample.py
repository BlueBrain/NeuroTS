"""Test neurots.morphmath.sample code."""

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
import numpy as np
import pytest
from numpy.testing import assert_equal

from neurots.morphmath import sample


def test_Distr():
    # pylint: disable=too-many-statements
    # Test distributions
    assert_equal(sample.Distr.norm({"mean": 1, "std": 0.5}), ("standard_normal", 1, 0.5))
    assert_equal(sample.Distr.uniform({"min": 1, "max": 1.25}), ("uniform", 1, 0.25))
    assert_equal(sample.Distr.expon({"loc": 1, "lambda": 2}), ("standard_exponential", 1, 0.5))

    # Setup normal distribution
    np.random.seed(0)
    mt = np.random.MT19937()
    mt._legacy_seeding(0)  # Use legacy seeding to get the same result as with np.random.seed(0)
    rng = np.random.RandomState(mt)
    mt2 = np.random.MT19937()
    mt2._legacy_seeding(0)
    rng_new = np.random.Generator(mt2)

    params = {"norm": {"mean": 9.024144162609812, "std": 3.5462697985669935}}
    soma_d = sample.Distr(params)
    soma_d_rng = sample.Distr(params, random_generator=rng)
    soma_d_new = sample.Distr(params, random_generator=rng_new)

    # Test draw_positive
    val = soma_d.draw_positive()
    val_rng = soma_d_rng.draw_positive()
    val_new = soma_d_new.draw_positive()
    assert_equal(val, 15.279949720206192)
    assert_equal(val_rng, val)
    assert_equal(val_new, 10.356455608693715)

    assert_equal(soma_d.draw_positive(), 10.443209585321375)
    assert_equal(soma_d_rng.draw_positive(), 10.443209585321375)
    assert_equal(soma_d_new.draw_positive(), 14.207311245358344)

    # Test draw
    assert_equal(soma_d.draw(), 12.495013116354336)
    assert_equal(soma_d_rng.draw(), 12.495013116354336)
    assert_equal(soma_d_new.draw(), 18.201541834082416)

    # Setup uniform distribution
    params = {"uniform": {"min": 20, "max": 30}}
    soma_d = sample.Distr(params)
    soma_d_rng = sample.Distr(params, random_generator=rng)
    soma_d_new = sample.Distr(params, random_generator=rng_new)

    # Test draw_positive
    val = soma_d.draw_positive()
    val_rng = soma_d_rng.draw_positive()
    soma_d_new.draw_positive()  # This call is just to align random states of rng and rng_new
    val_new = soma_d_new.draw_positive()
    assert_equal(val, 24.236547993389046)
    assert_equal(val_rng, val)
    assert_equal(val_new, val)

    expected = 26.45894113066656
    assert_equal(soma_d.draw_positive(), expected)
    assert_equal(soma_d_rng.draw_positive(), expected)
    assert_equal(soma_d_new.draw_positive(), expected)

    # Test draw
    expected = 24.375872112626926
    assert_equal(soma_d.draw(), expected)
    assert_equal(soma_d_rng.draw(), expected)
    assert_equal(soma_d_new.draw(), expected)

    # Setup exponential distribution
    params = {"expon": {"loc": 10, "lambda": 5}}
    soma_d = sample.Distr(params)
    soma_d_rng = sample.Distr(params, random_generator=rng)
    soma_d_new = sample.Distr(params, random_generator=rng_new)

    # Test draw_positive
    val = soma_d.draw_positive()
    val_rng = soma_d_rng.draw_positive()
    val_new = soma_d_new.draw_positive()
    assert_equal(val, 10.444704882606532)
    assert_equal(val_rng, val)
    assert_equal(val_new, 10.461004518163628)

    assert_equal(soma_d.draw_positive(), 10.662982436410763)
    assert_equal(soma_d_rng.draw_positive(), 10.662982436410763)
    assert_equal(soma_d_new.draw_positive(), 10.46145745042702)

    # Test draw
    assert_equal(soma_d.draw(), 10.09672042018045)
    assert_equal(soma_d_rng.draw(), 10.09672042018045)
    assert_equal(soma_d_new.draw(), 10.092614156264565)

    # Setup data distribution
    params = {"data": {"weights": [0.1, 0.9], "bins": [1, 2]}}
    soma_d = sample.Distr(params)
    assert_equal(soma_d.draw_positive(), 2)

    soma_d_rng = sample.Distr(params, random_generator=rng)
    assert_equal(soma_d_rng.draw_positive(), 2)

    # Setup negative loc distribution
    params = {"uniform": {"min": -10, "max": -10}}
    soma_d = sample.Distr(params)
    with pytest.raises(ValueError):
        soma_d.draw_positive()

    # Setup negative val distribution
    params = {"uniform": {"min": -50, "max": 10}}
    soma_d = sample.Distr(params, random_generator=rng)
    assert_equal(soma_d.draw_positive(), 5.535798297559666)


def test_soma_size():
    np.random.seed(0)
    rng = np.random.default_rng(0)
    params = {"soma": {"size": {"norm": {"mean": 9.024144162609812, "std": 3.5462697985669935}}}}

    val1 = sample.soma_size(params)
    assert_equal(val1, 15.279949720206192)

    val1_rng = sample.soma_size(params, random_generator=rng)
    assert_equal(val1_rng, 9.470017448440464)
