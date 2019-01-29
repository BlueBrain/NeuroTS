from tns.morphmath.sample import Distr

def test_Distr():
    params = {'soma': {'size': {'norm': {'mean': 9.024144162609812, 'std': 3.5462697985669935}}}}
    Distr(params)
