# A file to store basic functionality needed in different modules.
import numpy as np


neurite_types = {2:'axon',
                 3:'basal',
                 4:'apical'}


def round_num(num, decimal_places=4):
    """Rounds a number to the selected num of decimal places
    This allows consistency throughout the method and avoids
    numerical artifacts"""
    return np.round(num, decimal_places)


def create_section_from_data(parent, direction, start_point, stop, process=None):
    """Transforms the input data into information that pass in
    the generated section and returns the sectionGrower object.
    """
    from tns.core import section

    return section.SectionGrower(parent=parent,
                                 start_point=start_point,
                                 direction=direction,
                                 randomness=0.1,
                                 targeting=0.2,
                                 children=0,
                                 process=process,
                                 stop_criteria=copy.deepcopy(stop))
