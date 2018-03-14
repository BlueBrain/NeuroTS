from tns.morphmath import sample
import numpy as np


bifurcation_methods = ['symmetric', 'bio_oriented', 'directional', 'bio_smoothed',]


def grow_trunks(input_distributions, input_parameters):
    """Generates trunks on soma"""
    n_neurites = 0

    if input_parameters["basal"]:
        n_basals = sample.n_neurites(input_distributions['basal']["num_trees"])
        n_neurites = n_neurites + n_basals

    if input_parameters["apical"]:
        n_apicals = sample.n_neurites(input_distributions['apical']["num_trees"])
        n_neurites = n_neurites + n_apicals

    if input_parameters["axon"]:
        n_axons = sample.n_neurites(input_distributions['axon']["num_trees"])
        n_neurites = n_neurites + n_axons

    trunk_angles = sample.trunk_angles(input_distributions, n_neurites)
    trunk_z = sample.azimuth_angles(input_distributions, n_neurites)

    return trunk_angles, trunk_z


def grow_soma(grower):
    """Generates a soma based on input_distributions.
    The initial neurites need to be generated
    in order to get the soma coordinates correct.
    """
    from tns.core.soma import SomaGrower

    soma_radius = sample.soma_size(grower.input_distributions)

    trunk_angles, trunk_z = grow_trunks(grower.input_distributions,
                                        grower.input_parameters)

    s = SomaGrower(initial_point=grower.input_parameters["origin"],
                   radius=soma_radius)

    grower.trunks = s.generate(neuron=grower.neuron,
                               trunk_angles=trunk_angles,
                               z_angles=trunk_z)


def grow_neurite(grower, tree_type):
    """Selects a trunk according to the selected orientation,
    grows the corresponding tree. If the orientation is None
    a trunk is randomly selected from the list.
    """
    from tns.core.tree import TreeGrower
    from tns.morphmath.rotation import angle3D

    parameters = grower.input_parameters[tree_type]
    distributions = grower.input_distributions[tree_type]

    orientation = parameters["orientation"]

    if orientation is None:
        Aselect = np.random.choice(range(len(grower.trunks)))
        trunk = grower.trunks[Aselect]
        orientation = trunk/np.linalg.norm(trunk)
    else:
        Aselect = np.argsort([angle3D(a / np.linalg.norm(a), orientation)
                              for a in grower.trunks])[0]
        trunk = grower.neuron.soma.center + grower.neuron.soma.radius * np.array(orientation)

    method = parameters["branching_method"]

    assert method in bifurcation_methods, \
        'Method not recognized, please select one of: ' + ', '.join(bifurcation_methods) + ' !'

    tr = TreeGrower(initial_direction=orientation,
                    initial_point=trunk,
                    parameters=parameters)

    ph = sample.ph(distributions["ph"])

    if  tree_type != "apical":
        tr.generate_ph_angles(neuron=grower.neuron, ph_angles=ph,
                              method=method)
    else:
        tr.generate_ph_apical(neuron=grower.neuron, ph_angles=ph,
                              method=method)

    grower.trunks = np.delete(grower.trunks, Aselect, axis=0)
