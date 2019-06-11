"""Basic class for TreeGrower Algorithms based on path distance"""

import numpy as np

from tns.generate.algorithms.common import bif_methods, init_ph_angles
from tns.generate.algorithms.tmdgrower import TMDAlgo
from tns.morphmath.utils import norm


class TMDAlgoPath(TMDAlgo):
    """TreeGrower of TMD path dependent growth"""

    def metric_ref(self, section):
        """Returns the metric reference, here path distance reference,
           or zero if no section is provided as input.
        """
        # Function to return reference for path distance
        if section:
            return section.pathlength
        return 0.0

    def metric(self, section):
        """Returns the metric at the current position, here path distance
        """
        # Function to return path distance
        return section.pathlength

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


class TMDApicalAlgoPath(TMDAlgoPath):
    """TreeGrower of TMD apical growth"""

    def initialize(self):
        """
        TMD basic grower of an apical tree based on path distance
        Initializes the tree grower and
        computes the apical distance using the input barcode.
        """
        from tmd.Topology.analysis import find_apical_point_distance
        stop, num_sec = super(TMDApicalAlgoPath, self).initialize()
        self.params['apical_distance'] = find_apical_point_distance(self.ph_angles)
        return stop, num_sec

    def bifurcate(self, currentSec):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.bif.remove(currentSec.stop_criteria["bif_term"]["bif"])
        ang = self.angles[currentSec.stop_criteria["bif_term"]["bif"]]
        current_pd = self.metric(currentSec)

        if currentSec.process == 'major':
            dir1, dir2 = bif_methods['directional'](currentSec.direction, angles=ang)
            if current_pd <= self.params['apical_distance']:
                process1 = 'major'
                process2 = 'secondary'
            else:
                process1 = 'secondary'
                process2 = 'secondary'
        else:
            dir1, dir2 = self.bif_method(currentSec.history(), angles=ang)
            process1 = 'secondary'
            process2 = 'secondary'

        first_point = np.array(currentSec.points[-1])

        stop1, stop2 = self.get_stop_criteria(currentSec)

        s1 = {'direction': dir1,
              'first_point': first_point,
              'stop': stop1,
              'process': process1}

        s2 = {'direction': dir2,
              'first_point': first_point,
              'stop': stop2,
              'process': process2}

        return s1, s2


class TMDGradientAlgoPath(TMDApicalAlgoPath):
    """TreeGrower of TMD apical growth"""

    def bifurcate(self, currentSec):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.bif.remove(currentSec.stop_criteria["bif_term"]["bif"])
        ang = self.angles[currentSec.stop_criteria["bif_term"]["bif"]]
        current_pd = self.metric(currentSec)

        if currentSec.process == 'major':
            dir1, dir2 = bif_methods['directional'](currentSec.direction, angles=ang)
            if current_pd <= self.params['apical_distance']:
                process1 = 'major'
                process2 = 'secondary'
            else:
                process1 = 'secondary'
                process2 = 'secondary'
        else:
            dir1, dir2 = self.bif_method(currentSec.history(), angles=ang)
            process1 = 'secondary'
            process2 = 'secondary'

        def majorize_process(stop, process, input_dir):
            '''Currates the non-major processes to apply a gradient to large components'''
            difference = np.abs(stop["bif_term"]["bif"] - stop["bif_term"]["term"])
            if np.isinf(difference):
                difference = np.abs(stop["bif_term"]["term"] - self.metric(currentSec))
            if difference > self.params['bias_length']:
                direction1 = (1.0 - self.params['bias']) * np.array(input_dir)
                direction2 = self.params['bias'] * np.array(currentSec.direction)
                direct = np.add(direction1, direction2)
                return 'major', direct / norm(direct)
            return process, input_dir

        stop1, stop2 = self.get_stop_criteria(currentSec)

        if process1 != 'major':
            process1, dir1 = majorize_process(stop1, process1, dir1)
        if process2 != 'major':
            process2, dir2 = majorize_process(stop2, process2, dir2)

        first_point = np.array(currentSec.points[-1])

        s1 = {'direction': dir1,
              'first_point': first_point,
              'stop': stop1,
              'process': process1}

        s2 = {'direction': dir2,
              'first_point': first_point,
              'stop': stop2,
              'process': process2}

        return s1, s2
