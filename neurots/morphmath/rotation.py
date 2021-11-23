"""Definition of basic rotation functionality."""

import math

import numpy as np

from neurots.morphmath.utils import norm


def spherical_from_vector(vect):
    """Return the spherical coordinates of a vector: phi, theta."""
    x, y, z = vect

    phi = np.arctan2(y, x)
    theta = np.arccos(z / norm(vect))

    return phi, theta


def vector_from_spherical(phi, theta):
    """Return a normalized vector from the spherical angles: phi, theta."""
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    return x, y, z


def rotation_around_axis(axis, angle):
    """Return a normalized vector rotated around the selected axis by an angle."""
    d = np.array(axis, dtype=np.float) / np.linalg.norm(axis)

    sn = np.sin(angle)
    cs = np.cos(angle)

    eye = np.eye(3, dtype=np.float)
    # ddt = np.outer(d, d)
    skew = np.array([[0, -d[2], d[1]], [d[2], 0, -d[0]], [-d[1], d[0], 0]], dtype=np.float)

    # mtx = ddt + cs * (eye - ddt) + sn * skew
    # mtx = cs * eye + sn * skew + (1. - cs) * ddt
    mtx = eye + sn * skew + (1.0 - cs) * np.linalg.matrix_power(skew, 2)
    return mtx


def angle3D(v1, v2):
    """Return the angle between v1, v2."""
    v1 = np.array(v1)
    v2 = np.array(v2)

    return math.acos(v1.dot(v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


def rotate_vector(vec, axis, angle):
    """Rotate the input vector vec by a selected angle around a specific axis."""
    return np.dot(rotation_around_axis(axis, angle), vec)
