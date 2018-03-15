import tns
import tmd
import view

# Select output_path to save results
output_path = './Results/'
# Select a name for the synthesized neuron
output_name = 'TestNeuron'

# Extract distributions from cells in input directory
filename = './TNS/test_data/bio/'
distr = tns.extract_input.distributions(filename, diameter_model=True)

# Generate default parameters dictionary
params = tns.extract_input.parameters(neurite_types=['basal', 'apical'])

# Initialize a neuron
N = tns.Grower(input_distributions=distr, input_parameters=params, name=output_name)

# Grow your neuron
N.grow()

# Correct the diameters of your neuron
N.diametrize()

# Save your neuron to the selected output path
N.save(output_path=output_path)

# Load the generated neuron
n = tmd.io.load_neuron(output_path + output_name + '.h5')

# View your generated neuron
view.view.neuron(n)
