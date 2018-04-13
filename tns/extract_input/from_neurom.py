import neurom as nm
from neurom import stats
import numpy as np


def transform_distr(opt_distr):
    if opt_distr.type == 'norm':
        return {"norm": {"mean": opt_distr.params[0],
                         "std": opt_distr.params[1]}}
    elif opt_distr.type == 'uniform':
        return {"uniform": {"min": opt_distr.params[0],
                            "max": opt_distr.params[1] + opt_distr.params[0]}}
    elif opt_distr.type == 'expon':
        return {"expon": {"loc": opt_distr.params[0],
                          "lambda": 1. / opt_distr.params[1]}}


def soma_data(pop):
    # Extract soma size as a normal distribution
    # Returns a dictionary with the soma information
    soma_size = nm.get('soma_radii', pop)
    ss = stats.fit(soma_size,  distribution='norm')

    return {"size": transform_distr(ss)}


def trunk_neurite(pop, neurite_type=nm.BASAL_DENDRITE):
    '''Extracts the trunk data for a specific tree type'''

    angles = [nm.get('trunk_angles', neuron, neurite_type=neurite_type) for neuron in pop]
    angles = [i for a in angles for i in a]
    heights, bins = np.histogram(angles, bins=30)

    # Extract trunk relative orientations to reshample

    return {"trunk": {"orientation_deviation": {"data":
                                                {"bins": (bins[1:] + bins[:-1]) / 2.,
                                                 "weights": heights}},
                      "azimuth": {"uniform": {"min": np.pi, "max": 0.0}}}}


def radial_density_neurite(pop, neurite_type=nm.BASAL_DENDRITE):
    # Extract the radial distribution of sections density.

    # Termination radial density of neurite type.
    term_radial_dist = nm.get('section_term_radial_distances', pop, neurite_type=neurite_type)

    # Bifurcation radial density of neurite type.
    bif_radial_dist = nm.get('section_bif_radial_distances', pop, neurite_type=neurite_type)

    return {"term_density": {"data": term_radial_dist},
            "bif_density": {"data": bif_radial_dist}}


def number_neurites(pop, neurite_type=nm.BASAL_DENDRITE):
    # Extract number of neurites as a precise distribution
    # The output is given in integer numbers which are
    # the permitted values for the number of trees.
    nneurites = nm.get('number_of_neurites', pop, neurite_type=neurite_type)
    heights, bins = np.histogram(nneurites, bins=np.arange(np.min(nneurites),
                                                           np.max(nneurites) + 2))

    return {"num_trees": {"data": {"bins": bins[:-1],
                                   "weights": heights}}}
