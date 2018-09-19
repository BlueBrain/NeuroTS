import numpy as np
import math

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


def rotation_around_axis(axis, angle):
    """Returns a normalized vector rotated
    around the selected axis by an angle.
    """
    d = np.array(axis, dtype=np.float) / np.linalg.norm(axis)

    sn = np.sin(angle)
    cs = np.cos(angle)

    eye = np.eye(3, dtype=np.float)
    #ddt = np.outer(d, d)
    skew = np.array([[    0,  -d[2],   d[1]],
                     [ d[2],     0,   -d[0]],
                     [-d[1],   d[0],     0]], dtype=np.float)

    #mtx = ddt + cs * (eye - ddt) + sn * skew
    #mtx = cs * eye + sn * skew + (1. - cs) * ddt
    mtx = eye + sn * skew + (1. - cs) * np.linalg.matrix_power(skew, 2)
    return mtx


def angle3D(v1, v2):
    """Returns the angle between v1, v2"""
    def dotproduct(v1, v2):
        return sum((a*b) for a, b in zip(v1, v2))
    def length(v):
        return math.sqrt(dotproduct(v, v))
    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))


def rotate_vector(vec, axis, angle):
    """Rotates the input vector vec
       by a selected angle
       around a specific axis.
    """
    return np.dot(rotation_around_axis(axis, angle), vec)
