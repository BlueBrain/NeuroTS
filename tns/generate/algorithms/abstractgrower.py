"""Abstract class for TreeGrower Algorithms"""

import abc

class AbstractAlgo(object):
    """TreeGrower abstract class"""
    # meta class is used to define other classes
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self,
                 input_data,
                 parameters,
                 start_point):
        """Abstract TreeGrower Algorithm initialization.
        input_data: dictionary in which data used by the algorithm are stored
        parameters: input parameters to be used by growth algorithm
        bif_method (bifurcation method, select from: bio_oriented, symmetric, directional)
        will be defined from the input parameters
        start_point: the coordinates of the first point of the tree
        """

    @abc.abstractmethod
    def first_section(self):
        """Generates the data to be used for the initialization of the first section 
        to be grown. Here the expected number of sections needs to be computed. 
        Also the initial stoping criterion is defined for the first section of the tree.
        """

    @abc.abstractmethod
    def bifurcate(self, currentSec):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections. Returns a dictionary for each new
        section to be generated that should contain:
        directions, start_point, stop_criterion, process_type, nunber_of_children
        """

    @abc.abstractmethod
    def terminate(self, currentSec):
        """When the section terminates there are usually a few actions to be
        performed, such as remove the data of the section that are used from
        the data consumed by the active growers.
        """

    @abc.abstractmethod
    def extend(self, currentSec):
        """Corresponds to the continuation of a section and within this function
        the section grower is called and the generated section is returned.
        """
