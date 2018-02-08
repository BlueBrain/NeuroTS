import tns

# Cell to use as input for the diameter model
input_cell = '../../bitbucket/MorphSynthesis/Input/L5SPC_Input/GoodRepaired/Fluo55_low.h5'
synthesized_cell = './local/Neuron.h5'
output_cell = './local/Neuron_diam'

tns.diametrize(input_file=input_cell,
               cell_name=synthesized_cell,
               new_name=output_cell)
