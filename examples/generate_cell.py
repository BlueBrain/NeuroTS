import tns
from tns import extract_input
from tns.grower import neuron

# Extract distributions from cells in input directory
filename = './test_data/bio/'
distr = extract_input.distributions(filename)

# Generate default parameters dictionary
params = extract_input.parameters(neurite_types=['basal'])

# Initialize a neuron
from tns.grower import neuron
N = neuron.Neuron(input_distributions=distr, input_parameters=params)
N.name = 'Neuron'

# Grow your neuron
N.grow()
# Save your neuron
N.save(output_path='./local/')
