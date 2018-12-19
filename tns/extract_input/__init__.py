# Module to extract morphometrics and TMD-input from a set of tree-shaped cells.
import tmd
import neurom as nm
from tns.extract_input.from_TMD import persistent_homology_angles
from tns.extract_input.from_neurom import soma_data, trunk_neurite, number_neurites
from tns.extract_input.from_diameter import population_model, model


def default_keys():
    '''Returns the important keys for the distribution extraction'''
    return {'soma': {},
            'basal': {},
            'apical': {},
            'axon': {}}


def distributions(filepath, neurite_types=None, threshold_sec=2,
                  diameter_model=False, feature='radial_distances'):
    '''Extracts the input distributions from an input population
    defined by a directory of swc or h5 files
    threshold_sec: defines the minimum accepted number of terminations
    diameter_model: defines if the diameter model will be extracted
    '''
    # Assume all neurite_types will be extracted if neurite_types is None
    if neurite_types is None:
        neurite_types = ['basal', 'apical', 'axon']

    pop_tmd = tmd.io.load_population(filepath)
    pop_nm = nm.load_neurons(filepath)

    input_distributions = default_keys()
    input_distributions['soma'].update(from_neurom.soma_data(pop_nm))

    # Define the neurom neurite_types
    neurom_types = {'basal': nm.BASAL_DENDRITE,
                    'apical': nm.APICAL_DENDRITE,
                    'axon': nm.AXON}

    def fill_input_distributions(input_distr, neurite_type):
        '''Helping function to avoid code duplication'''
        nm_type = neurom_types[neurite_type]
        input_distr[neurite_type].update(from_neurom.trunk_neurite(pop_nm, nm_type))
        input_distr[neurite_type].update(from_neurom.number_neurites(pop_nm, nm_type))
        input_distr[neurite_type].update(
            persistent_homology_angles(pop_tmd,
                                       threshold=threshold_sec,
                                       neurite_type=neurite_type,
                                       feature=feature))

    for ntype in neurite_types:
        fill_input_distributions(input_distributions, ntype)

    if diameter_model:
        input_distributions["diameter_model"] = population_model(pop_nm)

    return input_distributions


def parameters(name="Test_neuron", origin=(0., 0., 0.),
               neurite_types=['basal', 'apical', 'axon'], method='trunk'):
    '''Returns a default set of input parameters
       to be used as input for synthesis.
    '''
    # Assume all neurite_types will be extracted if neurite_types is None
    if neurite_types is None:
        neurite_types = ['basal', 'apical', 'axon']

    # Set up required fields
    input_parameters = {'basal': {},
                        'apical': {},
                        'axon': {}}

    input_parameters["origin"] = origin

    if method == 'trunk':
        branching = 'random'
    elif method == 'tmd':
        branching = 'bio_oriented'

    parameters_default = {"randomness": 0.15,
                          "targeting": 0.12,
                          "radius": 0.3,
                          "orientation": None,
                          "growth_method": method,
                          "branching_method": branching,
                          "modify": None}

    if 'basal' in neurite_types:
        input_parameters["basal"].update(parameters_default)
        input_parameters["basal"].update({"tree_type": 3})

    if 'apical' in neurite_types:
        input_parameters["apical"].update(parameters_default)
        input_parameters["apical"].update({"apical_distance": 0.0,
                                           "tree_type": 4,
                                           "orientation": [(0., 1., 0.)], })
        if method == 'tmd':
            input_parameters["apical"]["growth_method"] = 'tmd_apical'
            input_parameters["apical"]["branching_method"] = 'directional'

    if 'axon' in neurite_types:
        input_parameters["axon"].update(parameters_default)
        input_parameters["axon"].update({"tree_type": 2,
                                         "orientation": [(0., -1., 0.)], })

    input_parameters['grow_types'] = neurite_types

    return input_parameters


def diameter_distributions(filepath):
    '''Extracts the input diameter distributions from an input population
       defined by a directory of swc or h5 files
    '''
    import os

    if os.path.isdir(filepath):
        pop_nm = nm.load_neurons(filepath)
        model = population_model(pop_nm)
    elif os.path.isfile(filepath):
        neu_nm = nm.load_neuron(filepath)
        model = model(neu_nm)
    else:
        raise IOError("No directory or file found that matches the selected filepath!")

    return {"diameter_model": model}
