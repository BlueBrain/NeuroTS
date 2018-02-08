import neurom as nm
import numpy as np
from neurom.core import Tree
from neurom import morphmath

def section_mean_taper(s):
    initial_diam = min(s.points[:,3])

    di_li = sum([morphmath.segment_radius([s.points[i], s.points[i+1]]) *
                 morphmath.segment_length([s.points[i], s.points[i+1]])
                 for i in xrange(len(s.points)-1)])

    i_li = sum([i * morphmath.segment_length([s.points[i], s.points[i+1]])
                for i in xrange(len(s.points)-1)])

    return (di_li - initial_diam * s.length) / i_li


def section_mean_taper_old(s):
    """Returns the mean taper rate within a section"""
    return mean([(s.points[i][3] - s.points[i+1][3]) /
                 morphmath.segment_length([s.points[i], s.points[i+1]])
                 if morphmath.segment_length([s.points[i], s.points[i+1]]) > 0.001
                 else 0.0
                 for i in xrange(len(s.points)-1)])


def terminal_diam(tree):
    """Returns the model for the terminations"""
    term_diam = [2. * t.points[-1, 3] for t in Tree.ileaf(tree.iter_sections().next())]

    return term_diam


def terminal_rate(tree):
    """Returns the model for the terminations"""
    term_rate = [2. * section_mean_taper(t) for t in Tree.ileaf(tree.iter_sections().next())]

    return term_rate


def terminal_max_diam(tree):
    """Returns the model for the terminations"""
    term_max = [2. * max(t.points[:, 3]) for t in Tree.ileaf(tree.iter_sections().next())]

    return term_max


def trunk_taper(tree):
    """Returns the trunk tapering"""
    return 2. * section_mean_taper(tree.iter_sections().next())


def section_taper(tree):
    """Returns the tapering of the *diameters* within
       the sections of a tree"""
    # Return non-leafs and exclude the trunk = first section
    return filter(None, [2 * section_mean_taper(s) if Tree.is_leaf(s) else None for s in tree.iter_sections()])[1:]


def rall_ratio(tree):
    """Returns the rall ratio exponent of the diameters
       of the segments of a tree. At each bifurcation
       the e (p^e = d_1^e + d_2^e) is computed"""
    from neurom.core import Tree

    return [bif_ratio(bif_point) for bif_point in Tree.ibifurcation_point(tree.iter_sections().next())]


def bif_ratio(bif_point):
    """Returns the rall ration on a bifurcation point.
    """
    from scipy.optimize import curve_fit

    def funct(diameters, e):
        D, d1, d2 = diameters
        return np.power(d1/D, e) + np.power(d2/D, e)

    x = (bif_point.points[-1][3],
         bif_point.children[0].points[-1][3],
         bif_point.children[1].points[-1][3])

    y = 1.

    rall_ratio = curve_fit(funct, x, y, 3./2.)[0][0]

    if np.abs(1.0 - funct(x, rall_ratio)) < 0.01:
        return curve_fit(funct, x, y, 3./2.)[0][0]


def diameter_model(neuron):
    """Measures the statistical properties of a neuron's
       diameters and outputs a diameter_model"""
    from itertools import chain
    from neurom.core.types import tree_type_checker as is_type
    from neurom.core import Tree, iter_neurites

    values = {}

    types_to_process = {tree.type.value: tree.type for tree in neuron.neurites}

    for typee in types_to_process:

        neurite_type = types_to_process[typee]

        rall = [rall_ratio(tree) for tree in iter_neurites(neuron, filt=is_type(neurite_type))]

        taper = [section_taper(tree) for tree in iter_neurites(neuron, filt=is_type(neurite_type))]

        term_diam = [ terminal_diam(tree) for tree in iter_neurites(neuron, filt=is_type(neurite_type))]
        term_rate = [ terminal_rate(tree) for tree in iter_neurites(neuron, filt=is_type(neurite_type))]

        term_max_diam = [terminal_max_diam(tree) for tree in iter_neurites(neuron, filt=is_type(neurite_type))]

        max_diam = [2.*np.max(nm.get('segment_radii', tree)) for tree in iter_neurites(neuron, filt=is_type(neurite_type))]

        tr_taper = [trunk_taper(tree) for tree in iter_neurites(neuron, filt=is_type(neurite_type))]

        values[typee-1] =  {"taper": [c for c in chain(*taper)],
                            "rall": [c for c in chain(*rall)],
                            "term": [c for c in chain(*term_diam)],
                            "term_taper": [c for c in chain(*term_rate)],
                            "term_max_diam": [c for c in chain(*term_max_diam)],
                            "trunk": max_diam,
                            "trunk_taper": tr_taper}
    return values


def diameter_model_population(neurons):
    """Measures the statistical properties of a neuron's
       diameters and outputs a diameter_model"""
    from itertools import chain
    from neurom.core.types import tree_type_checker as is_type
    from neurom.core import Tree, iter_neurites

    values = {}

    types_to_process = {tree.type.value: tree.type for tree in neurons.neurites}

    for typee in types_to_process:

        neurite_type = types_to_process[typee]

        rall = [rall_ratio(tree) for tree in iter_neurites(neurons, filt=is_type(neurite_type))]

        taper = [section_taper(tree) for tree in iter_neurites(neurons, filt=is_type(neurite_type))]

        term_diam = [ terminal_diam(tree) for tree in iter_neurites(neurons, filt=is_type(neurite_type))]
        term_rate = [ terminal_rate(tree) for tree in iter_neurites(neurons, filt=is_type(neurite_type))]

        term_max_diam = [terminal_max_diam(tree) for tree in iter_neurites(neurons, filt=is_type(neurite_type))]

        max_diam = [2.*np.max(nm.get('segment_radii', tree)) for tree in iter_neurites(neurons, filt=is_type(neurite_type))]

        tr_taper = [trunk_taper(tree) for tree in iter_neurites(neurons, filt=is_type(neurite_type))]

        values[typee-1] =  {"taper": [c for c in chain(*taper)],
                            "rall": [c for c in chain(*rall)],
                            "term": [c for c in chain(*term_diam)],
                            "term_taper": [c for c in chain(*term_rate)],
                            "term_max_diam": [c for c in chain(*term_max_diam)],
                            "trunk": max_diam,
                            "trunk_taper": tr_taper}
    return values
