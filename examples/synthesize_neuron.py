import tns


def run():
    # Extract distributions from cells in input directory
    filename = './../test_data/bio/'
    distr = tns.extract_input.distributions(filename, diameter_model=True)

    # Generate default parameters dictionary
    params = tns.extract_input.parameters(neurite_types=['basal', 'apical'])

    # Initialize a neuron
    grower = tns.NeuronGrower(input_distributions=distr, input_parameters=params)

    # Grow your neuron
    grower.grow()

    # Correct the diameters of your neuron
    grower.diametrize()

    grower.neuron.write_swc('synthesized_neuron.swc')


run()
