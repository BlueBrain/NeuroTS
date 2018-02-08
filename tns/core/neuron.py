'''
TNS class : Neuron
'''
import numpy as np


class Neuron(object):
    """
    A Neuron object is a container for Trees and a Soma.
    The groups and points encode the 3D structure of the Neuron.
    """

    def __init__(self, name='Neuron'):
        """TNS Neuron Object

        Parameters:
            neuron: Obj neuron where groups and points are stored
            initial_direction: 3D vector or random
            initial_point:  the root of the tree
            radius: assuming that the radius is constant for now.
            tree_type: an integer indicating the type of the tree (choose from 2, 3, 4, 5)
        """
        self.name = name

        self.points = []
        self.groups = [np.array([0, 1, -1])]
        self.sections = [[],]


    def save(self, output_path='./'):
        '''
        Output the synthesized neuron in h5 file format
        '''
        import h5py
        import os

        opath = os.path.join(output_path, str(self.name) + '.h5')

        Fdata = h5py.File(opath, 'w')

        Fdata.create_dataset(name="points", data=np.array(self.points))
        Fdata.create_dataset(name="structure", data=np.array(self.groups))

        Fdata.close()
