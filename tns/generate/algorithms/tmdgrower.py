"""Basic class for TreeGrower Algorithms"""

import numpy as np

from tns.morphmath import sample
from tns.basic import round_num
from tns.generate.algorithms.common import init_ph_angles, bif_methods
from tns.generate.algorithms.abstractgrower import AbstractAlgo


class TMDAlgo(AbstractAlgo):
    """TreeGrower of TMD basic growth"""

    def __init__(self,
                 input_data,
                 bif_method,
                 start_point):
        """
        TMD basic grower
        input_data: saves all the data required for the growth
        bif_method: selects the bifurcation method used for the growth
        """

        self.bif_method = bif_methods[bif_method]
        self.ph_angles = sample.ph(input_data["persistence_diagram"])
        self.start_point = start_point
        self.bif = None
        self.term = None
        self.angles = None
        self.bt_all = None

    def initialize(self):
        """Generates the data to be used for the initialization
        of the first section to be grown. Saves the extracted
        input data into the corresponding structures.
        """
        bif, term, angles, bt_all = init_ph_angles(self.ph_angles)

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
        dirs = self.bif_method(currentSec.direction, angles=ang)
        start_point = np.array(currentSec.points3D[-1])

        stops = [{"bif_term": {"ref": self.start_point[:3],
                               "bif": self.bif[0] if self.bif else np.inf,
                               "term": round_num(term)}}
                 for term in [currentSec.stop_criteria["bif_term"]["term"],
                              self.bt_all[currentSec.stop_criteria["bif_term"]["bif"]]]]

        return [{'direction': direction,
                 'start_point': start_point,
                 'stop': stop,
                 'process': currentSec.process} for direction, stop in zip(dirs, stops)]

    def terminate(self, currentSec):
        """When the growth of a section is terminated the "term"
        must be removed from the TMD grower
        """
        self.term.remove(currentSec.stop_criteria["bif_term"]["term"])

    def extend(self, currentSec):
        """Definition of stop criterion for the growth of the current section.
        """
        bif_term = currentSec.stop_criteria["bif_term"]
        bif_term["bif"] = round_num(self.bif[0]) if self.bif else np.inf

        if bif_term["term"] not in self.term:
            bif_term["term"] = round_num(self.term[0]) if self.term else np.inf

        return currentSec.generate()


class TMDApicalAlgo(TMDAlgo):
    """TreeGrower of TMD apical growth"""

    def bifurcate(self, currentSec):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.bif.remove(currentSec.stop_criteria["bif_term"]["bif"])
        ang = self.angles[currentSec.stop_criteria["bif_term"]["bif"]]

        current_rd = np.linalg.norm(np.subtract(currentSec.points3D[-1], self.start_point))

        if currentSec.process=='major':
            dir1, dir2 = bif_methods['directional'](currentSec.direction, angles=ang)
            if current_rd <= self.params['apical_distance']:
                process1 = 'major'
                process2 = 'secondary'
            else:
                process1 = 'secondary'
                process2 = 'secondary'
        else:
            dir1, dir2 = self.bif_method(currentSec.direction, angles=ang)
            process1 = 'secondary'
            process2 = 'secondary'

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
              'process': process1}

        s2 = {'direction': dir2,
              'start_point': start_point,
              'stop':stop2,
              'process': process2}

        return s1, s2
