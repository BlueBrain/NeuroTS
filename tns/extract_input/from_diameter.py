''' Module to extract morphometrics about diameters of cells.'''

from itertools import chain

import numpy as np
from neurom import get
from neurom.core import Tree, iter_neurites
from neurom.core.types import tree_type_checker as is_type
from neurom.morphmath import segment_length, segment_radius

from tns.morphio_utils import NEUROM_TYPE_TO_STR
from tns.utils import _check

default_model = {'Rall_ratio': 3. / 2.,
                 'siblings_ratio': 1.}


def section_mean_taper(s):
    '''Computes the mean tapering of a section'''
    min_diam = min(s.points[:, 3])

    di_li = sum([segment_radius([s.points[i], s.points[i + 1]]) * segment_length(
        [s.points[i], s.points[i + 1]]) for i in range(len(s.points) - 1)])

    return (di_li - min_diam * s.length) / s.length


def terminal_diam(tree):
    """Returns the model for the terminations"""
    mean_diam = np.mean(tree.points[:, 3])
    term_diam = [2. * t.points[-1, 3] for t in Tree.ileaf(next(tree.iter_sections()))
                 if t.points[-1, 3] < 1.2 * mean_diam]

    return term_diam


def section_taper(tree):
    """Returns the tapering of the *diameters* within
       the sections of a tree"""
    # Exclude the trunk = first section, taper should not be x2 because it is relative
    tapers = [section_mean_taper(s) for s in tree.iter_sections()]
    return [taper for taper in tapers if taper][1:]


def section_trunk_taper(tree):
    """Returns the tapering of the *diameters* within
       the sections of a tree"""
    # Exclude the trunk = first section, taper should not be x2 because it is relative
    return section_mean_taper(next(tree.iter_sections()))


def model(input_object):
    """Measures the statistical properties of an input_object's
       diameters and outputs a diameter_model
       Input can be a population of neurons, or a single neuron.
    """
    values = {}

    for neurite_type in set(tree.type for tree in input_object.neurites):

        neurites = list(iter_neurites(input_object, filt=is_type(neurite_type)))

        taper = [section_taper(tree) for tree in neurites]
        trunk_taper = np.array([section_trunk_taper(tree) for tree in neurites])
        taper_c = np.array(list(chain(*taper)))
        # Keep only positive, non-zero taper rates
        taper_c = taper_c[np.where(taper_c > 0.00001)[0]]
        trunk_taper = trunk_taper[np.where(trunk_taper >= 0.0)[0]]
        term_diam = [terminal_diam(tree) for tree in neurites]
        trunk_diam = [2. * np.max(get('segment_radii', tree)) for tree in neurites]

        key = NEUROM_TYPE_TO_STR[neurite_type]

        values[key] = {"taper": taper_c,
                       "term": [c for c in chain(*term_diam)],
                       "trunk": trunk_diam,
                       "trunk_taper": trunk_taper}

        _check(values[key])
        values[key].update(default_model)

    return values
