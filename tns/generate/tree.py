'''
TNS class : Tree
'''
import copy
import json
import logging
from collections import namedtuple

import numpy as np

from morphio import PointLevel, SectionType
from tns.utils import TNSError
from tns.generate.algorithms import basicgrower, tmdgrower
from tns.generate.section import (SectionGrower, SectionGrowerPath,
                                  SectionGrowerTMD)
from tns.morphmath import sample

L = logging.getLogger('tns')

# LAMBDA: parameter that defines the slope of exponential probability
LAMDA = 1.

growth_algorithms = {'tmd': tmdgrower.TMDAlgo,
                     'tmd_apical': tmdgrower.TMDApicalAlgo,
                     'tmd_gradient': tmdgrower.TMDGradientAlgo,
                     'axon_trunk': basicgrower.AxonAlgo,
                     'trunk': basicgrower.TrunkAlgo}

section_growers = {'radial_distances': SectionGrowerTMD,
                   'path_distances': SectionGrowerPath,
                   'trunk_length': SectionGrower}


# Section grower parameters
SectionParameters = namedtuple('SectionParameters',
                               ['randomness', 'targeting', 'scale_prob', 'history'])


def _create_section_parameters(input_dict):
    """ Create section parameters from input dictionary
    Args:
        input_dict: dict
            Input dictionary with 'randomness' and 'targeting' entries

    Returns:
        SectionParameters namedtuple
    """
    randomness = np.clip(input_dict['randomness'], 0.0, 1.0)
    targeting = np.clip(input_dict['targeting'], 0.0, 1.0)
    history = np.clip(1.0 - randomness - targeting, 0.0, 1.0)

    parameters = SectionParameters(
        randomness=randomness,
        targeting=targeting,
        scale_prob=LAMDA,
        history=history
    )

    try:
        assert np.isclose(randomness + targeting + history, 1.0)
        L.debug('Section Parameters: %s', parameters)
        return parameters

    except AssertionError:
        msg = 'Parameters randomness, targeting and history do not sum to 1:\n{}'.format(parameters)
        L.error(msg)
        raise TNSError(msg)


class TreeGrower:
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
            parameters including: tree_type, radius, randomness, targeting.
            tree_type: an integer indicating the type (choose from 2, 3, 4, 5)
            context: an object containing contextual information
        """
        self.neuron = neuron
        self.direction = initial_direction
        self.point = initial_point
        self.type = parameters["tree_type"]  # 2: axon, 3: basal, 4: apical, 5: other
        self.params = parameters
        self.distr = distributions
        self.active_sections = list()
        self.context = context

        # Creates the distribution from which the segment lengths
        # To sample a new seg_len call self.seg_len.draw()
        self.seg_length_distr = sample.Distr(self.params["step_size"])
        self._section_parameters = _create_section_parameters(parameters)
        self.growth_algo = self._initialize_algorithm()

    def _initialize_algorithm(self):
        """ Initialization steps for TreeGrower
        """
        grow_meth = growth_algorithms[self.params["growth_method"]]

        growth_algo = grow_meth(input_data=self.distr,
                                params=self.params,
                                start_point=self.point,
                                context=self.context)

        stop, num_sec = growth_algo.initialize()

        sec = self.add_section(parent=None,
                               direction=self.direction,
                               first_point=list(self.point),
                               stop=copy.deepcopy(stop),
                               process='major',
                               pathlength=0.,
                               children=2 if num_sec > 1 else 0)
        # First section of the tree has at least one point.
        sec.first_point()

        return growth_algo

    def add_section(self, parent, direction, first_point, stop, pathlength,
                    process=None, children=0):
        """Generates a section from the parent section "act"
        from all the required information. The section is
        added to the neuron.sections and activated.
        """
        SGrower = section_growers[self.params["metric"]]

        sec_grower = SGrower(parent=parent,
                             first_point=first_point,
                             direction=direction,
                             parameters=self._section_parameters,
                             children=children,
                             process=process,
                             stop_criteria=copy.deepcopy(stop),
                             step_size_distribution=self.seg_length_distr,
                             pathlength=pathlength,
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
        ordered_list = np.argsort([ss.stop_criteria["TMD"].bif for ss in secs])
        return np.copy(secs)[ordered_list]

    def append_section(self, section):
        '''Append section to the MorphIO neuron'''
        if section.parent:
            append_fun = section.parent.append_section
        else:
            append_fun = self.neuron.append_root_section

        if L.level == logging.DEBUG:  # pragma: no cover
            data = {"parent": section.parent.id if section.parent else None,
                    "coord": np.vstack(section.points).tolist(),
                    "radius": [self.params["radius"] * 2] * len(section.points),
                    "type": int(SectionType(self.params["tree_type"]))}
            L.debug("appended_data=%s", json.dumps(data))

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
                    latest = section_grower.latest_directions[-1]
                    section_grower.id = section.id
                    # the current section_grower bifurcates
                    # Returns two section_grower dictionaries: (S1, S2)
                    for child_section in self.growth_algo.bifurcate(section_grower):
                        child = self.add_section(parent=section,
                                                 pathlength=section_grower.pathlength,
                                                 **child_section)
                        # Copy the final normed direction of parent to all children
                        child.latest_directions.append(latest)
                        # Generate the first point of the section
                        child.first_point()
                    self.active_sections.remove(section_grower)

                elif state == 'terminate':
                    # the current section_grower terminates
                    self.growth_algo.terminate(section_grower)
                    self.active_sections.remove(section_grower)
