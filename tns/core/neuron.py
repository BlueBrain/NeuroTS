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
        """TNS Neuron Object where groups and points are stored

        Parameters:
            name: given name to be used in saving into a file.
            points: a 4-D structure of points (x, y, z, radius)
            groups: the structure of the tree in h5 format (SegmentID, Type, ParentID)
            sections: a set of section objects as an alternative representation of groups.
        """
        self.name = name
        self.points = []
        self.groups = [np.array([0, 1, -1])]
        # The following implements the correct connectivity of sections, while growing.
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


    def load(self, input_file):
        '''Loads a groups-points structure
           into the Neuron object.
        '''
        import h5py
        import os

        F = h5py.File(input_file)
        self.points = np.array(F['points'])
        self.groups = np.array(F['structure'])
        self.name = os.path.basename(input_file.replace('.h5',''))
