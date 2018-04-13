"""Basic class for TreeGrower Algorithms"""

from abstractgrower import AbstractAlgo
from common import bif_methods
from tns.morphmath import sample
from tns.basic import round_num
import numpy as np


def _init_ph_angles(ph_angles):
    '''Returns the data to be used by TMD algorithms
    in the growth process.
    bif: round values for bifurcations
    term: round values for terminations
    angles: angle values for each corresponding bifurcation
    bt_all: linked bifurcation - termination round values
    '''
    bif = [round_num(i) for i in np.unique(np.array(ph_angles)[:, 1])[1:]] # bif[0] = 0 trivial.
    term = [round_num(i) for i in np.array(ph_angles)[:, 0]]
    angles = {round_num(p[1]): [p[2], p[3], p[4], p[5]] for p in ph_angles}
    bt_all = {round_num(p[1]): p[0] for p in ph_angles}

    return bif, term, angles, bt_all


class TMDAlgo(AbstractAlgo):
    """TreeGrower of TMD basic growth"""

    def __init__(self,
                 input_data,
                 parameters,
                 start_point):
        """
        TMD basic grower
        input_data: saves all the data required for the growth
        parameters: input parameters to be used by growth algorithm
        bif_method will be defined from the input parameters
        start_point: the coordinates of the first point of the tree
        """
        self.params = parameters
        self.bif_method = bif_methods[parameters["branching_method"]]
        self.ph_angles = sample.ph(input_data["persistence_diagram"])
        self.start_point = start_point

    def first_section(self):
        """Generates the data to be used for the initialization
        of the first section to be grown. Returns the initial stop
        criterion and the expected number of sections
        """
        bif, term, angles, bt_all = _init_ph_angles(self.ph_angles)

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

    def extend(self, currentSec):
        """Definition of stop criterion for the growth of the current section.
        """
        currentSec.stop_criteria["bif_term"]["bif"] = round_num(self.bif[0]) if self.bif else np.inf

        if currentSec.stop_criteria["bif_term"]["term"] not in self.term:
            currentSec.stop_criteria["bif_term"]["term"] = round_num(self.term[0]) if self.term else np.inf

        return currentSec.generate()


class TMDApicalAlgo(TMDAlgo):
    """TreeGrower of TMD apical growth"""

    def __init__(self,
                 input_data,
                 parameters,
                 start_point):
        """
        TMD apical grower; the tree grows using the TMD for branching
        but the bifurcation method depends on the formation of the obliques
        and the tuft.
        input_data: saves all the data required for the growth
        parameters: input parameters to be used by growth algorithm
        bif_method will be defined from the input parameters
        start_point: the coordinates of the first point of the tree
        """
        self.params = parameters
        self.bif_method = bif_methods[parameters["branching_method"]]
        self.ph_angles = sample.ph(input_data["persistence_diagram"])
        self.start_point = start_point


    def bifurcate(self, currentSec):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.bif.remove(currentSec.stop_criteria["bif_term"]["bif"])
        ang = self.angles[currentSec.stop_criteria["bif_term"]["bif"]]
        dir1, dir2 = self.bif_method(currentSec.direction, angles=ang)
        start_point = np.array(currentSec.points3D[-1])
        process = 'testapical'

        stop1 = {"bif_term": {"ref": self.start_point[:3],
                              "bif": self.bif[0] if self.bif else np.inf,
                              "term": round_num(currentSec.stop_criteria["bif_term"]["term"])}}

        stop2 = {"bif_term": {"ref": self.start_point[:3],
                              "bif": self.bif[0] if self.bif else np.inf,
                              "term": round_num(self.bt_all[currentSec.stop_criteria["bif_term"]["bif"]])}}

        s1 = {'direction': dir1,
              'start_point': start_point,
              'stop':stop1,
              'process': process}

        s2 = {'direction': dir2,
              'start_point': start_point,
              'stop':stop2,
              'process': process}

        return s1, s2
