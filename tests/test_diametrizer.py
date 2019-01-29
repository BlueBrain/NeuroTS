import neurom
import os

from numpy.testing import assert_array_equal

import morphio
import tns.generate.diametrizer as test_module
from tns import extract_input
_path = os.path.dirname(os.path.abspath(__file__))

def test_diametrize_constant_all():
    neuron = morphio.mut.Morphology(os.path.join(_path, '..', 'test_data', 'simple.swc'))
    test_module.diametrize_constant_all(neuron)

    # assert_array_equal(morphio.Morphology(neuron).diameters,
    #                    [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5])

def test_diametrize_constant():
    neuron = morphio.mut.Morphology(os.path.join(_path, '..', 'test_data', 'simple.swc'))
    test_module.diametrize_constant(neuron)

    assert_array_equal(morphio.Morphology(neuron).diameters,
                       [2., 2., 2.5, 2.5, 2.5, 2.5, 2., 2., 3., 3., 3., 3.])
