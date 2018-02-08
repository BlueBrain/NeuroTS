import rotation
from nose import tools as nt

def test_spherical_from_vector():
    nt.ok_(np.allclose(rotation.spherical_from_vector([0,1,0]), (np.pi/2, 0.0)))
    nt.ok_(np.allclose(rotation.spherical_from_vector([1,0,0]), (0.0, 0.0)))
    nt.ok_(np.allclose(rotation.spherical_from_vector([-1,0,0]), (np.pi, 0.0)))
    nt.ok_(np.allclose(rotation.spherical_from_vector([1,1,0]), (np.pi/4, 0.0)))


def test_vector_from_spherical():
    nt.ok_(np.allclose(rotation.vector_from_spherical(np.pi/2, 0.0), (0.0, 1.0, 0.0)))
    nt.ok_(np.allclose(rotation.vector_from_spherical(0.0, 0.0), (1.0, 0.0, 0.0)))
    nt.ok_(np.allclose(rotation.vector_from_spherical(np.pi, 0.0), (-1.0, 0.0, 0.0)))
    nt.ok_(np.allclose(rotation.vector_from_spherical(np.pi/4, 0.0), (0.70710678118654757, 0.70710678118654746, 0.0)))
