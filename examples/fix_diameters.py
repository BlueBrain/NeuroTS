import os
import tns


def run():
    # Cell to use as input for the diameter model
    dir_path = os.path.dirname(os.path.realpath(__file__))
    input_cell = os.path.join(dir_path, '../test_data/bio/C220197A-P2.h5')

    # Outputcell to be saved
    output_cell_name = os.path.join(dir_path, './local/Neuron_diam')

    # Generate model from input cell

    model = tns.extract_input.diameter_distributions(input_cell)

    # Create the object to modify the input cell to be diametrized
    # Initialize tha cell with the output cell name
    G = tns.NeuronGrower(input_parameters=None, input_distributions=model, name=output_cell_name)

    # Modify the diameters using the generated model
    G.diametrize()

    G.neuron.write_asc('fixed_diameters.asc')


run()
