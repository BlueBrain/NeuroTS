"""Class to collect all TMD related info used in NeuroTS."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import copy
from collections import OrderedDict

import numpy as np

from neurots.basic import round_num
from neurots.utils import NeuroTSError


class Barcode:
    """Class to generate the barcode structure.

    The barcode structure is essential for the TMD based growth algorithms.

    Args:
        ph_angles (list of lists): list of barcodes and angles of 6 elements:

            * either::

                [
                    end_point,
                    start_point,
                    4D_angles
                ]

            * or equivalent::

                [
                    Termination,
                    Bifurcation,
                    Angle parent - child (x-y),
                    Angle parent - child (z),
                    Angle child1 - child2 (x-y),
                    Angle child1 - child2 (z)
                ]

    Returns:
       The ph_angles will be decomposed in the following dictionaries::

           {
               angles: {ID: 4D_angles}
               bifs: {ID: start_point}
               terms: {ID, end_point}
           }
    """

    def __init__(self, ph_angles):
        """Initialize the ph_angles into a barcode object."""
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

    @staticmethod
    def validate_persistence(ph_angles):
        """Checks if data are in the expected format.

        The input barcodes should follow the rules:
        1. Bar: (start, end), end > start
        """
        for p in ph_angles:
            if p[0] <= p[1]:
                return False
        return True

    def get_bar(self, bar_id):
        """Returns the pair of (bifurcation, termination) that corresponds to the input index.

        The trivial bifurcation of id=0 is not included.
        """
        if bar_id == 0:
            return (0, self.terms[bar_id])
        return (self.bifs[bar_id], self.terms[bar_id])

    def get_persistence_length(self):
        """Returns the maximum bar length."""
        return self.terms[0]

    def remove_bif(self, bar_id):
        """Remove a bifurcation that has been used if bif_id is not None."""
        if bar_id is not None:
            del self.bifs[bar_id]

    def remove_term(self, bar_id):
        """Remove a termination that has been used, if term_id is not None."""
        if bar_id is not None:
            del self.terms[bar_id]

    def get_term(self, bar_id):
        """Returns a termination based on index if the input ID exists of infinity.

        If it doesn't exist the branch will terminate
        as it gets term = -infinity.
        """
        try:
            return self.terms[bar_id]
        except KeyError:
            # bar ID does not exist
            return -np.inf

    def get_term_between(self, bar_id, above=0.0, below=np.inf):
        """Returns a termination based on index.

        If the index exists and its value is between the above / below thresholds, the termination
        is returned.
        If it doesn't exist the branch will terminate as it gets `term = -infinity`.
        """
        try:
            term = self.terms[bar_id]
            if above <= term <= below:
                return (bar_id, term)
            else:
                # no term found with requested properties
                return (None, -np.inf)
        except KeyError:
            # bar ID does not exist
            return (None, -np.inf)

    def min_bif(self, bif_above=0.0, bif_below=np.inf):
        """Returns the id and value of the minimum bifurcation whose value is in threshold range.

        If no value is valid, returns infinity (np.inf) and therefore the index is None.
        """
        if np.isinf(bif_above):
            bif_above = 0.0
        for bifurcation in self.bifs.items():
            bifurcation_value = bifurcation[1]
            if bif_below >= bifurcation_value >= bif_above:
                return bifurcation
        return (None, np.inf)

    def min_term(self, term_above=0.0, term_below=np.inf):
        """Returns the id and value of the minimum termination whose value is in threshold range.

        If no value is valid, returns zero, the section will terminate and therefore the index is
        None.
        """
        if np.isinf(term_above):
            term_above = 0.0
        for termination in self.terms.items():
            termination_value = termination[1]
            if term_below >= termination_value >= term_above:
                return termination
        return (None, 0)

    def max_term(self):
        """Returns the id and value of the maximum termination.

        Termination list cannot be empty. This means the growth should have stopped, and therefore
        it will results in a 'StopIteration' error
        """
        return next(reversed(self.terms.items()))

    def curate_stop_criterion(self, parent_stop, child_stop):
        """Checks if the children stop criterion is compatible with parent.

        The child bar's length should be smaller than the current bar's length.
        This process ensures that each branch can only generate smaller branches.
        The criteria to ensure this statement is `True` are the following:

        * parent_stop.ref <= child_stop.bif <= parent_stop.term or child_stop.bif = inf
        * child_stop.term <= parent_stop.term
        * term(child_stop.bif) <= parent_stop.term

        Args:
            parent_stop (TMDStop): stop criteria of parent section.
            target_stop (TMDStop): proposed stop criteria for child.

        Returns:
            TMDStop: The next bar for which the expected length of the child branch is smaller than
            current one for both bif and term.
        """
        MAX_ref = parent_stop.term
        target_stop = copy.deepcopy(child_stop)

        # Case 0. Incompatibility checks
        # One of the assumed conditions is wrong
        # This should not happen, therefore growth should stop!
        if target_stop.term > MAX_ref:
            raise NeuroTSError("broken pipeline")
        if (not np.isinf(target_stop.bif)) and (target_stop.bif > MAX_ref):
            raise NeuroTSError("broken pipeline")

        # Case 1. Requirements fulfilled for inputs ref, bif, term
        if self.get_term(target_stop.bif_id) <= target_stop.term:
            return target_stop

        # Case 2. A new bifurcation needs to be identified
        bif_id, bif = self.select_compatible_bif(
            below_bif=parent_stop.ref,
            above_bif=MAX_ref,
            below_term=parent_stop.ref,
            above_term=target_stop.term,
        )
        target_stop.update_bif(bif_id, bif)
        return target_stop

    def select_compatible_bif(self, below_bif, above_bif, below_term, above_term):
        """Finds a bifurcation within the barcode.

        The bifurcation must fulfil both bif and term criteria / boundaries:
        below_bif <= bif <= above_bif
        below_term <= term <= above_term
        """
        # Search bar according to minimum bifurcation
        for bif_id, bif in self.bifs.items():
            corresp_term = self.get_term(bif_id)
            if (below_bif <= bif <= above_bif) and (below_term <= corresp_term <= above_term):
                # Define new termination corresponding to bifurcation
                return (bif_id, bif)
        return (None, np.inf)
