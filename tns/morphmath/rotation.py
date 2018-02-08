import numpy as np

def spherical_from_vector(vect):
    """Returns the spherical coordinates
    of a vector: phi, theta
    """
    x, y, z = vect

    phi = np.arctan2(y, x)
    theta = np.arccos(z / np.linalg.norm(vect))

    return phi, theta


def vector_from_spherical(phi, theta):
    """Returns a normalized vector
    from the spherical angles: phi, theta
    """
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    return x, y, z


def rotation_around_axis(direction, angle):
    """Returns a normalized vector rotated
    around the selected direction by an angle.
    """
    d = np.array(direction, dtype=np.float64)
    d /= np.linalg.norm(d)

    eye = np.eye(3, dtype=np.float64)
    ddt = np.outer(d, d)
    skew = np.array([[    0,  d[2],  -d[1]],
                     [-d[2],     0,  d[0]],
                     [d[1], -d[0],    0]], dtype=np.float64)

    mtx = ddt + np.cos(angle) * (eye - ddt) + np.sin(angle) * skew
    return mtx
