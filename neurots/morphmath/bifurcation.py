"""Definition of bifurcation functionality."""

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

import numpy as np

import neurots.morphmath.rotation as rt
from neurots.morphmath.utils import get_random_point


def random(random_generator=np.random):
    """Get 3-d coordinates of a new random point.

    The distance between the produced point and (0,0,0) is given by the value D.
    """
    dir1 = get_random_point(random_generator=random_generator)
    dir2 = get_random_point(random_generator=random_generator)

    return (np.array(dir1), np.array(dir2))


def symmetric(direction, angles):
    """Get 3-d coordinates for two new directions at a selected angle."""
    # phi0 = angles[0] #not used
    # theta0 = angles[1] #not used
    phi1 = angles[2] / 2.0
    theta1 = angles[3] / 2.0

    dir1 = rt.rotate_vector(direction, [0, 0, 1], phi1)
    dir1 = rt.rotate_vector(dir1, [1, 0, 0], theta1)
    dir2 = rt.rotate_vector(direction, [0, 0, 1], -phi1)
    dir2 = rt.rotate_vector(dir2, [1, 0, 0], -theta1)

    return (np.array(dir1), np.array(dir2))


def bio_oriented(direction, angles):
    """Input: init_phi, init_theta, dphi, dtheta."""
    phi0 = angles[0]
    theta0 = angles[1]
    phi1 = angles[2]
    theta1 = angles[3]

    dir1 = rt.rotate_vector(direction, [0, 0, 1], phi0)
    dir1 = rt.rotate_vector(dir1, [1, 0, 0], theta0)
    dir2 = rt.rotate_vector(dir1, [0, 0, 1], phi1)
    dir2 = rt.rotate_vector(dir2, [1, 0, 0], theta1)

    return (np.array(dir1), np.array(dir2))


def directional(direction, angles):
    """Input: init_phi, init_theta, dphi, dtheta."""
    # phi0 = angles[0] #not used
    # theta0 = angles[1] #not used
    phi1 = angles[2]
    theta1 = angles[3]

    dir2 = rt.rotate_vector(direction, [0, 0, 1], phi1)
    dir2 = rt.rotate_vector(dir2, [1, 0, 0], theta1)

    return (np.array(direction), np.array(dir2))
