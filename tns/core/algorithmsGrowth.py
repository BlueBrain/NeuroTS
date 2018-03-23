from tns.process_input import handle_distributions
from tns.morphmath import random_tree as rd
from tns.morphmath import sample
from tns.basic import round_num
import numpy as np

#growth_methods = {'ph_apical': 'generate_ph_apical',
#                  'ph_angles': 'generate_ph_angles',
#                  'ph_basic': 'generate_ph',
#                  'trunk': 'generate_trunk',
#                  'binary': 'generate_binary',}

bif_methods = {'bio_oriented': rd.get_bif_bio_oriented,
               'symmetric': rd.get_bif_symmetric,
               'directional': rd.get_bif_directional, 
               'random': rd.get_bif_random}


class TMDGrower(object):
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
        print "TMD Section is growing with selected: ", growth_method


    def initialize(self):
        """Generates the data to be used for the initialization
        of the first section to be grown. Saves the extracted
        input data into the corresponding structures.
        """
        bif, term, angles, bt_all = handle_distributions.init_ph_angles(self.ph_angles)

        self.bif = bif
        self.term = term
        self.angles = angles
        self.bt_all = bt_all

        stop = {"bif_term": {"ref": self.start_point[:3],
                             "bif": self.bif[0],
                             "term": self.term[-1]}}

        num_sec = len(self.ph_angles)

        return stop, num_sec


    def bifurcate(self, currentSec):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.bif.remove(currentSec.stop_criteria["bif_term"]["bif"])
        ang = self.angles[currentSec.stop_criteria["bif_term"]["bif"]]
        dir1, dir2 = self.bif_method(currentSec.direction, angles=ang)
        start_point = np.array(currentSec.points3D[-1])

        stop1 = {"bif_term": {"ref": self.start_point[:3],
                              "bif": self.bif[0] if self.bif else np.inf,
                              "term": round_num(currentSec.stop_criteria["bif_term"]["term"])}}

        stop2 = {"bif_term": {"ref": self.start_point[:3],
                              "bif": self.bif[0] if self.bif else np.inf,
                              "term": round_num(self.bt_all[currentSec.stop_criteria["bif_term"]["bif"]])}}

        s1 = {'direction': dir1,
              'start_point': start_point,
              'stop':stop1,
              'process': currentSec.process}

        s2 = {'direction': dir2,
              'start_point': start_point,
              'stop':stop2,
              'process': currentSec.process}

        return s1, s2


    def terminate(self, currentSec):
        """When the growth of a section is terminated the "term"
        must be removed from the TMD grower
        """
        self.term.remove(currentSec.stop_criteria["bif_term"]["term"])


    def continuate(self, currentSec):
        """Definition of stop criterion for the growth of the current section.
        """
        currentSec.stop_criteria["bif_term"]["bif"] = round_num(self.bif[0]) if self.bif else np.inf

        if currentSec.stop_criteria["bif_term"]["term"] not in self.term:
            currentSec.stop_criteria["bif_term"]["term"] = round_num(self.term[0]) if self.term else np.inf

        return currentSec.generate()


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
        self.bif_method = bif_methods[bif_method]
        self.growth_method = growth_method
        print "Basic Section is growing with selected: ", growth_method
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

        children = 0
        print currentSec.parent, self.growth_method
        if self.growth_method == 'binary' and currentSec.parent < 4:
            children = 2

        s1 = {'direction': dir1,
              'start_point': start_point,
              'stop':stop1,
              'process': currentSec.process,
              'children':children}

        s2 = {'direction': dir2,
              'start_point': start_point,
              'stop':stop2,
              'process': currentSec.process,
              'children':children}

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

        return currentSec.generate_nseg()
