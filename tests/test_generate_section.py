'''Test tns.generate.section code'''
from nose import tools as nt
from tns.generate import section
import numpy as np
from numpy.testing import assert_array_almost_equal


EXPECTED_WEIGHTS = np.array([0.01831564, 0.04978707, 0.13533528, 0.36787944, 1.        ])

def test_MEMORY_WEIGHTS():
    nt.ok_(section.MEMORY == 5)
    assert_array_almost_equal(section.WEIGHTS, EXPECTED_WEIGHTS)

def test_SectionGrower():
    # Create basic section for testing purposes
    s = section.SectionGrower(None, None, [0.,0.,0.], None, 0.0, 0.0, None, None)
    # Test trivial history is zeros.
    assert_array_almost_equal(s.history(), np.zeros(3))
    # Test history of one point.
    s.points.append([0.,1., 0.])
    s.latest_directions.append([0., 0., 1.])
    s.latest_directions_normed.append([0., 1., 0.])

    assert_array_almost_equal(s.history(), np.array([0., 1., 0.]))
    # Test history of two point.
    s.points.append([0.,1., 1.])
    s.latest_directions.append([0., 0., 1.])
    s.latest_directions_normed.append([0., 0., 1.])
    assert_array_almost_equal(s.history(), np.array([0., 0.34525776, 0.9385079]))
    s.points.append([0.,1., 2.])
    s.latest_directions.append([0., 0., 1.])
    s.latest_directions_normed.append([0., 0., 1.])
    assert_array_almost_equal(s.history(), np.array([0., 0.0984573, 0.99514128]))
    s.points.append([0.,1., 3.])
    s.latest_directions.append([0., 0., 1.])
    s.latest_directions_normed.append([0., 0., 1.])
    assert_array_almost_equal(s.history(), np.array([0., 0.03310225, 0.99945197]))
    s.points.append([1.,2., 4.])
    s.latest_directions.append([1., 1., 1.])
    s.latest_directions_normed.append([1., 1., 1.] / np.linalg.norm([1., 1., 1.]))
    assert_array_almost_equal(s.history(), np.array([0.41177931, 0.42484243, 0.80619272]))
