from tns.process_input import handle_distributions
from tns.morphmath import random_tree as rd
from tns.morphmath import sample
from tns.basic import round_num
import numpy as np

growth_methods = {'trunk': 'generate_trunk',
                  'binary': 'generate_binary',}
                  #'random_walk': 'generate_random_walk'}


bif_methods = {'random': rd.get_bif_random}


class BasicGrower(object):
    """TMD Grower class"""
    def __init__(self,
                 input_data,
                 bif_method,
                 growth_method,
                 start_point=None):
        """TMD Grower Object

        Parameters:
            neuron: Obj neuron where groups and points are stored
            initial_direction: 3D vector
            initial_point: 3D vector that defines the starting point of the tree
            parameters including: tree_type, radius, randomness, targeting, apical_distance
            tree_type: an integer indicating the type (choose from 2, 3, 4, 5)
        """
        self.ph_angles = sample.ph(input_data["ph"])
        self.bif_method = bif_methods[bif_method]
        self.growth_method = growth_method
        self.start_point = start_point


    def initialize(self):
        """Generates the data to be used for the initialization
        of the first section to be grown. Saves the extracted
        input data into the corresponding structures.
        """
        if self.growth_method == 'trunk':
            stop = {"num_seg":100}
            num_sec = 1
        elif self.growth_method == 'binary':
            stop = {"num_seg":100}
            num_sec = 16

        return stop, num_sec


    def bifurcate(self, currentSec):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        dir1, dir2 = self.bif_method()
        start_point = np.array(currentSec.points3D[-1])
        stop1 = currentSec.stop_criteria
        stop2 = currentSec.stop_criteria

        s1 = {'direction': dir1,
              'start_point': self.start_point,
              'stop':stop1,
              'process': currentSec.process}

        s2 = {'direction': dir2,
              'start_point': self.start_point,
              'stop':stop2,
              'process': currentSec.process}

        return s1, s2


    def terminate(self, currentSec):
        """When the growth of a section is terminated the "term"
        must be removed from the TMD grower
        """
        print 'Terminated: ', currentSec.parent


    def continuate(self, currentSec):
        """Definition of stop criterion for the growth of the current section.
        """
        print 'Continues now: ', currentSec.parent

