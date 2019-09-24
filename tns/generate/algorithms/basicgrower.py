"""Basic class for TreeGrower Algorithms"""
import logging
import numpy as np

from tns.generate.algorithms.abstractgrower import AbstractAlgo
from tns.generate.algorithms.common import bif_methods

logger = logging.getLogger(__name__)


class TrunkAlgo(AbstractAlgo):
    """TreeGrower basic growth of trunks class"""

    def __init__(self,
                 input_data,
                 params,
                 start_point,
                 context=None):
        """
        input_data: saves all the data required for the growth
        params: parameters needed for growth, it should include the bif_method
        bifurcation method, select from: bio_oriented, symmetric, directional
        context: an object containing contextual information
        """
        super(TrunkAlgo, self).__init__(input_data, params, start_point, context)
        self.bif_method = bif_methods[params["branching_method"]]

    def initialize(self):
        """Generates the data to be used for the initialization
        of the first section to be grown. Saves the extracted
        input data into the corresponding structures.
        """
        stop = {"num_seg": self.params['num_seg']}
        num_sec = 1  # A single section per tree will be generated

        return stop, num_sec

    def bifurcate(self, current_section):
        """When the section bifurcates two new sections are created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        dir1, dir2 = self.bif_method()
        start_point = np.array(current_section.last_point)
        stop = current_section.stop_criteria

        children = 0
        # print currentSec.parent, self.growth_method

        s1 = {'direction': dir1,
              'start_point': start_point,
              'stop': stop,
              'process': current_section.process,
              'children': children}

        s2 = {'direction': dir2,
              'start_point': start_point,
              'stop': stop,
              'process': current_section.process,
              'children': children}

        return s1, s2

    def terminate(self, current_section):
        """When the growth of a section is terminated the "term"
        must be removed from the TMD grower
        """

    def extend(self, current_section):
        '''Creates a section with the selected parameters
           until at least one stop criterion is fulfilled.
        '''
        return current_section.next()
