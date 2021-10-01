import numpy as np
import copy
import neurots

def tmd_scale(barcode, thickness):
    # only the two first points of each bar are modified
    # because they correspond to spatial dimensions
    scaling_factor = np.ones(len(barcode[0]), dtype=np.float)
    scaling_factor[:2] = thickness
    return np.multiply(barcode, scaling_factor).tolist()


def modify_barcode(ph, thickness=1150.0, thickness_reference=1150.0):
    max_p = np.max(ph)
    scaling_reference = 1.0
    if 1 - max_p / thickness_reference < 0: #If cell is larger than the layers
        scaling_reference = thickness_reference / max_p
    return tmd_scale(ph, scaling_reference * thickness / thickness_reference)


def identity(ph):
    return ph

# Modify input parameters to scale barcode
params = neurots.extract_input.parameters(neurite_types=['apical', 'basal'], method='tmd')
distr = neurots.extract_input.distributions('./test_data/bio/', neurite_types=['apical', 'basal'])

# The basal dendrite will not be modified
params['basal'].update({'modify':{'funct':identity, 'kwargs': {}}})
# The apical dendrite will be scaled down to 0.10 % of its length
params['apical'].update({'modify':{'funct':modify_barcode, 'kwargs': {'thickness':100, 'thickness_reference':1000}}})

N = neurots.NeuronGrower(input_parameters=params, input_distributions=distr)
n = N.grow()
n.write('test_scaling.h5')
