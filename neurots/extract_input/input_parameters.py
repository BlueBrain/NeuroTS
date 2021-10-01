"""Input parameters functions"""

tmd_algos = ('tmd', 'tmd_gradient', 'tmd_apical')


def parameters(origin=(0., 0., 0.),
               method='tmd',
               neurite_types=('basal', 'apical', 'axon'),
               feature='path_distances',
               diameter_parameters=None):
    '''Returns a default set of input parameters
       to be used as input for synthesis.
    '''
    input_parameters = {
        'basal': {},
        'apical': {},
        'axon': {},
        'origin': origin,
        'grow_types': neurite_types,
    }

    def merged_params(data):
        """Use input method to set branching"""
        ret = dict()
        if method == 'trunk':
            branching = 'random'
        elif method in tmd_algos:
            branching = 'bio_oriented'
        else:
            raise KeyError('Method not recognized! Please select from: {}.'.format(tmd_algos))

        ret.update({"randomness": 0.15,
                    "targeting": 0.12,
                    "radius": 0.3,
                    "orientation": None,
                    "growth_method": method,
                    "branching_method": branching,
                    "modify": None,
                    "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                    "metric": feature})
        ret.update(data)
        return ret

    if 'axon' in neurite_types:
        input_parameters["axon"] = merged_params({"tree_type": 2, "orientation": [(0., -1., 0.)], })

    if 'basal' in neurite_types:
        input_parameters["basal"] = merged_params({"tree_type": 3})

    if 'apical' in neurite_types:
        input_parameters["apical"] = merged_params({"tree_type": 4,
                                                    "branching_method": "directional",
                                                    "orientation": [(0., 1., 0.)], })
        if method == 'tmd':
            input_parameters["apical"]["growth_method"] = 'tmd_apical'

    input_parameters["diameter_params"] = {}
    if diameter_parameters is None:
        input_parameters["diameter_params"]['method'] = 'default'
    elif isinstance(diameter_parameters, str):
        input_parameters["diameter_params"]['method'] = diameter_parameters
    elif isinstance(diameter_parameters, dict):
        input_parameters["diameter_params"] = diameter_parameters
        input_parameters["diameter_params"]['method'] = 'external'
    else:
        raise ValueError('Diameter params not understood, {}'.format(diameter_parameters))

    return input_parameters
