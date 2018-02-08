from tns import extract_input

# Extract distributions from cells in input directory
filename = '../Input/L5SPC_Input/GoodRepaired/'
distr = extract_input.distributions(filename)

# Generate default parameters dictionary
params = extract_input.parameters(neurite_types=['basal'])

# Initialize a neuron
from tns.grower import neuron
N = neuron.Neuron(input_distributions=distr, input_parameters=params)
N.name = 'You_fave_name'

# Grow your neuron
N.grow()
# Save your neuron
N.save(output_path='./Your_fave_directory/')
