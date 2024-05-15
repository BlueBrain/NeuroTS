"""Definition of basic rotation functionality."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    d = np.array(axis, dtype=float) / np.linalg.norm(axis)

    sn = np.sin(angle)
    cs = np.cos(angle)

    eye = np.eye(3, dtype=float)
    # ddt = np.outer(d, d)
    skew = np.array([[0, -d[2], d[1]], [d[2], 0, -d[0]], [-d[1], d[0], 0]], dtype=float)

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


def rotation_matrix_from_vectors(vec1, vec2):
    """Find the rotation matrix that aligns vec1 to vec2.

    Picked from morph_tool.transform
    Picked from: https://stackoverflow.com/a/59204638/3868743

    Args:
        vec1: A 3d "source" vector
        vec2: A 3d "destination" vector

    Returns:
        A transform matrix (3x3) which when applied to vec1, aligns it with vec2.
    """
    vec1, vec2 = vec1 / np.linalg.norm(vec1), vec2 / np.linalg.norm(vec2)

    v_cross = np.cross(vec1, vec2)
    v_cross_norm = np.linalg.norm(v_cross)
    if v_cross_norm == 0:
        return np.eye(3)

    kmat = np.array(
        [
            [0.0, -v_cross[2], v_cross[1]],
            [v_cross[2], 0.0, -v_cross[0]],
            [-v_cross[1], v_cross[0], 0.0],
        ]
    )

    return np.eye(3) + kmat + kmat.dot(kmat) * ((1 - np.dot(vec1, vec2)) / (v_cross_norm**2))
