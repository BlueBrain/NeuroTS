"""Abstract class for TreeGrower Algorithms"""

import abc


class AbstractAlgo(object):
    """TreeGrower abstract class"""
    # meta class is used to define other classes
    __metaclass__ = abc.ABCMeta

    def __init__(self, input_data, params, start_point, context):
        """TreeGrower Algorithm initialization.
        input_data: dictionary in which data used by the algorithm are stored
        params: parameters needed for growth, it should include the bif_method
        bifurcation method, select from: bio_oriented, symmetric, directional
        context: an object containing contextual information
        """
        self.context = context
        self.input_data = input_data
        self.params = params
        self.start_point = start_point

    @abc.abstractmethod
    def initialize(self):
        """Abstract TreeGrower Algorithm initialization.
        Generates the data to be used for the initialization of the first section to be grown.
        """

    @abc.abstractmethod
    def bifurcate(self, currentSec):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """

    @abc.abstractmethod
    def terminate(self, currentSec):
        """When the growth of a section is terminated the "term"
        must be removed from the TMD grower
        """

    @abc.abstractmethod
    def extend(self, currentSec):
        """Definition of stop criterion for the growth of the current section.
        """
