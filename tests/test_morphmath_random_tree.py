from nose import tools as nt
from tns.morphmath.random_tree import *
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal

def test_get_bif_directional():
    assert_array_almost_equal(get_bif_directional([0., 1., 0.], [0., 0., 0., np.pi/2]),
                              (np.array([0., 1., 0.]), np.array([0., 0., 1.])))
    assert_array_almost_equal(get_bif_directional([0., 1., 0.], [0., 0., 0., 0]),
                              (np.array([0., 1., 0.]), np.array([0., 1., 0.])))
    assert_array_almost_equal(get_bif_directional([0., 1., 0.], [0., 0., 0., np.pi]),
                              (np.array([0., 1., 0.]), np.array([0., -1., 0.])))
    assert_array_almost_equal(get_bif_directional([0., 1., 0.], [0., 0., 0., np.pi/4]),
                              (np.array([0., 1., 0.]), np.array([0., 1./np.sqrt(2), 1./np.sqrt(2)])))

def test_get_bif_bio_oriented():
    assert_array_almost_equal(get_bif_bio_oriented([0., 1., 0.], [0., 0., 0., np.pi/4]),
                              (np.array([0., 1., 0.]), np.array([0., 1./np.sqrt(2), 1./np.sqrt(2)])))
    assert_array_almost_equal(get_bif_bio_oriented([0., 1., 0.], [0., np.pi/4, 0., np.pi/4]),
                              (np.array([0., 1./np.sqrt(2), 1./np.sqrt(2)]), np.array([0., 0, 1])))

def test_get_bif_symmetric():
    assert_array_almost_equal(get_bif_symmetric([0,0,1], [1,1,1,1]),
                              [[0. ,-0.479426, 0.877583],
                               [0. , 0.479426, 0.877583]])