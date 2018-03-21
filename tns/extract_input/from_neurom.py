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
                          "lambda": 1./opt_distr.params[1]}}

def soma_data(pop, distr):
    # Extract soma size as a normal distr
    soma_size = nm.get('soma_radii', pop)
    ss = stats.fit(soma_size,  distribution='norm')

    distr.update({"soma":{}})

    distr["soma"]["size"] = transform_distr(ss)

def trunk_data(pop, distr):
    # Extract trunk relative orientations to reshample

    def get_trunk_neurite_type(pop, distr, tree_type='basal', nm_type=nm.BASAL_DENDRITE):
        '''Extracts the trunk data for a specific tree type'''

        angles = [nm.get('trunk_angles', n, neurite_type=nm_type) for n in pop]
        angles = [i for a in angles for i in a]
        heights, bins = np.histogram(angles, bins=30)

        if tree_type not in distr:
            distr[tree_type] = {}

        distr[tree_type].update({"trunk":{}})

        distr[tree_type]["trunk"]["orientation_deviation"] = {"data":
                                                {"bins": (bins[1:] + bins[:-1]) / 2.,
                                                 "weights": heights}}

        # Set trunk azimuth as a predefined uniform
        distr[tree_type]["trunk"]["azimuth"] = {"uniform": {"min":np.pi, "max":0.0}}

    get_trunk_neurite_type(pop, distr, tree_type='basal', nm_type=nm.BASAL_DENDRITE)
    get_trunk_neurite_type(pop, distr, tree_type='apical', nm_type=nm.APICAL_DENDRITE)
    get_trunk_neurite_type(pop, distr, tree_type='axon', nm_type=nm.AXON)


def radial_density(pop, distr):
    # Extract the radial distribution of sections density.

    # Radial density of basal dendrites.
    radial_dist = nm.get('section_term_radial_distances', pop, neurite_type=nm.BASAL_DENDRITE)
    # Normalize the density according to the number of neurons
    # This way the section density is equally distributed among neurons.
    distr["basal"] = {"term_density":{"data": radial_dist}}

    radial_dist = nm.get('section_bif_radial_distances', pop, neurite_type=nm.BASAL_DENDRITE)
    distr["basal"]["bif_density"] = {"data": radial_dist}

    # Radial density of apical dendrites.
    radial_dist = nm.get('section_term_radial_distances', pop, neurite_type=nm.APICAL_DENDRITE)
    distr["apical"] = {"term_density":{"data": radial_dist}}

    radial_dist = nm.get('section_bif_radial_distances', pop, neurite_type=nm.APICAL_DENDRITE)
    distr["apical"]["bif_density"] = {"data": radial_dist}

    # Radial density of axons.
    radial_dist = nm.get('section_term_radial_distances', pop, neurite_type=nm.AXON)
    distr["axon"] = {"term_density":{"data": radial_dist}}

    radial_dist = nm.get('section_bif_radial_distances', pop, neurite_type=nm.AXON)
    distr["axon"]["bif_density"] = {"data": radial_dist}


def number_neurites_data(pop, distr):
    # Extract number of neurites as a precise distribution
    # The output is given in integer numbers which are
    # the permitted values for the number of trees.
    def get_nneurite_type(pop, distr, tree_type='basal', nm_type=nm.BASAL_DENDRITE):
        '''Extracts the number of neurites for a specific tree type'''

        nneurites = nm.get('number_of_neurites', pop, neurite_type=nm_type)
        heights, bins = np.histogram(nneurites,
                                      bins=np.arange(np.min(nneurites), np.max(nneurites)+2))

        if tree_type not in distr:
            distr[tree_type] = {}

        distr[tree_type]["num_trees"] = {"data": 
                                                {"bins": bins[:-1],
                                                 "weights": heights}}

    get_nneurite_type(pop, distr, tree_type='basal', nm_type=nm.BASAL_DENDRITE)
    get_nneurite_type(pop, distr, tree_type='apical', nm_type=nm.APICAL_DENDRITE)
    get_nneurite_type(pop, distr, tree_type='axon', nm_type=nm.AXON)
