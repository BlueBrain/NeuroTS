"""Basic class for TreeGrower Algorithms"""
import logging
import numpy as np

from tns.generate.algorithms.abstractgrower import AbstractAlgo
from tns.generate.algorithms.common import bif_methods
from tns.generate.algorithms.common import section_data

logger = logging.getLogger(__name__)


class TrunkAlgo(AbstractAlgo):
    """TreeGrower basic growth of trunks class"""

    def __init__(self,
                 input_data,
                 params,
                 start_point,
                 context=None,
                 **_):
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
        first_point = np.array(current_section.last_point)
        stop = current_section.stop_criteria

        return section_data(dir1, first_point, stop, current_section.process), \
               section_data(dir2, first_point, stop, current_section.process)

    def terminate(self, current_section):
        """When the growth of a section is terminated the "term"
        must be removed from the TMD grower
        """

    def extend(self, current_section):
        '''Creates a section with the selected parameters
           until at least one stop criterion is fulfilled.
        '''
        return current_section.next()


class AxonAlgo(TrunkAlgo):
    """TreeGrower of axon growth.

    Only a trunk with one segment is synthesized and another process is supposed to gaft an actual
    axon on this trunk.
    """

    def __init__(self, *args, **kwargs):
        # Force num_seg in params to 1
        params = kwargs.get("params", None) or args[1]
        params["num_seg"] = 1

        super().__init__(*args, **kwargs)
