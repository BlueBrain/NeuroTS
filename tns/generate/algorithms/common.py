"""Functionality used by multiple algorithms"""

# from collections import namedtuple
import numpy as np
from tns.morphmath import random_tree as rd


bif_methods = {'bio_oriented': rd.get_bif_bio_oriented,
               'symmetric': rd.get_bif_symmetric,
               'directional': rd.get_bif_directional,
               'random': rd.get_bif_random}


class TMDStop(object):
    '''Class to define the data for stop criteria
       based on the TMD method.
    '''

    def __init__(self, bif_id, bif, term_id, term, ref):
        '''Initialization of TMDStop class with parameters.
        Args:
            bif_id (int): bifurcation ID
            bif (float): bifurcation value
            term_id (int): termination ID
            term (float): termination value
            ref (float): reference value (i.e for path or radial distances)
        '''
        self.bif_id = bif_id
        self.bif = bif
        self.term_id = term_id
        self.term = term
        self.ref = ref

    def update_bif(self, bif_id, bif):
        '''Sets new values to bifurcation'''
        self.bif_id = bif_id
        self.bif = bif

    def update_term(self, term_id, term):
        '''Sets new values to termination'''
        self.term_id = term_id
        self.term = term

    def child_length(self):
        '''Returns the absolute difference between
           bifurcation and termination, which
           defines the length of the bar.
        '''
        return abs(self.term - self.bif)

    def expected_length(self):
        '''Returns the expected length of the current section.
           That is computed as the difference between reference value
           and the expected bifurcation value.
           If bifurcation > termination, then the reference value
           minus the termination will be computed instead.
           In real morphologies termination will be larger than
           bifurcation, unless bifurcation is set to inf.
           So the expected length will be computed based on term
           only if the section will terminate before it bifurcates.
        '''
        return abs(self.ref - min(self.bif, self.term))

    def __eq__(self, other):
        if isinstance(other, TMDStop):
            return (self.bif_id == other.bif_id and
                    self.term_id == other.term_id and
                    np.isclose(self.bif, other.bif) and
                    np.isclose(self.term, other.term) and
                    np.allclose(self.ref, other.ref))
        return False
