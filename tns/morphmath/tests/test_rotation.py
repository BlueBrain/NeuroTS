from tns.morphmath.rotation import spherical_from_vector, vector_from_spherical
from nose import tools as nt

import numpy as np
from numpy.testing import assert_array_equal

def test_spherical_from_vector():
    # FIXME
    # assert_array_equal(spherical_from_vector([0,1,0]), (np.pi/2, 0.0))
    # assert_array_equal(spherical_from_vector([1,0,0]), (0.0, 0.0))
    # assert_array_equal(spherical_from_vector([-1,0,0]), (np.pi, 0.0))
    # assert_array_equal(spherical_from_vector([1,1,0]), (np.pi/4, 0.0))
    pass


def test_vector_from_spherical():
    # assert_array_equal(vector_from_spherical(np.pi/2, 0.0), (0.0, 1.0, 0.0))
    # assert_array_equal(vector_from_spherical(0.0, 0.0), (1.0, 0.0, 0.0))
    # assert_array_equal(vector_from_spherical(np.pi, 0.0), (-1.0, 0.0, 0.0))
    # assert_array_equal(vector_from_spherical(np.pi/4, 0.0), (0.70710678118654757, 0.70710678118654746, 0.0))
    pass
