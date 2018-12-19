'''Util functions useful for general purposes'''

from numpy import sqrt


def norm(vect):
    '''A faster norm than numpy.linalg.norm'''
    return sqrt(vect[0] * vect[0] + vect[1] * vect[1] + vect[2] * vect[2])
