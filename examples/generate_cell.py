import tns

# Extract distributions from cells in input directory
filename = './test_data/bio/'
distr = tns.extract_input.distributions(filename)

# Generate default parameters dictionary
params = tns.extract_input.parameters(neurite_types=['basal'])

# Initialize a neuron
N = tns.Grower(input_distributions=distr, input_parameters=params, name='Neuron')

# Grow your neuron
N.grow()
# Save your neuron
N.save(output_path='./local/')
