import numpy as np

from collections import deque
from morphio import SectionType


def sample(data, size=None):
    """Returns a value according to the input data"""
    return np.random.choice(data, size=size)


def fill_sec_diameters(neuron, section, taper, max_diam):
    """Fills in the diameters of a section
       with an increasing tapering according
       to the biological model (taper, max_diam).
    """
    segment_lenghts = np.linalg.norm(np.diff(section.points[::-1], axis=0), axis=1)
    cum_segment_lengths = np.cumsum(np.append([0], segment_lenghts))
    diameters = cum_segment_lengths * taper + section.diameters[-1]
    last_allowed_diameter = np.where(diameters < max_diam)[0][-1]
    diameters[last_allowed_diameter:] = diameters[last_allowed_diameter]


def fill_parent_diameters(neuron, chil, secID, model, status, connections):
    """Fills in the diameters of a section
       with an increasing tapering according
       to the biological model.
    """
    rall = sample(np.array(model['rall'])[np.array(model['rall']) > 0.0])
    trunk_diam = sample(model['trunk'])

    if np.alltrue(status[chil]):

        d1 = neuron.points[neuron.groups[chil[0]][0]][3]
        d2 = neuron.points[neuron.groups[chil[1]][0]][3]

        if rall is None:
            neuron.points[neuron.groups[secID + 1][0] - 1][3] = np.max([d1, d2])
        else:
            parent_d = np.power(np.power(d1, rall) + np.power(d2, rall), 1. / rall)

            if parent_d <= trunk_diam:
                neuron.points[neuron.groups[secID + 1][0] - 1][3] = parent_d
            else:
                # print secID, parent_d, d1, d2
                neuron.points[neuron.groups[secID + 1][0] - 1][3] = np.max([d1, d2])

        return True  # Action completed, to remove from active sections

    else:
        return False  # Action not completed, to keep in active sections


def correct_diameters(neuron, model):
    """Takes as input a neuron object,
       modifies the diameters and
       returns the new object
       Choose neurite type to diametrize
       Basals: 3
       Apicals: 4
       Axons: 2
    """

    term = [section_id for section_id in neuron.depth_begin()
            if not neuron.children(section_id)]

    # Set terminal diameters to term_diam
    for t in term:
        diameters = neuron.section(t).diameters
        diameters[-1] = model[2]['term'][-1]
        neuron.section(t).diameters = diameters

    active = deque(term)
    vistied = set()

    while active:
        section_id = active.pop()
        section = neuron.section(section_id)
        section.type = SectionType.basal_dendrite

        if neuron.children(section_id):
            # Assign a new diameter to the last point if section is not terminal
            state = fill_parent_diameters(
                neuron, chil, a, model[section.type], status, connections)
            maxD_param = 'trunk'
            taper_model_param = 'trunk_taper' if neuron.is_root(section_id) else 'taper'
        else:
            # Assign a new diameter to the last point if section is terminal
            state = True
            maxD_param = 'term_max_diam'
            taper_model_param = 'term_taper'

        # Fill in the section with new diameters, only when all children are processed.
        if state:
            # Taper within a section
            maxD = sample(model[section.type][maxD_param])
            taper_model = np.array(model[section.type][taper_model_param])
            tapering = sample(taper_model[taper_model > 0.0])

            fill_sec_diameters(neuron, section, tapering, maxD)
