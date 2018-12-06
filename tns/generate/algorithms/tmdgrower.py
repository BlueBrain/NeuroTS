"""Basic class for TreeGrower Algorithms"""

import numpy as np

from tns.morphmath import sample
from tns.basic import round_num
from tns.generate.algorithms.common import init_ph_angles, bif_methods
from tns.generate.algorithms.abstractgrower import AbstractAlgo
from tns.morphmath.utils import norm


class TMDAlgo(AbstractAlgo):
    """TreeGrower of TMD basic growth"""

    def __init__(self,
                 input_data,
                 params,
                 start_point):
        """
        TMD basic grower
        input_data: saves all the data required for the growth
        params: parameters needed for growth, it should include the bif_method
        bifurcation method, select from: bio_oriented, symmetric, directional
        """
        self.bif_method = bif_methods[params["branching_method"]]
        self.params = params
        self.ph_angles = sample.ph(input_data["persistence_diagram"])
        if params['modify']:
            self.ph_angles = params['modify']['funct'](self.ph_angles,
                                                       **params['modify']['kwargs'])
        self.start_point = start_point
        self.bif = None
        self.term = None
        self.angles = None
        self.bt_all = None

    def curate_bif(self, stop, currentBF, currentTR):
        '''Checks if selected bar is smaller than current bar length.
           Returns the smallest bifurcation for which the length of the bar
           is smaller than current one.
           If there are no bif left or if the bif is largest than the current
           termination target the np.inf is returned instead.
        currentSec.stop_criteria["bif_term"]
        '''
        current_length = np.abs(stop["term"] - stop["bif"])
        target_length = np.abs(currentTR - currentBF)

        if not self.bif or target_length==np.inf:
            return np.inf
        if target_length <= current_length:
            return currentBF
        for b in self.bif:
            target_length = np.abs(currentTR - b)
            if target_length <= current_length:
                return b
        return np.inf

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

        stop1 = {"bif_term": {"ref": self.start_point[:3],
                              "bif": b1,
                              "term": round_num(currentSec.stop_criteria["bif_term"]["term"])}}

        b2 = self.curate_bif(currentSec.stop_criteria["bif_term"], currentBF,
                             round_num(self.bt_all[currentSec.stop_criteria["bif_term"]["bif"]]))

        stop2 = {"bif_term": {"ref": self.start_point[:3],
                              "bif": b2,
                              "term": round_num(self.bt_all[currentSec.stop_criteria["bif_term"]["bif"]])}}

        return (stop1, stop2)

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
        dir1, dir2 = self.bif_method(currentSec.history(), angles=ang)
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

    def terminate(self, currentSec):
        """When the growth of a section is terminated the "term"
        must be removed from the TMD grower
        """
        self.term.remove(currentSec.stop_criteria["bif_term"]["term"])
        #print 'B: ', currentSec.stop_criteria["bif_term"]["bif"],
        #print ' & removed T: ', currentSec.stop_criteria["bif_term"]["term"]

    def extend(self, currentSec):
        """Definition of stop criterion for the growth of the current section.
        """
        bif_term = currentSec.stop_criteria["bif_term"]

        if bif_term["bif"] not in self.bif and bif_term["bif"] != np.inf:
            currentSec.stop_criteria["bif_term"]["bif"] = self.curate_bif(currentSec.stop_criteria["bif_term"],
                                                                          self.bif[0] if self.bif else np.inf,
                                                                          round_num(bif_term["term"]))

        if bif_term["term"] not in self.term and bif_term["term"] != np.inf:
            currentSec.stop_criteria["bif_term"]["term"] = np.min(self.term) if self.term else np.inf

        return currentSec.next()


class TMDApicalAlgo(TMDAlgo):
    """TreeGrower of TMD apical growth"""

    def initialize(self):
        """
        TMD basic grower of an apical tree
        Initializes the tree grower and
        computes the apical distance using the input barcode.
        """
        from tmd.Topology.analysis import find_apical_point_distance
        stop, num_sec = super(TMDApicalAlgo, self).initialize()
        self.params['apical_distance'] = find_apical_point_distance(self.ph_angles)
        return stop, num_sec

    def bifurcate(self, currentSec):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.bif.remove(currentSec.stop_criteria["bif_term"]["bif"])
        ang = self.angles[currentSec.stop_criteria["bif_term"]["bif"]]

        current_rd = norm(np.subtract(currentSec.points3D[-1], self.start_point))

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

class TMDGradientAlgo(TMDApicalAlgo):
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
            dir1, dir2 = self.bif_method(currentSec.history(), angles=ang)
            process1 = 'secondary'
            process2 = 'secondary'

        start_point = np.array(currentSec.points3D[-1])

        def majorize_process(stop, process, input_dir):
            difference = np.abs(stop["bif_term"]["bif"] - stop["bif_term"]["term"])
            if difference > self.params['bias_length'] and difference != np.inf:
                direction1 = (1.0 - self.params['bias']) * np.array(input_dir)
                direction2 = self.params['bias'] * np.array(currentSec.direction)
                direct = np.add(direction1, direction2)
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
