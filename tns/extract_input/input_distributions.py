"""Input distributions"""

import neurom as nm
import tmd
from tns.extract_input.from_TMD import persistent_homology_angles
from tns.extract_input.from_neurom import soma_data, trunk_neurite, number_neurites
from tns.extract_input import from_diameter


def default_keys():
    '''Returns the important keys for the distribution extraction'''
    return {'soma': {},
            'basal': {},
            'apical': {},
            'axon': {}}


def distributions(filepath, neurite_types=None, threshold_sec=2,
                  diameter_input_morph=False, feature='radial_distances'):
    '''Extracts the input distributions from an input population
    defined by a directory of swc or h5 files
    threshold_sec: defines the minimum accepted number of terminations
    diameter_input_morph: if provided it will be used for the generation
                          of diameter model
    feature: defines the TMD feature that will be used to extract the
             persistence barcode: radial_distances, path_distances
    '''
    # Assume all neurite_types will be extracted if neurite_types is None
    if neurite_types is None:
        neurite_types = ['basal', 'apical', 'axon']

    pop_tmd = tmd.io.load_population(filepath)
    pop_nm = nm.load_neurons(filepath)

    input_distributions = default_keys()
    input_distributions['soma'].update(soma_data(pop_nm))

    # Define the neurom neurite_types
    neurom_types = {'basal': nm.BASAL_DENDRITE,
                    'apical': nm.APICAL_DENDRITE,
                    'axon': nm.AXON}

    def fill_input_distributions(input_distr, neurite_type):
        '''Helping function to avoid code duplication'''
        nm_type = neurom_types[neurite_type]
        input_distr[neurite_type].update(trunk_neurite(pop_nm, nm_type))
        input_distr[neurite_type].update(number_neurites(pop_nm, nm_type))
        input_distr[neurite_type].update(
            persistent_homology_angles(pop_tmd,
                                       threshold=threshold_sec,
                                       neurite_type=neurite_type,
                                       feature=feature))

    for ntype in neurite_types:
        fill_input_distributions(input_distributions, ntype)

    # In order to create diameter model an exemplar morphology is required
    # This is provided by diameter_input_morph
    if diameter_input_morph:
        neu_exemplar = nm.load_neuron(diameter_input_morph)
        input_distributions["diameter"] = from_diameter.model(neu_exemplar)
        input_distributions["diameter"]["method"] = 'M5'  # By default, diametrize from_tips

    return input_distributions
