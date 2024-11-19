"""Definition of bifurcation functionality."""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

import numpy as np

import neurots.morphmath.rotation as rt
from neurots.morphmath.utils import get_random_point
from neurots.utils import PIA_DIRECTION


def random(random_generator=np.random, pia_direction=None):
    """Get 3-d coordinates of a new random point.

    The distance between the produced point and (0,0,0) is given by the value D.
    """
    dir1 = get_random_point(random_generator=random_generator)
    dir2 = get_random_point(random_generator=random_generator)

    return dir1, dir2


def symmetric(direction, angles, pia_direction=None):
    """Get 3-d coordinates for two new directions at a selected angle."""
    phi1 = angles[2] / 2.0
    theta1 = angles[3] / 2.0

    x_dir = np.array([1, 0, 0])
    z_dir = np.array([0, 0, 1])
    if pia_direction is not None:
        rot = rt.rotation_matrix_from_vectors(PIA_DIRECTION, pia_direction).T
        z_dir = z_dir.dot(rot)
        x_dir = x_dir.dot(rot)

    dir1 = rt.rotate_vector(direction, z_dir, phi1)
    dir1 = rt.rotate_vector(dir1, x_dir, theta1)
    dir2 = rt.rotate_vector(direction, z_dir, -phi1)
    dir2 = rt.rotate_vector(dir2, x_dir, -theta1)

    return dir1, dir2


def bio_oriented(direction, angles, pia_direction=None):
    """Input: init_phi, init_theta, dphi, dtheta."""
    phi0 = angles[0]
    theta0 = angles[1]
    phi1 = angles[2]
    theta1 = angles[3]

    x_dir = np.array([1, 0, 0])
    z_dir = np.array([0, 0, 1])
    if pia_direction is not None:
        rot = rt.rotation_matrix_from_vectors(PIA_DIRECTION, pia_direction).T
        z_dir = z_dir.dot(rot)
        x_dir = x_dir.dot(rot)

    dir1 = rt.rotate_vector(direction, z_dir, phi0)
    dir1 = rt.rotate_vector(dir1, x_dir, theta0)
    dir2 = rt.rotate_vector(dir1, z_dir, phi1)
    dir2 = rt.rotate_vector(dir2, x_dir, theta1)

    return dir1, dir2


def directional(direction, angles, pia_direction=None):
    """Input: init_phi, init_theta, dphi, dtheta."""
    phi1 = angles[2]
    theta1 = angles[3]

    x_dir = np.array([1, 0, 0])
    z_dir = np.array([0, 0, 1])
    if pia_direction is not None:
        rot = rt.rotation_matrix_from_vectors(PIA_DIRECTION, pia_direction).T
        z_dir = z_dir.dot(rot)
        x_dir = x_dir.dot(rot)

    dir2 = rt.rotate_vector(direction, z_dir, phi1)
    dir2 = rt.rotate_vector(dir2, x_dir, theta1)

    return direction, dir2
