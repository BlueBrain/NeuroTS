"""Models to create diameters of synthesized cells."""
from morphio import SectionType
from neurom import NeuriteType

STR_TO_TYPES = {
    "apical": SectionType.apical_dendrite,
    "basal": SectionType.basal_dendrite,
    "axon": SectionType.axon,
}

TYPE_TO_STR = {
    SectionType.apical_dendrite: "apical",
    SectionType.basal_dendrite: "basal",
    SectionType.axon: "axon",
    SectionType.soma: "soma",
}


NEUROM_TYPE_TO_STR = {
    NeuriteType.apical_dendrite: "apical",
    NeuriteType.basal_dendrite: "basal",
    NeuriteType.soma: "soma",
    NeuriteType.axon: "axon",
}

STR_TO_NEUROM_TYPES = {
    "apical": NeuriteType.apical_dendrite,
    "basal": NeuriteType.basal_dendrite,
    "soma": NeuriteType.soma,
    "axon": NeuriteType.axon,
}


def section_filter(neuron, tree_type=None):
    """Filters all sections according to type."""
    if tree_type is None:
        return list(neuron.iter())
    return [i for i in neuron.iter() if i.type == tree_type]


def root_section_filter(neuron, tree_type=None):
    """Filters root sections according to type."""
    if tree_type is None:
        return list(neuron.root_sections)
    return [i for i in neuron.root_sections if i.type == tree_type]
