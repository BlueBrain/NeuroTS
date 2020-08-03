"""Functionality used by multiple algorithms"""

# from collections import namedtuple
import numpy as np
from tns.morphmath import bifurcation as _bif


bif_methods = {'bio_oriented': _bif.bio_oriented,
               'symmetric': _bif.symmetric,
               'directional': _bif.directional,
               'random': _bif.random}


def checks_bif_term(ref, bif, term, target_length):
    '''Returns True if:
       1. Ref < Bif < Term unless Bif is infinite, then Ref < Term
       2. Target_length >= (Bif - Ref)
       3. Target_length >= (Term - Ref)
       Otherwise returns False
    '''
    term_cond = 0 < term - ref <= target_length

    if np.isinf(bif):
        return term_cond

    bif_cond = 0 < bif - ref <= target_length

    return term_cond and bif_cond and term > bif


def section_data(direction, first_point, stop_criteria, process_type):
    """ Generates section data dictionary from arguments """
    return {'direction': direction,
            'first_point': first_point,
            'stop': stop_criteria,
            'process': process_type}


class TMDStop:
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
        # self.verify()

    def printme(self):
        '''Prints all features'''
        TMDuple = self.ref, self.bif_id, self.bif, self.term_id, self.term
        print("(Ref: {}, BifID: {}, Bif: {}, TermID: {}, Term: {})".format(*TMDuple))

    def verify(self):
        '''Returns True if stop is valid.
           Validity is defined by bif < term
           unless bif in infinity.
           Also both bif and term have to be
           larger than the reference distance.
        '''
        # If no bifurcation the bif comparison is meaningless
        if np.isinf(self.bif) and (self.ref <= self.term):
            return True
        if self.ref <= self.bif <= self.term:
            return True
        return False

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

    def expected_bifurcation_length(self):
        '''Computes an estimate for the length of the branch
           if a bifurcation occurs. That will happen at distance
           "bif" and therefore the expected length is:
           (bifurcation - current length).
           If bifurcation is inf, the expected length is zero.
        '''
        if np.isinf(self.bif):
            return 0.0
        return abs(self.bif - self.ref)

    def expected_termination_length(self):
        '''Computes an estimate for the length of the branch
           if a termination occurs. That will happen at distance
           "term" and therefore the expected length is:
           (termination - current length).
           If termination is inf, the expected length is zero.
        '''
        if np.isinf(self.term):
            return 0.0
        return abs(self.term - self.ref)

    def expected_maximum_length(self):
        '''Returns the expected length of the current section.
           That is computed as the difference between reference value
           and the expected bifurcation value.
           If bifurcation < termination, then the reference value
           minus the termination will be computed instead.
           In real morphologies termination will be larger than
           bifurcation, unless bifurcation is set to inf.
           So the expected length will be computed based on term
           only if the section will terminate before it bifurcates.
        '''
        if np.isinf(self.bif):
            return abs(self.ref - self.term)
        return abs(self.ref - max(self.bif, self.term))

    def __eq__(self, other):
        'Run tests'
        if isinstance(other, TMDStop):
            return (self.bif_id == other.bif_id and
                    self.term_id == other.term_id and
                    np.isclose(self.bif, other.bif) and
                    np.isclose(self.term, other.term) and
                    np.allclose(self.ref, other.ref))
        return False
