from numpy import random
import numpy as np
import rotation as rt
from tns.morphmath.utils import norm


def get_random_point(D=1.0):
    '''
    Get 3-d coordinates of a new random point.
    The distance between the produced point and (0,0,0)
    is given by the value D.
    '''
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

    # phi, theta = rt.spherical_from_vector(direction)
    # dir1 = rt.vector_from_spherical(phi + phi1, theta + theta1)
    # dir2 = rt.vector_from_spherical(phi - phi1, theta - theta1)

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

    # phi, theta = rt.spherical_from_vector(direction)
    # dir1 = rt.vector_from_spherical(phi - phi0, theta - theta0)
    # dir2 = rt.vector_from_spherical(phi - phi0 - phi1, theta - theta0 - theta1)

    dir1 = rt.rotate_vector(direction, [0, 0, 1], phi0)
    dir1 = rt.rotate_vector(dir1, [1, 0, 0], theta0)
    dir2 = rt.rotate_vector(dir1, [0, 0, 1], phi1)
    dir2 = rt.rotate_vector(dir2, [1, 0, 0], theta1)

    return (np.array(dir1), np.array(dir2))


# def get_bif_bio_smoothed(direction, angles):
#    '''Input: init_phi, init_theta, dphi, dtheta.
#    '''
#    def smoothing(ang):
#        if np.abs(ang) > np.pi:
#            return np.abs(ang)/2
#        else:
#            return ang

#    phi0 = np.abs(smoothing(angles[0]))
#    theta0 = smoothing(angles[1])
#    phi1 = smoothing(angles[2])
#    theta1 = smoothing(angles[3])

#    phi, theta = rt.spherical_from_vector(direction)
#    dir1 = rt.vector_from_spherical(phi - phi0, theta - theta0)
#    dir2 = rt.vector_from_spherical(phi - phi0 - phi1, theta - theta0 - theta1)

#    return (np.array(dir1), np.array(dir2))


def get_bif_directional(direction, angles):
    '''Input: init_phi, init_theta, dphi, dtheta.
    '''
    # phi0 = angles[0] #not used
    # theta0 = angles[1] #not used
    phi1 = angles[2]
    theta1 = angles[3]

    # phi, theta = rt.spherical_from_vector(direction)
    # dir1 = rt.vector_from_spherical(phi, theta)
    # dir2 = rt.vector_from_spherical(phi - phi1, theta - theta1)

    dir2 = rt.rotate_vector(direction, [0, 0, 1], phi1)
    dir2 = rt.rotate_vector(dir2, [1, 0, 0], theta1)

    return (np.array(direction), np.array(dir2))


# def get_bif_soma_repulsion(direction, angles, soma, curr_point):
#    '''Input: init_phi, init_theta, dphi, dtheta.
#    '''
#    phi0 = angles[2]
#    theta0 = angles[3]

    # phi, theta = rt.spherical_from_vector(np.subtract(curr_point, soma))
    # dir1 = rt.vector_from_spherical(phi + phi0, theta + theta0)
    # dir2 = rt.vector_from_spherical(phi - phi0, theta - theta0)

#    dir1 = rt.rotate_vector(direction, [0,0,1], phi0)
#    dir1 = rt.rotate_vector(dir1, [1,0,0], theta0)
#    dir2 = rt.rotate_vector(dir1, [0,0,1], phi1)
#    dir2 = rt.rotate_vector(dir2, [1,0,0], theta1)

#    return (np.array(dir1), np.array(dir2))
