'''Definition of bifurcation functionality'''

import numpy as np
import tns.morphmath.rotation as rt


def get_random_point(D=1.0):
    '''
    Get 3-d coordinates of a new random point.
    The distance between the produced point and (0,0,0)
    is given by the value D.
    '''
    # pylint: disable=assignment-from-no-return
    phi = np.random.uniform(0., 2. * np.pi)
    theta = np.arccos(np.random.uniform(-1.0, 1.0))

    sn_theta = np.sin(theta)

    x = D * np.cos(phi) * sn_theta
    y = D * np.sin(phi) * sn_theta
    z = D * np.cos(theta)

    return np.array((x, y, z))


def get_bif_random():
    '''
    Get 3-d coordinates of a new random point.
    The distance between the produced point and (0,0,0)
    is given by the value D.
    '''
    dir1 = get_random_point()
    dir2 = get_random_point()

    return (np.array(dir1), np.array(dir2))


def get_bif_symmetric(direction, angles):
    '''
    Get 3-d coordinates for two new directions
    at a selected angle.
    '''
    # phi0 = angles[0] #not used
    # theta0 = angles[1] #not used
    phi1 = angles[2] / 2.
    theta1 = angles[3] / 2.

    dir1 = rt.rotate_vector(direction, [0, 0, 1], phi1)
    dir1 = rt.rotate_vector(dir1, [1, 0, 0], theta1)
    dir2 = rt.rotate_vector(direction, [0, 0, 1], - phi1)
    dir2 = rt.rotate_vector(dir2, [1, 0, 0], - theta1)

    return (np.array(dir1), np.array(dir2))


def get_bif_bio_oriented(direction, angles):
    '''Input: init_phi, init_theta, dphi, dtheta.
    '''
    phi0 = angles[0]
    theta0 = angles[1]
    phi1 = angles[2]
    theta1 = angles[3]

    dir1 = rt.rotate_vector(direction, [0, 0, 1], phi0)
    dir1 = rt.rotate_vector(dir1, [1, 0, 0], theta0)
    dir2 = rt.rotate_vector(dir1, [0, 0, 1], phi1)
    dir2 = rt.rotate_vector(dir2, [1, 0, 0], theta1)

    return (np.array(dir1), np.array(dir2))


def get_bif_directional(direction, angles):
    '''Input: init_phi, init_theta, dphi, dtheta.
    '''
    # phi0 = angles[0] #not used
    # theta0 = angles[1] #not used
    phi1 = angles[2]
    theta1 = angles[3]

    dir2 = rt.rotate_vector(direction, [0, 0, 1], phi1)
    dir2 = rt.rotate_vector(dir2, [1, 0, 0], theta1)

    return (np.array(direction), np.array(dir2))
