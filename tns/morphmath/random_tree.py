from numpy import random
import numpy as np
import rotation as rt

#---------------------------- Random point generation ------------------------#

def get_random_point(D=1.0):
    '''
    Get 3-d coordinates of a new random point.
    The distance between the produced point and (0,0,0)
    is given by the value D.
    '''

    zeta0 = random.uniform(0,1)
    theta0 = np.arccos(2*(zeta0-0.5))
    phi0 = random.uniform(0,2*np.pi)

    x = D*np.sin(theta0)*np.cos(phi0)    
    y = D*np.sin(theta0)*np.sin(phi0)    

    z = D*np.cos(theta0)

    return np.array([x, y, z])


def get_bif_symmetric(direction, angles):
    '''
    Get 3-d coordinates for two new directions
    at a selected angle.
    '''
    #phi0 = angles[0] #not used
    #theta0 = angles[1] #not used
    phi1 = angles[2] / 2.
    theta1 = angles[3] / 2.

    phi, theta = rt.spherical_from_vector(direction)

    x1, y1, z1 = rt.vector_from_spherical(phi + phi1, theta + theta1)

    x2, y2, z2 = rt.vector_from_spherical(phi - phi1, theta - theta1)

    return (np.array([x1, y1, z1]), np.array([x2, y2, z2]))


def get_bif_bio_oriented(direction, angles):
    '''Input: init_phi, init_theta, dphi, dtheta.
    '''
    phi0 = angles[0]
    theta0 = angles[1]
    phi1 = angles[2]
    theta1 = angles[3]

    phi, theta = rt.spherical_from_vector(direction)

    x1, y1, z1 = rt.vector_from_spherical(phi - phi0, theta - theta0)

    x2, y2, z2 = rt.vector_from_spherical(phi - phi0 - phi1, theta - theta0 - theta1)

    return (np.array([x1, y1, z1]), np.array([x2, y2, z2]))


def get_bif_directional(direction, angles):
    '''Input: init_phi, init_theta, dphi, dtheta.
    '''
    #phi0 = angles[0] #not used
    #theta0 = angles[1] #not used
    phi1 = angles[2]
    theta1 = angles[3]

    phi, theta = rt.spherical_from_vector(direction)

    x1, y1, z1 = rt.vector_from_spherical(phi, theta)

    x2, y2, z2 = rt.vector_from_spherical(phi - phi1, theta - theta1)

    return (np.array([x1, y1, z1]), np.array([x2, y2, z2]))


def get_bif_soma_repulsion(direction, angles, soma, curr_point):
    '''Input: init_phi, init_theta, dphi, dtheta.
    '''
    phi0 = angles[2]
    theta0 = angles[3]

    phi, theta = rt.spherical_from_vector(np.subtract(curr_point, soma))

    x1, y1, z1 = rt.vector_from_spherical(phi + phi0, theta + theta0)

    x2, y2, z2 = rt.vector_from_spherical(phi - phi0, theta - theta0)

    return (np.array([x1, y1, z1]), np.array([x2, y2, z2]))
