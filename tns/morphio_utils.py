''' Models to create diameters of synthesized cells '''
from morphio import SectionType

DICT_OF_TYPES = {SectionType.apical_dendrite: 4,
                 SectionType.basal_dendrite: 3,
                 SectionType.axon: 2}

STR_TO_TYPES = {'apical': SectionType.apical_dendrite,
                'basal': SectionType.basal_dendrite,
                'axon': SectionType.axon}


def section_filter(neuron, tree_type=None):
    '''Filters all sections according to type.'''
    if tree_type is None:
        return list(neuron.iter())
    return [i for i in neuron.iter() if i.type == tree_type]


def root_section_filter(neuron, tree_type=None):
    '''Filters root sections according to type.'''
    if tree_type is None:
        return list(neuron.root_sections)
    return [i for i in neuron.root_sections if i.type == tree_type]
