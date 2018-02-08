# Module to extract morphometrics and TMD from a set of tree-shaped cells.

def distributions(filepath, neurite_types=['basal', 'apical', 'axon']):
    '''Extracts the input distributions from an input population
       defined by a directory of swc or h5 files
    '''
    import from_TMD
    import from_neurom
    import neurontopology as ntn
    import neurom as nm

    pop_ntn = ntn.io.load_population(filepath)
    pop_nm = nm.load_neurons(filepath)

    input_distributions = {}

    from_neurom.soma_data(pop_nm, input_distributions)
    from_neurom.number_neurites_data(pop_nm, input_distributions)
    from_neurom.trunk_data(pop_nm, input_distributions)
    if 'basal' in neurite_types:
        from_TMD.ph_basal(pop_ntn, input_distributions)
    if 'apical' in neurite_types:
        from_TMD.ph_apical(pop_ntn, input_distributions)
    if 'axon' in neurite_types:
        from_TMD.ph_axon(pop_ntn, input_distributions)

    return input_distributions


def parameters(name="Test_neuron", origin=(0.,0.,0.), neurite_types=['basal', 'apical', 'axon']):
    '''Returns a default set of input parameters
       to be used as input for synthesis.
    '''
    # Set up required fields

    input_parameters = {"origin":origin,
                        "name":name,
                        "apical":{},
                        "basal":{},
                        "axon":{},}

    parameters_default = {"apical_distance": 0.0,
                          "randomness":0.15,
                          "targeting":0.12,
                          "radius":0.3}

    if 'basal' in neurite_types:
        input_parameters["basal"].update({"tree_type":3,
                                          "branching_method": "bio_oriented",})
        input_parameters["basal"].update(parameters_default)

    if 'apical' in neurite_types:
        input_parameters["apical"].update({"tree_type":4,
                                          "branching_method": "directional",})
        input_parameters["apical"].update(parameters_default)

    if 'axon' in neurite_types:
        input_parameters["axon"].update({"tree_type":2,
                                          "branching_method": "bio_oriented",})
        input_parameters["axon"].update(parameters_default)

    return input_parameters
