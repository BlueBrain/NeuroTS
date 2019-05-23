"""Input parameters functions"""


def parameters(origin=(0., 0., 0.), method='trunk', neurite_types=None):
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
    elif method == 'tmd' or method == 'tmd_path':
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
                                           "branching_method": "directional",
                                           "orientation": [(0., 1., 0.)], })
        if method == 'tmd':
            input_parameters["apical"]["growth_method"] = 'tmd_apical'
        if method == 'tmd_path':
            input_parameters["apical"]["growth_method"] = 'tmd_apical_path'

    if 'axon' in neurite_types:
        input_parameters["axon"].update(parameters_default)
        input_parameters["axon"].update({"tree_type": 2,
                                         "orientation": [(0., -1., 0.)], })

    input_parameters['grow_types'] = neurite_types

    return input_parameters
