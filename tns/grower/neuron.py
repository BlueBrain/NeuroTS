'''
TNS class : Neuron object that contains the growers inside the class.
'''
import numpy as np
from tns.core import soma
from tns.core import tree
from tns.morphmath import sample
import math
import grow as gr


class Neuron(object):
    """
    A Neuron object is a container for Trees and a Soma.
    The groups and points encode the 3D structure of the Neuron.
    """

    def __init__(self, input_parameters, input_distributions, name='Neuron'):
        """TNS Neuron Object

        Parameters:
            neuron: Obj neuron where groups and points are stored
            points: a set of 4D points (x,y,z,radius)
            groups: the structure of the tree in h5 format (SegmentID, Type, ParentID)
            sections: keeps a record of section objects
            trunks: the sampled trunks of the tree
            input_parameters: the user-defined parameters
            input_distributions: distributions extracted from biological data
        """
        self.name = name

        self.points = []
        self.groups = [np.array([0, 1, -1])]
        self.sections = [[],]
        self.trunks = []
        self.input_parameters = input_parameters
        self.input_distributions = input_distributions


    def save(self, output_path='./'):
        '''
        Output the synthesized neuron in h5 file format;
        the points is a set of 4D points (x,y,z,radius),
        the groups is the structure of the tree (SegmentID, Type, ParentID)
        '''
        import h5py
        import os

        opath = os.path.join(output_path, str(self.name) + '.h5')

        Fdata = h5py.File(opath, 'w')

        Fdata.create_dataset(name="points", data=np.array(self.points))
        Fdata.create_dataset(name="structure", data=np.array(self.groups))

        Fdata.close()


    def grow_soma(self):
        """Generates a soma based on input_distributions.
        The initial neurites need to be generated
        in order to get the soma coordinates correct.
        """
        soma_radius = sample.soma_size(self.input_distributions)

        trunk_angles, trunk_z = gr.grow_trunks(self.input_distributions,
                                               self.input_parameters)

        s = soma.Soma(initial_point=self.input_parameters["origin"],
                      radius=soma_radius)

        self.trunks = s.generate(neuron=self,
                                 trunk_angles=trunk_angles,
                                 z_angles=trunk_z)


    def grow_neurite(self, tree_type, orientation=None):
        """Selects a trunk according to the selected orientation,
        grows the corresponding tree. If the orientation is None
        a trunk is randomly selected from the list.
        """
        if orientation is None:
            Aselect = np.random.choice(range(len(self.trunks)))
            trunk = self.trunks[Aselect]
            orientation = trunk/np.linalg.norm(trunk)
        else:
            Aselect = np.argsort([gr.angle3D(a / np.linalg.norm(a), orientation)
                                 for a in self.trunks])[0]
            trunk = self.soma.center + self.soma.radius * np.array(orientation)

        method = self.input_parameters[tree_type]["branching_method"]

        assert method in gr.methods, \
               'Method not recognized, please select one of: ' + ', '.join(gr.methods) + ' !'

        tr = tree.Tree(initial_direction=orientation,
                       initial_point=trunk,
                       parameters=self.input_parameters[tree_type])

        ph = sample.ph(self.input_distributions[tree_type]["ph"])

        #if tree_type != "apical":
        #    tr.generate_galton_watson(neuron=self, ph_angles=ph,
        #                              method=method)
        #else:
        #    tr.generate_galton_watson_apical(neuron=self, ph_angles=ph,
        #                                     method=method)

        if  tree_type != "apical":
            tr.generate_ph_angles(neuron=self, ph_angles=ph,
                                  method=method)
        else:
            tr.generate_ph_apical(neuron=self, ph_angles=ph,
                                  method=method)

        self.trunks = np.delete(self.trunks, Aselect, axis=0)


    def grow(self):
        """Generates a neuron according to the input_parameters
        and the input_distributions. The neuron consists of a soma 
        and a list of trees encoded in the h5 format as a set of points
        and groups.
        """
        self.grow_soma()

        if self.input_parameters["apical"]:
            self.grow_neurite(orientation=self.input_parameters["apical"]["orientation"],
                              tree_type="apical")

        if self.input_parameters["axon"]:
            self.grow_neurite(orientation=self.input_parameters["axon"]["orientation"],
                              tree_type="axon")

        if self.input_parameters["basal"]:
            while len(self.trunks) > 0:
               self.grow_neurite(orientation=None, tree_type="basal")
