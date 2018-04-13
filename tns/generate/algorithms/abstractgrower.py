"""Abstract class for TreeGrower Algorithms"""

import abc


class AbstractAlgo(object):
    """TreeGrower abstract class"""
    # meta class is used to define other classes
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self,
                 input_data,
                 bif_method,
                 start_point):
        """Abstract TreeGrower Algorithm initialization.
        input_data: dictionary in which data used by the algorithm are stored
        bif_method: bifurcation method, select from: bio_oriented, symmetric, directional
        """

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
