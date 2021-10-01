from numpy.testing import assert_array_almost_equal

import neurots.morphmath.rotation as test_module


def test_vector_from_spherical():
    assert_array_almost_equal(test_module.vector_from_spherical(1, 1),
                              [0.454649, 0.708073, 0.540302])


def test_rotate_vector():
    assert_array_almost_equal(test_module.rotate_vector([1,1,1], [2,3,4], 2),
                              [0.293989, 1.240039, 1.172976])


def test_angle3D():
    assert_array_almost_equal(test_module.angle3D([1,1,1], [2,3,4]),
                              0.265729)
