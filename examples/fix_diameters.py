import tns

# Cell to use as input for the diameter model
input_cell = './test_data/bio/C220197A-P2.h5'
synthesized_cell = './local/Neuron.h5'
output_cell = './local/Neuron_diam'

tns.diametrize(input_file=input_cell,
               cell_name=synthesized_cell,
               new_name=output_cell)
