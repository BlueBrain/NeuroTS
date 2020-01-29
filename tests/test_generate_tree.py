from nose import tools as nt
from tns.utils import TNSError
from tns.generate.tree import _create_section_parameters
from numpy import testing as npt


def test_create_section_parameters__normal_input():

    input_dict = {'randomness': 0.3, 'targeting': 0.6}

    parameters = _create_section_parameters(input_dict)

    npt.assert_almost_equal(parameters.randomness, 0.3)
    npt.assert_almost_equal(parameters.targeting, 0.6)
    npt.assert_almost_equal(parameters.history, 1.0 - 0.6 - 0.3)


def test_create_section_parameters__exceed_bounds():

    input_dict = {'randomness': 1.1, 'targeting': -0.1}
    parameters = _create_section_parameters(input_dict)

    npt.assert_almost_equal(parameters.randomness, 1.0)
    npt.assert_almost_equal(parameters.targeting, 0.0)
    npt.assert_almost_equal(parameters.history, 0.0)

    input_dict = {'randomness': -0.1, 'targeting': 1.0}
    parameters = _create_section_parameters(input_dict)

    npt.assert_almost_equal(parameters.randomness, 0.0)
    npt.assert_almost_equal(parameters.targeting, 1.0)
    npt.assert_almost_equal(parameters.history, 0.0)


@nt.raises(TNSError)
def test_create_section_parameters__sum_to_one_error():

    input_dict = {'randomness': 2.0, 'targeting': 2.0}

    parameters = _create_section_parameters(input_dict)


