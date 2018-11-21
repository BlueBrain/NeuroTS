"""Basic class for TreeGrower Algorithms based on path distance"""

import numpy as np

from tns.morphmath import sample
from tns.basic import round_num
from tns.generate.algorithms.common import init_ph_angles, bif_methods
from tns.generate.algorithms.tmdgrower import TMDAlgo


class TMDAlgoPath(TMDAlgo):
    """TreeGrower of TMD path dependent growth"""

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

        stop = {"bif_term": {"ref": 0,
                             "bif": self.bif[0],
                             "term": self.term[-1]}}

        num_sec = len(self.ph_angles)

        return stop, num_sec

    def get_stop_criteria(self, currentSec):
        """Returns stop1 and stop2 that are the commonly
           shared stop criteria for all TMDPath algorithms.
           stop[bif_term] = {ref: the current path distance
                             bif: the smallest appropriate bifurcation path length
                             term: the appropriate termination path length
                            }
        """
        currentBF = self.bif[0] if len(self.bif) > 1 else np.inf

        b1 = self.curate_bif(currentSec.stop_criteria["bif_term"], currentBF,
                             round_num(currentSec.stop_criteria["bif_term"]["term"]))

        stop1 = {"bif_term": {"ref": currentSec.pathlength,
                              "bif": b1,
                              "term": round_num(currentSec.stop_criteria["bif_term"]["term"])}}

        b2 = self.curate_bif(currentSec.stop_criteria["bif_term"], currentBF,
                             round_num(self.bt_all[currentSec.stop_criteria["bif_term"]["bif"]]))

        stop2 = {"bif_term": {"ref": currentSec.pathlength,
                              "bif": b2,
                              "term": round_num(self.bt_all[currentSec.stop_criteria["bif_term"]["bif"]])}}

        return (stop1, stop2)

    def bifurcate(self, currentSec):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.bif.remove(currentSec.stop_criteria["bif_term"]["bif"])

        ang = self.angles[currentSec.stop_criteria["bif_term"]["bif"]]
        dir1, dir2 = self.bif_method(currentSec.get_current_direction(), angles=ang)

        start_point = np.array(currentSec.points3D[-1])

        stop1, stop2 = self.get_stop_criteria(currentSec)

        s1 = {'direction': dir1,
              'start_point': start_point,
              'stop':stop1,
              'process': currentSec.process}

        s2 = {'direction': dir2,
              'start_point': start_point,
              'stop':stop2,
              'process': currentSec.process}

        return s1, s2

class TMDApicalAlgoPath(TMDAlgoPath):
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
            dir1, dir2 = self.bif_method(currentSec.get_current_direction(), angles=ang)
            process1 = 'secondary'
            process2 = 'secondary'

        start_point = np.array(currentSec.points3D[-1])

        stop1, stop2 = self.get_stop_criteria(currentSec)

        s1 = {'direction': dir1,
              'start_point': start_point,
              'stop':stop1,
              'process':process1}

        s2 = {'direction': dir2,
              'start_point': start_point,
              'stop':stop2,
              'process': process2}

        return s1, s2


class TMDGradientAlgoPath(TMDAlgoPath):
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
            dir1, dir2 = self.bif_method(currentSec.get_current_direction(), angles=ang)
            process1 = 'secondary'
            process2 = 'secondary'

        def majorize_process(stop, process, input_dir):
            difference = np.abs(stop["bif_term"]["bif"] - stop["bif_term"]["term"])
            if difference == np.inf:
                difference = np.abs(stop["bif_term"]["term"] - currentSec.pathlength)
            if difference > self.params['bias_length']:
                direction1 = (1.0 - self.params['bias']) * np.array(input_dir)
                direction2 = self.params['bias'] * np.array(currentSec.direction)
                direct = np.add(direction1, direction2).tolist()
                return 'major', direct
            else:
                return process, input_dir

        stop1, stop2 = self.get_stop_criteria(currentSec)

        if process1 != 'major':
            process1, dir1 = majorize_process(stop1, process1, dir1)
        process2, dir2 = majorize_process(stop2, process2, dir2)

        start_point = np.array(currentSec.points3D[-1])

        s1 = {'direction': dir1,
              'start_point': start_point,
              'stop':stop1,
              'process':process1}

        s2 = {'direction': dir2,
              'start_point': start_point,
              'stop':stop2,
              'process': process2}

        return s1, s2
