"""example of how to synthetise cell with external diametrizer"""
import os
from functools import partial
import tns
from tns import extract_input
from diameter_synthesis import build_models, build_diameters

def run():
    """Extract distributions from cells in input directory"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(dir_path, '../test_data/bio/')

    neurite_types = ['basal']

    config = {}
    config['neurite_types'] = neurite_types
    config['models'] = ['generic', ]
    config['n_samples'] = 1
    config['extra_params'] = {}
    config['extra_params']['generic'] = {
                'terminal_threshold': 1.,
                'taper': {'max_residual': 10, 'zeros':1e-8, 'max': 0.002, 'min': -0.005},
                'threshold': {'apical': 0.2, 'basal': 1.},
                'trunk_max_tries': 10
                }

    diameter_model_function = partial(build_models.build, config=config)
    distr = extract_input.distributions(filename, feature='path_distances',
                                        diameter_input_morph=filename,
                                        diameter_model=diameter_model_function)

    # Generate default parameters dictionary
    params = extract_input.parameters(neurite_types=neurite_types,
                                      feature='path_distances',
                                      method='tmd',
                                      diameter_parameters=config)

    # converts a morphio to neuromV2 neuron
    def external_diametrizer(neuron, model, neurite_type):
        return build_diameters.build(neuron, model, neurite_types, config)

    # Initialize a neuron
    grower = tns.NeuronGrower(input_distributions=distr,
                              input_parameters=params,
                              external_diametrizer=external_diametrizer)

    # Grow your neuron
    grower.grow()

    grower.neuron.write('generated_cell.asc')
    grower.neuron.write('generated_cell.swc')
    grower.neuron.write('generated_cell.h5')


run()
