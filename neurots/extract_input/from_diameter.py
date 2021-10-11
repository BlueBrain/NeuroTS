"""Module to extract morphometrics about diameters of cells."""
from collections import defaultdict
from itertools import chain

import numpy as np
from neurom import get
from neurom.core.morphology import Section
from neurom.core.morphology import iter_neurites
from neurom.morphmath import segment_length
from neurom.morphmath import segment_radius

from neurots.morphio_utils import NEUROM_TYPE_TO_STR
from neurots.utils import _check

default_model = {"Rall_ratio": 3.0 / 2.0, "siblings_ratio": 1.0}


def section_mean_taper(s):
    """Computes the mean tapering of a section."""
    min_diam = min(s.points[:, 3])

    di_li = sum(
        [
            segment_radius([s.points[i], s.points[i + 1]])
            * segment_length([s.points[i], s.points[i + 1]])
            for i in range(len(s.points) - 1)
        ]
    )

    return (di_li - min_diam * s.length) / s.length


def terminal_diam(tree):
    """Returns the model for the terminations."""
    mean_diam = np.mean(tree.points[:, 3])
    term_diam = [
        2.0 * t.points[-1, 3]
        for t in Section.ileaf(next(tree.iter_sections()))
        if t.points[-1, 3] < 1.2 * mean_diam
    ]

    return term_diam


def section_taper(tree):
    """Returns the tapering of the *diameters* within the sections of a tree."""
    # Exclude the trunk = first section, taper should not be x2 because it is relative
    tapers = [section_mean_taper(s) for s in tree.iter_sections()]
    return [taper for taper in tapers if taper][1:]


def section_trunk_taper(tree):
    """Returns the tapering of the *diameters* within the sections of a tree."""
    # Exclude the trunk = first section, taper should not be x2 because it is relative
    return section_mean_taper(next(tree.iter_sections()))


def model(input_object):
    """Measure the statistical properties of input_object's diameters and outputs a diameter_model.

    Input can be a population of neurons, or a single neuron.
    """
    values = {}

    tapers = defaultdict(list)
    trunk_tapers = defaultdict(list)
    term_diams = defaultdict(list)
    trunk_diams = defaultdict(list)

    for neurite in iter_neurites(input_object):
        tapers[neurite.type].append(section_taper(neurite))
        trunk_tapers[neurite.type].append(section_trunk_taper(neurite))
        term_diams[neurite.type].append(terminal_diam(neurite))
        trunk_diams[neurite.type].append(2.0 * np.max(get("segment_radii", neurite)))

    for neurite_type in tapers:
        key = NEUROM_TYPE_TO_STR[neurite_type]

        taper_c = np.array(list(chain(*tapers[neurite_type])))
        trunk_taper = np.array(trunk_tapers[neurite_type])

        # Keep only positive, non-zero taper rates
        taper_c = taper_c[np.where(taper_c > 0.00001)[0]]
        trunk_taper = trunk_taper[np.where(trunk_taper >= 0.0)[0]]

        values[key] = {
            "taper": taper_c,
            "term": list(chain(*term_diams[neurite_type])),
            "trunk": trunk_diams[neurite_type],
            "trunk_taper": trunk_taper,
        }

        _check(values[key])
        values[key].update(default_model)

    return values
