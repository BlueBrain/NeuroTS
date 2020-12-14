from tns.morphmath import sample
import numpy as np
from numpy.testing import assert_equal

def test_Distr():
    params = {'soma': {'size': {'norm': {'mean': 9.024144162609812, 'std': 3.5462697985669935}}}}
    np.random.seed(0)
    soma_d = sample.Distr(params['soma']['size'])
    val = soma_d.draw_positive()

    np.random.seed(79)
    val_neg = soma_d.draw_positive()

    np.random.seed(0)
    val1 = sample.soma_size(params)
    assert_equal(val, val1)
    assert_equal(val, 15.279949720206192)
    assert_equal(val_neg, 9.270213756873975)

    params = {'data': {'weights': [0.1, 0.9], 'bins': [1, 2]}}
    soma_d = sample.Distr(params)
    assert_equal(soma_d.draw_positive(), 2)

    assert_equal(sample.Distr.norm({"mean": 1, "std": 0.5}), {"loc": 1, "scale": 0.5})
    assert_equal(sample.Distr.uniform({"min": 1, "max": 1.25}), {"loc": 1, "scale": 0.25})
    assert_equal(sample.Distr.expon({"loc": 1, "lambda": 2}), {"loc": 1, "scale": 0.5})
