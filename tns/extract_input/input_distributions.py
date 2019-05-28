"""Input distributions"""

import neurom as nm
from neurom import load_neurons
import tmd
from tns.extract_input.from_TMD import persistent_homology_angles
from tns.extract_input.from_neurom import soma_data, trunk_neurite, number_neurites
from tns.extract_input import from_diameter
from tns.morphio_utils import STR_TO_NEUROM_TYPES


def _append_dicts(*args):
    '''Merge all dicts into the first one'''
    ret = args[0]
    for other_dict in args[1:]:
        ret.update(other_dict)
    return ret


def distributions(filepath, neurite_types=('basal', 'apical', 'axon'), threshold_sec=2,
                  diameter_input_morph=None, feature='radial_distances', diameter_model='M5'):
    '''Extracts the input distributions from an input population
    defined by a directory of swc or h5 files
    threshold_sec: defines the minimum accepted number of terminations
    diameter_input_morph: if input set of morphologies is provided
                          it will be used for the generation of diameter model
                          if no input is provided no diameter model will be generated
    feature: defines the TMD feature that will be used to extract the
             persistence barcode: radial_distances, path_distances
    '''
    pop_tmd = tmd.io.load_population(filepath)
    pop_nm = nm.load_neurons(filepath)

    input_distributions = {'soma': {}, 'basal': {}, 'apical': {}, 'axon': {}}
    input_distributions['soma'] = soma_data(pop_nm)

    if diameter_input_morph is not None:
        input_distributions["diameter"] = from_diameter.model(load_neurons(diameter_input_morph))
        input_distributions['diameter']['method'] = diameter_model

    for neurite_type in neurite_types:
        nm_type = STR_TO_NEUROM_TYPES[neurite_type]
        input_distributions[neurite_type] = _append_dicts(
            trunk_neurite(pop_nm, nm_type),
            number_neurites(pop_nm, nm_type),
            persistent_homology_angles(pop_tmd,
                                       threshold=threshold_sec,
                                       neurite_type=neurite_type,
                                       feature=feature),
            {'filtration_metric': feature})
    return input_distributions