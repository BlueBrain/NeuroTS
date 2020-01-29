"""Basic class for TreeGrower Algorithms"""

import copy
import numpy as np

from tns.generate.algorithms.abstractgrower import AbstractAlgo
from tns.generate.algorithms.common import bif_methods
from tns.generate.algorithms.common import TMDStop
from tns.generate.algorithms.common import section_data
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
        self.params = copy.deepcopy(params)
        self.ph_angles = sample.ph(input_data["persistence_diagram"])
        if params.get('modify'):
            self.ph_angles = params['modify']['funct'](self.ph_angles,
                                                       **params['modify']['kwargs'])
        self.barcode = Barcode(list(self.ph_angles))
        self.start_point = start_point
        self.apical_point = None
        self.apical_point_distance_from_soma = 0.0

    @staticmethod
    def metric_ref(section):
        """Returns the metric reference, here path distance reference,
           or zero if no section is provided as input.
        """
        # Function to return reference for path distance
        if section:
            return section.pathlength
        return 0.0

    @staticmethod
    def metric(section):
        """Returns the metric at the current position,
           here path distance, recorded in section
        """
        # Function to return path distance
        return section.pathlength

    def get_stop_criteria(self, current_section):
        """Returns stop1 and stop2 that are the commonly
           shared stop criteria for all TMDPath algorithms.
           stop["TMD"] = {ref: the current path distance
                          bif: the smallest appropriate bifurcation path length
                          term: the appropriate termination path length
                          }
        """
        # Ensure that reference is correctly assigned
        current_section.stop_criteria["TMD"].ref = self.metric_ref(current_section)
        # Copy the values for the parent stop TMD to use
        parent_tmd = copy.deepcopy(current_section.stop_criteria["TMD"])
        # Save the values of bifurcation for parent
        parent_bif_id = parent_tmd.bif_id
        parent_bif = parent_tmd.bif
        # Define the current criterion, inherited from parent
        current_tmd = copy.deepcopy(current_section.stop_criteria["TMD"])

        # The termination remains the same, so it is always True that
        # current_tmd.term <= parent_tmd.term
        # We find the smallest bifurcation that fulfils requirements
        # parent_tmd.ref <= current_tmd.bif <= parent_tmd.term
        # Bifurcation is larger than current reference distance
        bif_id, bif = self.barcode.min_bif(bif_above=parent_tmd.ref,
                                           bif_below=parent_tmd.term)
        # Update the bifurcation in the stop_criterion
        current_tmd.update_bif(bif_id, bif)
        # Ensure that criterion fulfils all requirements
        # the term that corresponds to current_tmd.bif term_target
        # term_target <= parent_tmd.term
        # If not re-assign a new one, find the min bifurcation for which:
        # term_target <= parent_tmd.term
        target_stop1 = self.barcode.curate_stop_criterion(parent_tmd,
                                                          current_tmd)
        stop1 = {"TMD": target_stop1}
        # Find the termination that fulfils the requirement
        # termination <= current termination

        # Use the current bifurcation to determine the respective termination
        # Bifurcation should be larger than current reference distance
        term_id, term = self.barcode.get_term_between(parent_bif_id,
                                                      parent_bif,
                                                      current_tmd.term)
        current_tmd.update_term(term_id, term)

        # Get a stop criterion that fulfils requirements
        target_stop2 = self.barcode.curate_stop_criterion(parent_tmd,
                                                          current_tmd)
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

    def bifurcate(self, current_section):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.barcode.remove_bif(current_section.stop_criteria["TMD"].bif_id)
        ang = self.barcode.angles[current_section.stop_criteria["TMD"].bif_id]

        dir1, dir2 = self.bif_method(current_section.history(), angles=ang)
        first_point = np.array(current_section.last_point)

        stop1, stop2 = self.get_stop_criteria(current_section)

        return section_data(dir1, first_point, stop1, current_section.process), \
               section_data(dir2, first_point, stop2, current_section.process)

    def terminate(self, current_section):
        """When the growth of a section is terminated the "term"
        must be removed from the TMD grower
        """
        self.barcode.remove_term(current_section.stop_criteria["TMD"].term_id)

    def extend(self, current_section):
        """Definition of stop criterion for the growth of the current section.
        """
        criteria_tmd = copy.deepcopy(current_section.stop_criteria["TMD"])
        maximum_target = current_section.stop_criteria["TMD"].term
        reference = current_section.stop_criteria["TMD"].ref

        # We check that the current bifurcation has not been used
        if criteria_tmd.bif_id not in self.barcode.bifs and not np.isinf(criteria_tmd.bif):
            criteria_tmd.update_bif(*self.barcode.min_bif(bif_above=reference,
                                                          bif_below=maximum_target))
            criteria_tmd = self.barcode.curate_stop_criterion(criteria_tmd,
                                                              criteria_tmd)

        # We check that the current termination has not been used
        if criteria_tmd.term_id not in self.barcode.terms:
            # Termination must be larger that bifurcation
            # unless if bifurcation is infinite
            reference = criteria_tmd.bif if not np.isinf(criteria_tmd.bif) else criteria_tmd.ref
            criteria_tmd.update_term(*self.barcode.min_term(term_above=reference,
                                                            term_below=maximum_target))
            criteria_tmd = self.barcode.curate_stop_criterion(criteria_tmd,
                                                              criteria_tmd)

        current_section.stop_criteria["TMD"] = criteria_tmd

        return current_section.next()


class TMDApicalAlgo(TMDAlgo):
    """TreeGrower of TMD apical growth"""

    def initialize(self):
        """
        TMD basic grower of an apical tree based on path distance
        Initializes the tree grower and
        computes the apical distance using the input barcode.
        """
        from tmd.Topology.analysis import find_apical_point_distance
        stop, num_sec = super(TMDApicalAlgo, self).initialize()
        self.apical_point_distance_from_soma = find_apical_point_distance(self.ph_angles)
        return stop, num_sec

    def bifurcate(self, current_section):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.barcode.remove_bif(current_section.stop_criteria["TMD"].bif_id)
        ang = self.barcode.angles[current_section.stop_criteria["TMD"].bif_id]
        current_pd = self.metric(current_section)
        first_point = np.array(current_section.last_point)

        if current_section.process == 'major':
            dir1, dir2 = bif_methods['directional'](current_section.direction, angles=ang)
            if current_pd <= self.apical_point_distance_from_soma:
                process1 = 'major'
                process2 = 'secondary'
            else:
                if self.apical_point is None:
                    self.apical_point = first_point
                process1 = 'secondary'
                process2 = 'secondary'
        else:
            dir1, dir2 = self.bif_method(current_section.history(), angles=ang)
            process1 = 'secondary'
            process2 = 'secondary'

        stop1, stop2 = self.get_stop_criteria(current_section)

        return section_data(dir1, first_point, stop1, process1), \
               section_data(dir2, first_point, stop2, process2)


class TMDGradientAlgo(TMDApicalAlgo):
    """TreeGrower of TMD apical growth"""

    def _majorize_process(self, section, stop, process, input_dir):
        '''Currates the non-major processes to apply a gradient to large components'''
        difference = stop.expected_maximum_length()
        if difference > self.params['bias_length']:
            direction1 = (1.0 - self.params['bias']) * np.array(input_dir)
            direction2 = self.params['bias'] * np.array(section.direction)
            direct = np.add(direction1, direction2)
            return 'major', direct / norm(direct)
        return process, input_dir

    def bifurcate(self, current_section):
        """When the section bifurcates two new sections need to be created.
        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        s1, s2 = super(TMDGradientAlgo, self).bifurcate(current_section)

        if s1['process'] != 'major':
            s1['process'], s1['direction'] = self._majorize_process(current_section,
                                                                    s1['stop']["TMD"],
                                                                    s1['process'],
                                                                    s1['direction'])
        if s2['process'] != 'major':
            s2['process'], s2['direction'] = self._majorize_process(current_section,
                                                                    s2['stop']["TMD"],
                                                                    s2['process'],
                                                                    s2['direction'])
        return s1, s2
