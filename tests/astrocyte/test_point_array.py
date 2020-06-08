import numpy as np
from numpy import testing as npt
from tns.astrocyte import point_array as _pa


def _create_dynamic_array():

    initial_capacity = 3
    resize_factor = 2

    array = _pa.DynamicPointArray(initial_capacity, resize_factor)

    return array


def test_dynamic_point_array_contructor():

    array = _create_dynamic_array()

    assert len(array) == 0

    npt.assert_allclose(array.data, np.empty(shape=(0, 3)))

    assert array._size == 0
    assert array._capacity == 3


def test_dynamic_point_array_append():

    array = _create_dynamic_array()

    p0 = np.random.random(3)
    array.append(p0)
    npt.assert_allclose(array.data, [p0])
    assert len(array) == 1
    assert array.capacity == 3

    p1 = np.random.random(3)
    array.append(p1)
    npt.assert_allclose(array.data, np.vstack((p0, p1)))
    assert len(array) == 2
    assert array.capacity == 3

    p2 = np.random.random(3)
    array.append(p2)
    npt.assert_allclose(array.data, np.vstack((p0, p1, p2)))
    assert len(array) == 3
    assert array.capacity == 3

    p3 = np.random.random(3)
    array.append(p3)
    npt.assert_allclose(array.data, np.vstack((p0, p1, p2, p3)))
    assert len(array) == 4
    assert array.capacity == 6
