import os
import tns
from tns import extract_input 
def run():
    # Extract distributions from cells in input directory
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(dir_path, '../test_data/bio/')
    distr = extract_input.distributions(filename, feature='path_distances')
    # Generate default parameters dictionary
    params = extract_input.parameters(neurite_types=['basal', 'apical'],
                                          feature='path_distances', method='tmd')

    # Initialize a neuron
    N = tns.NeuronGrower(input_distributions=distr,
                         input_parameters=params)

    # Grow your neuron
    neuron = N.grow()

    neuron.write('generated_cell.asc')
    neuron.write('generated_cell.swc')
    neuron.write('generated_cell.h5')


run()