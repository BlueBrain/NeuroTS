"""Basic class for TreeGrower Algorithms"""

import numpy as np

from tns.basic import round_num
from tns.generate.algorithms.abstractgrower import AbstractAlgo
from tns.generate.algorithms.common import bif_methods, init_ph_angles
from tns.morphmath import sample
from tns.morphmath.utils import norm


class TMDAlgo(AbstractAlgo):
    """TreeGrower of TMD basic growth"""

    def __init__(self, input_data, params, start_point, context=None):
        """
        TMD basic grower
        input_data: saves all the data required for the growth
        params: parameters needed for growth, it should include the bif_method
        bifurcation method, select from: bio_oriented, symmetric, directional
        context: an object containing contextual information
        """
        super(TMDAlgo, self).__init__(input_data, params, start_point, context)
        self.bif_method = bif_methods[params["branching_method"]]
        self.params = params
        self.ph_angles = sample.ph(input_data["persistence_diagram"])
        if params.get('modify'):
            self.ph_angles = params['modify']['funct'](self.ph_angles,
                                                       **params['modify']['kwargs'])
        self.start_point = start_point
        self.bif = None
        self.term = None
        self.angles = None
        self.bt_all = None

    def metric_ref(self, section):
        """Returns the metric reference, here radial distance reference.
           Section is input for consistency with path distance
        """
        # pylint: disable=unused-argument
        # Function to return reference for path distance
        return self.start_point

    def metric(self, section):
        """Returns the metric at the current position, here radial distance
        """
        # Function to return path distance
        return norm(np.subtract(section.points[-1], self.start_point))

    def curate_bif(self, stop, target_bif, target_term):
        '''Checks if selected bar is smaller than current bar length.
           Returns the smallest bifurcation for which the length of the bar
           is smaller than current one.
           If there are no bif left or if the bif is largest than the current
           termination target the np.inf is returned instead.
        currentSec.stop_criteria["bif_term"]
        '''
        # Compute length of current section
        current_length = np.abs(stop["term"] - stop["bif"])
        # Compute target length of children
        target_length = np.abs(target_bif - target_term)

        # There are no bifurcations to check
        if not self.bif or np.isinf(target_length):
            return np.inf
        # If child length smaller than parent
        if target_length <= current_length:
            return target_bif
        # Else find the next bif for which child length
        # is smaller than parent
        for b in self.bif:
            target_length = np.abs(target_term - b)
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
        target_bif = self.bif[0] if len(self.bif) > 1 else np.inf

        b1 = self.curate_bif(currentSec.stop_criteria["bif_term"], target_bif,
                             round_num(currentSec.stop_criteria["bif_term"]["term"]))

        stop1 = {"bif_term": {"ref": self.metric_ref(currentSec),
                              "bif": b1,
                              "term": round_num(currentSec.stop_criteria["bif_term"]["term"])}}

        b2 = self.curate_bif(currentSec.stop_criteria["bif_term"], target_bif,
                             round_num(self.bt_all[currentSec.stop_criteria["bif_term"]["bif"]]))

        stop2 = {"bif_term": {"ref": self.metric_ref(currentSec),
                              "bif": b2,
                              "term": round_num(
                                  self.bt_all[currentSec.stop_criteria["bif_term"]["bif"]])}}

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

        stop = {"bif_term": {"ref": self.metric_ref(None),
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
        first_point = np.array(currentSec.points[-1])

        stop1, stop2 = self.get_stop_criteria(currentSec)

        s1 = {'direction': dir1,
              'first_point': first_point,
              'stop': stop1,
              'process': currentSec.process}

        s2 = {'direction': dir2,
              'first_point': first_point,
              'stop': stop2,
              'process': currentSec.process}

        return s1, s2

    def terminate(self, currentSec):
        """When the growth of a section is terminated the "term"
        must be removed from the TMD grower
        """
        self.term.remove(currentSec.stop_criteria["bif_term"]["term"])
        # print 'B: ', currentSec.stop_criteria["bif_term"]["bif"],
        # print ' & removed T: ', currentSec.stop_criteria["bif_term"]["term"]

    def extend(self, currentSec):
        """Definition of stop criterion for the growth of the current section.
        """
        bif_term = currentSec.stop_criteria["bif_term"]

        # First we check that the current termination has not been used
        if bif_term["term"] not in self.term and not np.isinf(bif_term["term"]):
            currentSec.stop_criteria["bif_term"]["term"] = np.min(
                self.term) if self.term else np.inf

        # Then we check that the current bifurcation has not been used
        if bif_term["bif"] not in self.bif and not np.isinf(bif_term["bif"]):
            currentSec.stop_criteria["bif_term"]["bif"] = self.curate_bif(
                currentSec.stop_criteria["bif_term"],
                self.bif[0] if self.bif else np.inf,
                round_num(bif_term["term"]))

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

        current_rd = self.metric(currentSec)

        if currentSec.process == 'major':
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


class TMDGradientAlgo(TMDApicalAlgo):
    """TreeGrower of TMD apical growth"""

    def bifurcate(self, currentSec):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.bif.remove(currentSec.stop_criteria["bif_term"]["bif"])
        ang = self.angles[currentSec.stop_criteria["bif_term"]["bif"]]

        current_rd = self.metric(currentSec)

        if currentSec.process == 'major':
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

        def majorize_process(stop, process, input_dir):
            '''Currates the non-major processes to apply a gradient to large components'''
            difference = np.abs(stop["bif_term"]["bif"] - stop["bif_term"]["term"])
            if difference == np.inf:
                difference = np.abs(stop["bif_term"]["term"] - self.metric(currentSec))
            if difference > self.params['bias_length'] and difference != np.inf:
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
