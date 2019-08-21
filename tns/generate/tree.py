'''
TNS class : Tree
'''
import copy

import numpy as np

from morphio import PointLevel, SectionType
from tns.generate.algorithms import basicgrower, tmdgrower, tmdgrower_path
from tns.generate.section import (SectionGrower, SectionGrowerPath,
                                  SectionGrowerTMD)

growth_algorithms = {'tmd': tmdgrower.TMDAlgo,
                     'tmd_apical': tmdgrower.TMDApicalAlgo,
                     'tmd_gradient': tmdgrower.TMDGradientAlgo,
                     'tmd_path': tmdgrower_path.TMDAlgoPath,
                     'tmd_apical_path': tmdgrower_path.TMDApicalAlgoPath,
                     'tmd_gradient_path': tmdgrower_path.TMDGradientAlgoPath,
                     'trunk': basicgrower.TrunkAlgo}

section_growers = {'tmd': SectionGrowerTMD,
                   'tmd_apical': SectionGrowerTMD,
                   'tmd_gradient': SectionGrowerTMD,
                   'tmd_path': SectionGrowerPath,
                   'tmd_apical_path': SectionGrowerPath,
                   'tmd_gradient_path': SectionGrowerPath,
                   'trunk': SectionGrower}


class TreeGrower(object):
    """Tree class"""

    def __init__(self,
                 neuron,
                 initial_direction,
                 initial_point,
                 parameters,
                 distributions,
                 context=None):
        """TNS Tree Object

        Parameters:
            neuron: Obj neuron where groups and points are stored
            initial_direction: 3D vector
            initial_point: 3D vector that defines the starting point of the tree
            parameters including: tree_type, radius, randomness, targeting, apical_distance
            tree_type: an integer indicating the type (choose from 2, 3, 4, 5)
            context: an object containing contextual information
        """
        self.neuron = neuron
        self.direction = initial_direction
        self.point = list(initial_point)
        self.type = parameters["tree_type"]  # 2: axon, 3: basal, 4: apical, 5: other
        self.params = parameters
        self.distr = distributions
        self.active_sections = list()
        self.context = context
        grow_meth = growth_algorithms[self.params["growth_method"]]

        self.growth_algo = grow_meth(input_data=self.distr,
                                     params=self.params,
                                     start_point=self.point,
                                     context=context)
        stop, num_sec = self.growth_algo.initialize()

        _ = self.add_section(parent=None,
                             direction=self.direction,
                             first_point=list(self.point),
                             stop=copy.deepcopy(stop),
                             process='major',
                             children=2 if num_sec > 1 else 0)

    def add_section(self, parent, direction, first_point, stop, process=None, children=0):
        """Generates a section from the parent section "act"
        from all the required information. The section is
        added to the neuron.sections and activated.
        """
        SGrower = section_growers[self.params['growth_method']]

        sec_grower = SGrower(parent=parent,
                             first_point=first_point,
                             direction=direction,
                             randomness=self.params["randomness"],
                             targeting=self.params["targeting"],
                             children=children,
                             process=process,
                             stop_criteria=copy.deepcopy(stop),
                             context=self.context)

        self.active_sections.append(sec_grower)
        return sec_grower

    def end(self):
        '''Ends the growth'''
        return not bool(self.active_sections)

    @staticmethod
    def order_per_process(secs):
        '''Orders sections according to process type, major first'''
        return np.copy(secs)[np.argsort([ss.process for ss in secs])]

    @staticmethod
    def order_per_bif(secs):
        '''Orders sections according to bifurcation times'''
        ordered_list = np.argsort([ss.stop_criteria["TMD"]['bif'] for ss in secs])
        return np.copy(secs)[ordered_list]

    def append_section(self, section):
        '''Append section to the MorphIO neuron'''
        if section.parent:
            append_fun = section.parent.append_section
        else:
            append_fun = self.neuron.append_root_section

        return append_fun(PointLevel(np.array(section.points).tolist(),
                                     [self.params['radius'] * 2] * len(section.points)),
                          SectionType(self.params['tree_type']))

    def next_point(self):
        '''Operates the tree growth according to the selected algorithm.
        '''
        if not isinstance(self.growth_algo, basicgrower.TrunkAlgo):
            ordered_sections = self.order_per_bif(self.active_sections)
        else:
            # TrunkAlgo does not keep track of the bifurcations so it is not
            # possible to order per bifurcation
            ordered_sections = np.copy(self.active_sections)

        for section_grower in ordered_sections:
            # the current section_grower is generated
            # In here the stop criterion can be modified accordingly
            state = self.growth_algo.extend(section_grower)

            if state != 'continue':
                section = self.append_section(section_grower)

                if state == 'bifurcate':
                    # Save the final normed direction of parent
                    latest = section_grower.latest_directions_normed[-1]
                    latest_un = section_grower.latest_directions[-1]
                    # the current section_grower bifurcates
                    # Returns two section_grower dictionaries: (S1, S2)
                    for child_section in self.growth_algo.bifurcate(section_grower):
                        child = self.add_section(parent=section, **child_section)
                        # Copy the final normed direction of parent to all children
                        child.latest_directions_normed.append(latest)
                        child.latest_directions.append(latest_un)
                    self.active_sections.remove(section_grower)

                elif state == 'terminate':
                    # the current section_grower terminates
                    self.growth_algo.terminate(section_grower)
                    self.active_sections.remove(section_grower)
