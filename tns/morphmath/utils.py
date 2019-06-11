'''Util functions useful for general purposes'''

import numpy as np
from numpy import sqrt


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


def norm(vect):
    '''A faster norm than numpy.linalg.norm
       This will be used for single vectors.
    '''
    return sqrt(vect[0] * vect[0] + vect[1] * vect[1] + vect[2] * vect[2])
