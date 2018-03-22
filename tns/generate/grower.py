'''
TNS class : Grower object that contains the grower functionality.
'''
import numpy as np
from tns.core import neuron
import algorithms


class Grower(object):
    """
    A Grower object is a container for a Neuron, encoded in the
    structure of groups and points,
    a set of input distributions which store the data consumed by the algorithms
    and the parameters which define the algorithms and the user-selected parameters.    
    """
    def __init__(self, input_parameters, input_distributions, name='Neuron'):
        """TNS Grower Object

        Parameters:
            neuron: Obj neuron where groups and points are stored
            trunks: the sampled trunks of the tree
            input_parameters: the user-defined parameters
            input_distributions: distributions extracted from biological data
        """
        self.neuron = neuron.Neuron(name=name)
        self.trunks = []
        self.input_parameters = input_parameters
        self.input_distributions = input_distributions


    def save(self, output_path='./'):
        '''
        Output the synthesized neuron in h5 file format;
        the points is a set of 4D points (x,y,z,radius),
        the groups is the structure of the tree (SegmentID, Type, ParentID)
        '''
        self.neuron.save(output_path=output_path)


    def grow(self):
        """Generates a neuron according to the input_parameters
        and the input_distributions. The neuron consists of a soma 
        and a list of trees encoded in the h5 format as a set of points
        and groups.
        """
        algorithms.grow_soma(self, interpolation=None)

        for tree in self.trunks:
            algorithms.grow_neurite(self, tree)


    def diametrize(self):
        """Corrects the diameters of the neuron saved in the Grower.
        The neuron can either be loaded from a file by calling G.neuron.load(filename)
        or it can be generate by calling the G.grow() method.
        The Grower should be initialized with a distribution
        that includes a diameter_model.
        To extract a diameter model from a file, call extract_input.diameter_distributions(file)
        """
        import diametrizer

        model = self.input_distributions['diameter_model']
        diametrizer.correct_diameters(self.neuron, model=model)
