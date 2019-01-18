''' Module to extract morphometrics about diameters of cells.'''

from itertools import chain

import numpy as np
from neurom import get, morphmath
from neurom.core import Tree, iter_neurites
from neurom.core.types import tree_type_checker as is_type
from neurom.morphmath import segment_length, segment_radius

default_model = {'Rall_ratio': 3. / 2.,
                 'siblings_ratio': [1. / 3.]}


def section_mean_taper(s):
    '''Computes the mean tapering of a section'''
    initial_diam = min(s.points[:, 3])

    di_li = sum([segment_radius([s.points[i], s.points[i + 1]]) * segment_length(
        [s.points[i], s.points[i + 1]]) for i in range(len(s.points) - 1)])

    i_li = sum([i * morphmath.segment_length([s.points[i], s.points[i + 1]])
                for i in range(len(s.points) - 1)])

    return (di_li - initial_diam * s.length) / i_li


def terminal_diam(tree):
    """Returns the model for the terminations"""
    term_diam = [2. * t.points[-1, 3] for t in Tree.ileaf(tree.iter_sections().next())]

    return term_diam


def section_taper(tree):
    """Returns the tapering of the *diameters* within
       the sections of a tree"""
    # Return non-leafs and exclude the trunk = first section
    tapers = [2 * section_mean_taper(s) if Tree.is_leaf(s)
              else None for s in tree.iter_sections()]
    return [taper for taper in tapers if taper][1:]


def model(neuron):
    """Measures the statistical properties of a neuron's
       diameters and outputs a diameter_model"""

    values = {}

    types_to_process = {tree.type.value: tree.type for tree in neuron.neurites}

    for typee in types_to_process:

        neurite_type = types_to_process[typee]
        taper = [section_taper(tree) for tree in iter_neurites(neuron, filt=is_type(neurite_type))]
        term_diam = [terminal_diam(tree)
                     for tree in iter_neurites(neuron, filt=is_type(neurite_type))]
        trunk_diam = [2. * np.max(get('segment_radii', tree))
                    for tree in iter_neurites(neuron, filt=is_type(neurite_type))]

        values[typee - 1] = {"taper": [c for c in chain(*taper)],
                             "term": [c for c in chain(*term_diam)],
                             "trunk": trunk_diam}

        values[typee - 1].update(default_model)

    return values


def get_taper(neurons, neurite_type):
    '''get taper'''
    return [section_taper(tree) for tree in iter_neurites(neurons, filt=is_type(neurite_type))]


def get_term_diam(neurons, neurite_type):
    '''get term'''
    return [terminal_diam(tree)
            for tree in iter_neurites(neurons, filt=is_type(neurite_type))]


def population_model(neurons):
    """Measures the statistical properties of a neuron's
       diameters and outputs a diameter_model"""

    values = {}

    types_to_process = {tree.type.value: tree.type for tree in neurons.neurites}

    for typee in types_to_process:

        neurite_type = types_to_process[typee]

        values[typee - 1] = {
            "taper": [c for c in chain(*get_taper(neurons, neurite_type))],
            "term": [c for c in chain(*get_term_diam(neurons, neurite_type))],
            "trunk": [
                2. * np.max(get('segment_radii', tree))
                for tree in iter_neurites(neurons, filt=is_type(neurite_type))
            ]
        }

        values[typee - 1].update(default_model)

    return values
