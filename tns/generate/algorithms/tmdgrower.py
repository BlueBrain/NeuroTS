"""Basic class for TreeGrower Algorithms"""

import copy
import numpy as np

from tns.generate.algorithms.abstractgrower import AbstractAlgo
from tns.generate.algorithms.common import bif_methods
from tns.generate.algorithms.common import TMDStop
from tns.morphmath import sample
from tns.morphmath.utils import norm
from tns.generate.algorithms.barcode import Barcode


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

        self.barcode = Barcode(list(self.ph_angles))
        self.start_point = start_point

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

    def curate_bif(self, stop, target):
        '''Checks if selected bar is smaller than current bar length.
           Returns the smallest bifurcation for which the length of the bar
           is smaller than current one.
           If there are no bif left or if the bif is largest than the current
           termination target the np.inf is returned instead.
        currentSec.stop_criteria["TMD"]
        '''
        target_stop = copy.deepcopy(target)
        # Compute length of current section
        current_length = stop.child_length()
        # Compute target length of children
        target_length = target_stop.child_length()

        # There are no bifurcations to check
        if not self.barcode.bifs or np.isinf(target_stop.bif):
            target_stop.update_bif(None, np.inf)
            return target_stop
        # If child length smaller than parent
        if target_length <= current_length:
            return target_stop
        # Else find the next bif for which child length
        # is smaller than parent
        for bar_id, bar_bif in self.barcode.bifs.items():
            target_length = np.abs(target_stop.term - bar_bif)
            if target_length <= current_length:
                target_stop.update_bif(bar_id, bar_bif)
                return target_stop
        target_stop.update_bif(None, np.inf)
        return target_stop

    def get_stop_criteria(self, currentSec):
        """Returns stop1 and stop2 that are the commonly
           shared stop criteria for all TMDPath algorithms.
           stop["TMD"] = {ref: the current path distance
                             bif: the smallest appropriate bifurcation path length
                             term: the appropriate termination path length
                            }
        """
        current_tmd = copy.deepcopy(currentSec.stop_criteria["TMD"])
        bif_id, bif = self.barcode.min_bif()

        target_stop = TMDStop(ref=self.metric_ref(currentSec),
                              bif_id=bif_id,
                              bif=bif,
                              term_id=current_tmd.term_id,
                              term=current_tmd.term)

        target_stop1 = self.curate_bif(currentSec.stop_criteria["TMD"], target_stop)
        stop1 = {"TMD": target_stop1}

        target_stop = TMDStop(ref=self.metric_ref(currentSec),
                              bif_id=bif_id,
                              bif=bif,
                              term_id=current_tmd.bif_id,
                              term=self.barcode.terms[current_tmd.bif_id])

        target_stop2 = self.curate_bif(currentSec.stop_criteria["TMD"], target_stop)
        stop2 = {"TMD": target_stop2}

        return (stop1, stop2)

    def initialize(self):
        """Generates the data to be used for the initialization
        of the first section to be grown. Saves the extracted
        input data into the corresponding structures.
        """
        b0_id, b0 = self.barcode.min_bif()
        t0_id, t0 = self.barcode.max_term()
        stop = {"TMD": TMDStop(ref=self.metric_ref(None),
                               bif_id=b0_id,
                               bif=b0,
                               term_id=t0_id,
                               term=t0)
                }

        num_sec = len(self.ph_angles)

        return stop, num_sec

    def bifurcate(self, currentSec):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.barcode.remove_bif(currentSec.stop_criteria["TMD"].bif_id)
        ang = self.barcode.angles[currentSec.stop_criteria["TMD"].bif_id]

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
        self.barcode.remove_term(currentSec.stop_criteria["TMD"].term_id)

    def extend(self, currentSec):
        """Definition of stop criterion for the growth of the current section.
        """
        criteria_tmd = copy.deepcopy(currentSec.stop_criteria["TMD"])

        # First we check that the current termination has not been used
        if criteria_tmd.term_id not in self.barcode.terms:
            criteria_tmd.update_term(*self.barcode.min_term())

        # Then we check that the current bifurcation has not been used
        if criteria_tmd.bif_id not in self.barcode.bifs and not np.isinf(criteria_tmd.bif):
            criteria_tmd.update_bif(*self.barcode.min_bif())
            criteria_tmd = self.curate_bif(currentSec.stop_criteria["TMD"], criteria_tmd)

        currentSec.stop_criteria["TMD"] = criteria_tmd

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
        self.barcode.remove_bif(currentSec.stop_criteria["TMD"].bif_id)
        ang = self.barcode.angles[currentSec.stop_criteria["TMD"].bif_id]

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
        self.barcode.remove_bif(currentSec.stop_criteria["TMD"].bif_id)
        ang = self.barcode.angles[currentSec.stop_criteria["TMD"].bif_id]

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
            difference = np.abs(stop["TMD"].bif - stop["TMD"].term)
            if difference == np.inf:
                difference = np.abs(stop["TMD"].term - self.metric(currentSec))
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
