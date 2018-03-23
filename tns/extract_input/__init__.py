# Module to extract morphometrics and TMD from a set of tree-shaped cells.
def default_keys():
    '''Returns the important keys for the distribution extraction'''
    return {'basal':{},
            'apical':{},
            'axon':{}}


def distributions(filepath, neurite_types=['basal', 'apical', 'axon'], threshold_sections=2, diameter_model=False):
    '''Extracts the input distributions from an input population
       defined by a directory of swc or h5 files
    '''
    import from_TMD
    import from_neurom
    import tmd
    import neurom as nm

    pop_ntn = tmd.io.load_population(filepath)
    pop_nm = nm.load_neurons(filepath)

    input_distributions = default_keys()

    from_neurom.soma_data(pop_nm, input_distributions)
    from_neurom.number_neurites_data(pop_nm, input_distributions)
    from_neurom.trunk_data(pop_nm, input_distributions)
    if 'basal' in neurite_types:
        from_TMD.ph_basal(pop_ntn, input_distributions, threshold=threshold_sections)
    if 'apical' in neurite_types:
        from_TMD.ph_apical(pop_ntn, input_distributions, threshold=threshold_sections)
    if 'axon' in neurite_types:
        from_TMD.ph_axon(pop_ntn, input_distributions, threshold=threshold_sections)

    if diameter_model:
        import from_diameter
        input_distributions["diameter_model"] = from_diameter.population_model(pop_nm)

    return input_distributions


def parameters(name="Test_neuron", origin=(0.,0.,0.), neurite_types=['basal', 'apical', 'axon'], method='basic'):
    '''Returns a default set of input parameters
       to be used as input for synthesis.
    '''
    # Set up required fields

    input_parameters = default_keys()
    input_parameters["origin"] = origin

    if method=='basic':
        gmethod = 'trunk'
        branching = 'random'
    else:
        gmethod = 'ph_angles'
        branching = 'bio_oriented'

    parameters_default = {"apical_distance": None,
                          "randomness":0.15,
                          "targeting":0.12,
                          "radius":0.3,
                          "orientation":None,
                          "growth_method": gmethod,
                          "method": method,}

    if 'basal' in neurite_types:
        input_parameters["basal"].update(parameters_default)
        input_parameters["basal"].update({"tree_type":3,
                                          "branching_method": branching,})

    if 'apical' in neurite_types:
        input_parameters["apical"].update(parameters_default)
        input_parameters["apical"].update({"apical_distance": 0.0,
                                           "tree_type":4,
                                           "orientation":[(0.,1.,0.)],
                                           "branching_method": branching,})

    if 'axon' in neurite_types:
        input_parameters["axon"].update(parameters_default)
        input_parameters["axon"].update({"tree_type":2,
                                          "orientation":[(0.,-1.,0.)],
                                          "branching_method": branching,})

    input_parameters['grow_types'] = neurite_types

    return input_parameters


def diameter_distributions(filepath, distributions=None):
    '''Extracts the input distributions from an input population
       defined by a directory of swc or h5 files
    '''
    import os
    import from_diameter
    import neurom as nm

    if os.path.isdir(filepath):
        pop_nm = nm.load_neurons(filepath)
        model = from_diameter.population_model(pop_nm)
    elif os.path.isfile(filepath):
        neu_nm = nm.load_neuron(filepath)
        model = from_diameter.model(neu_nm)
    else:
        return "No directory or file found that matches the selected filepath!"

    if distributions is None:
        distributions = {}

    distributions["diameter_model"] = model

    return distributions
