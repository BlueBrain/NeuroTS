import numpy as np
import neurom
import os

from numpy.testing import assert_array_equal

import morphio
import tns.generate.soma as test_module
from tns import extract_input
_path = os.path.dirname(os.path.abspath(__file__))


def test_interpolate():
    assert_array_equal(test_module.SomaGrower.interpolate(np.array([1,2,3])),
                       [1, 2, 3, 1, 2, 3, 1, 2, 3])
