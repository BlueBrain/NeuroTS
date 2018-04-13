'''
TNS class : Tree
'''
import numpy as np
import copy
from tns.morphmath import random_tree as rd
from tns.morphmath import rotation
import section
from algorithms import basicgrower, tmdgrower


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
        self.type = parameters["tree_type"] # 2: axon, 3: basal, 4: apical, 5: other
        self.params = parameters
        self.distr = distributions


    def add_first_section(self, num_sec, stop, process='major'):
        """Creates the first section of the tree in the neuron
        extracting all the required information.
        num_sec: the expected number of sections to be grown
        stop: defines the stop criterion
        process: assumed to be major since it starts from soma
        """
        # The first point of the tree is always connected to the soma, so parent=0
        # children is 2 if expected number of sections is more than 1.

        self.add_section(parent=0, direction=self.direction,
                         start_point=np.array(self.point),
                         stop=stop, process=process,
                         children=2 if num_sec > 1 else 0)


    def add_section(self, parent, direction, start_point, stop, process=None, children=0):
        """Generates a section from the parent section "act"
        from all the required information. The section is
        added to the neuron.sections and activated.
        """
        self.neuron.sections.append(section.SectionGrower(parent=parent,
                                                          start_point=start_point,
                                                          direction=direction,
                                                          randomness=self.params["randomness"],
                                                          targeting=self.params["targeting"],
                                                          children=children,
                                                          process=process,
                                                          stop_criteria=copy.deepcopy(stop)))


    def run(self):
        '''Operates the tree growth according to the selected algorithm.
        '''
        grow_meth = growth_algorithms[self.params["growth_method"]]

        growth_algo = grow_meth(input_data=self.distr,
                                parameters=self.params,
                                start_point=self.point)

        stop, num_sec = growth_algo.first_section()
        self.add_first_section(num_sec=num_sec, stop=stop)
        active_sections = [len(self.neuron.sections) - 1] # The last available section in the neuron

        while active_sections:

            active_sections.sort(reverse=True)
            currentID = active_sections.pop()
            currentSec = self.neuron.sections[currentID]
            self.neuron.add_group([len(self.neuron.points), self.type, currentSec.parent])

            # the current section is generated
            state = growth_algo.extend(currentSec) # In here the stop criterion can be modified accordingly
            #print state, len(active_sections)

            self.neuron.add_points_without_radius(currentSec.points3D, self.params['radius'])

            if state=='bifurcate':
            # the current section bifurcates
            # Returns two section dictionaries: (S1, S2)
                s1, s2 = growth_algo.bifurcate(currentSec)

                self.add_section(parent=currentID, **s1)
                active_sections.append(len(self.neuron.sections) - 1)

                self.add_section(parent=currentID, **s2)
                active_sections.append(len(self.neuron.sections) - 1)

            elif state=='terminate':
            # the current section terminates
                growth_algo.terminate(currentSec)
