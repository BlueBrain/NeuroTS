'''
TNS class : Grow a neuron
'''
import numpy as np
from tns.morphmath import sample
import math


methods = ['symmetric', 'bio_oriented', 'directional']


def angle3D(v1, v2):
    """Returns the angle between v1, v2"""
    def dotproduct(v1, v2):
        return sum((a*b) for a, b in zip(v1, v2))
    def length(v):
        return math.sqrt(dotproduct(v, v))
    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))


def grow_trunks(input_distributions, input_parameters):
    """Generates trunks on soma"""
    n_neurites = 0

    if input_parameters["basal"]:
        n_basals = sample.n_neurites(input_distributions['n_basals'])
        n_neurites = n_neurites + n_basals

    if input_parameters["apical"]:
        n_apicals = sample.n_neurites(input_distributions['n_apicals'])
        n_neurites = n_neurites + n_apicals

    if input_parameters["axon"]:
        n_axons = sample.n_neurites(input_distributions['n_axons'])
        n_neurites = n_neurites + n_axons

    trunk_angles = sample.trunk_angles(input_distributions, n_neurites)
    trunk_z = sample.azimuth_angles(input_distributions, n_neurites)

    return trunk_angles, trunk_z
