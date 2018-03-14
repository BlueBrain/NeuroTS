import tns

# Cell to use as input for the diameter model
input_cell = './test_data/bio/C220197A-P2.h5'
# Cell be diametrized
synthesized_cell = './local/Neuron.h5'
# Outputcell to be saved
output_cell_name = './local/Neuron_diam'

# Generate model from input cell
model = tns.extract_input.diameter_distributions(input_cell)

# Create the object to modify the input cell to be diametrized
# Initialize tha cell with the output cell name
G = tns.Grower(input_parameters=None, input_distributions=model, name=output_cell_name)

# Load the neuron to be modified
G.neuron.load(synthesized_cell)

# Modify the diameters using the generated model
G.diametrize()
