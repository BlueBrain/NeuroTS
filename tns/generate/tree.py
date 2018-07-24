'''
TNS class : Tree
'''
import copy
from enum import Enum

import numpy as np
from morphio import PointLevel, SectionType

from tns.generate.algorithms import basicgrower, tmdgrower
from tns.generate.section import SectionGrower
from tns.morphmath import random_tree as rd
from tns.morphmath import rotation

growth_algorithms = {'tmd': tmdgrower.TMDAlgo,
                     'tmd_apical': tmdgrower.TMDApicalAlgo,
                     'trunk': basicgrower.TrunkAlgo}


class TreeGrower(object):
    """Tree class"""

    def __init__(self,
                 neuron,
                 initial_direction,
                 initial_point,
                 parameters,
                 distributions):
        """TNS Tree Object

        Parameters:
            neuron: Obj neuron where groups and points are stored
            initial_direction: 3D vector
            initial_point: 3D vector that defines the starting point of the tree
            parameters including: tree_type, radius, randomness, targeting, apical_distance
            tree_type: an integer indicating the type (choose from 2, 3, 4, 5)
        """
        self.neuron = neuron
        self.direction = initial_direction
        self.point = list(initial_point)
        self.type = parameters["tree_type"]  # 2: axon, 3: basal, 4: apical, 5: other
        self.params = parameters
        self.distr = distributions
        self.active_sections = set()
        grow_meth = growth_algorithms[self.params["growth_method"]]

        self.growth_algo = grow_meth(input_data=self.distr,
                                     bif_method=self.params["branching_method"],
                                     start_point=self.point)

        stop, num_sec = self.growth_algo.initialize()

        self.add_section(parent=None,
                         direction=self.direction,
                         start_point=list(self.point),
                         stop=copy.deepcopy(stop),
                         children=2 if num_sec > 1 else 0)

    def add_section(self, parent, direction, start_point, stop, process=None, children=0):
        """Generates a section from the parent section "act"
        from all the required information. The section is
        added to the neuron.sections and activated.
        """
        self.active_sections.add(SectionGrower(parent=parent,
                                               start_point=start_point,
                                               direction=direction,
                                               randomness=self.params["randomness"],
                                               targeting=self.params["targeting"],
                                               children=children,
                                               process=process,
                                               stop_criteria=copy.deepcopy(stop)))

    def end(self):
        return not bool(self.active_sections)

    def next(self):
        '''Operates the tree growth according to the selected algorithm.
        '''

        for section_grower in self.active_sections.copy():
            # the current section_grower is generated
            # In here the stop criterion can be modified accordingly
            state = self.growth_algo.extend(section_grower)

            section = self.neuron.append_section(
                section_grower.parent,
                PointLevel(np.array(section_grower.points3D).tolist(),
                           [self.params['radius'] * 2] * len(section_grower.points3D)),
                SectionType(self.params['tree_type']))

            if state == 'bifurcate':
                # the current section_grower bifurcates
                # Returns two section_grower dictionaries: (S1, S2)
                for child_section in self.growth_algo.bifurcate(section_grower):
                    self.add_section(parent=section, **child_section)
                self.active_sections.remove(section_grower)

            elif state == 'terminate':
                # the current section_grower terminates
                self.growth_algo.terminate(section_grower)
                self.active_sections.remove(section_grower)