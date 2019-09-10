"""Class to collect all TMD related info used in TNS"""

from collections import OrderedDict
import numpy as np
from tns.basic import round_num


class Barcode(object):
    """Class to generate the barcode structure
       which is essential for the TMD based growth
       algorithms.
    """

    def __init__(self, ph_angles):
        '''Initialize the ph_angles
           into a barcode object.
           Args:
               ph_angles (list of lists): list of bracodes and angles of 6 elements:
                                          [end_point, start_point, 4D_angles]
                                           or equivalent:
                                          [Termination,
                                           Bifurcation,
                                           Angle parent - child (x-y),
                                           Angle parent - child (z),
                                           Angle child1 - child2 (x-y),
                                           Angle child1 - child2 (z)]
       The ph_angles will be decomposed in the following dictionaries
           angles: {ID: 4D_angles}
           bifs: {ID: start_point}
           terms: {ID, end_point}
           bars: {bif, term}
        '''
        # Sort persistence bars according to bifurcation
        ph_angles.sort(key=lambda x: x[1])

        self.bifs = OrderedDict()
        self.terms = OrderedDict()
        self.angles = OrderedDict()

        for bar_index, tmd_bar in enumerate(ph_angles):
            self.bifs[bar_index] = round_num(tmd_bar[1])
            self.terms[bar_index] = round_num(tmd_bar[0])
            self.angles[bar_index] = tmd_bar[2:]

        # Sort the terminations according to value to optimize access
        self.terms = OrderedDict(sorted(self.terms.items(), key=lambda x: x[1]))
        # Bifurcation at 0 is trivial so it should be removed
        del self.bifs[0]

    def get_bar(self, bar_id):
        '''Returns the pair of (bifurcation, termination)
           that corresponds to the input index
        '''
        if bar_id == 0:
            return (0, self.terms[bar_id])
        return (self.bifs[bar_id], self.terms[bar_id])

    def remove_bif(self, bar_id):
        '''Remove a bifurcation that has been used'''
        del self.bifs[bar_id]

    def remove_term(self, bar_id):
        '''Remove a termination that has been used'''
        del self.terms[bar_id]

    def min_bif(self):
        '''Returns the id and value of the minimum bifurcation
           If dict has no elements returns infinity (np.inf)
           and therefore the index is None
        '''
        try:
            return next(iter(self.bifs.items()))
        except StopIteration:
            return (None, np.inf)

    def min_term(self):
        '''Returns the id and value of the minimum termination
           Termination list cannot be empty. This means the growth
           should have stoped, and therefore it will results in a
           'StopIteration' error
        '''
        return next(iter(self.terms.items()))

    def max_term(self):
        '''Returns the id and value of the maximum termination
           Termination list cannot be empty. This means the growth
           should have stoped, and therefore it will results in a
           'StopIteration' error
        '''
        return next(reversed(self.terms.items()))
