from tns.morphmath import sample
import numpy as np
from numpy.testing import assert_equal

def test_Distr():
    params = {'soma': {'size': {'norm': {'mean': 9.024144162609812, 'std': 3.5462697985669935}}}}
    np.random.seed(0)
    soma_d = sample.Distr(params['soma']['size'])
    val = soma_d.draw_positive()
    np.random.seed(0)
    val1 = sample.soma_size(params)
    assert_equal(val, val1)
