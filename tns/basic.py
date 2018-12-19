# A file to store basic functionality needed in different modules.
import numpy as np


# Neurite type numbers are consistent with swc, h5py file formats
neurite_types = {2: 'axon',
                 3: 'basal',
                 4: 'apical'}


def round_num(num, decimal_places=4):
    """Rounds a number to the selected num of decimal places
    This allows consistency throughout the method and avoids
    numerical artifacts"""
    return np.round(num, decimal_places)
