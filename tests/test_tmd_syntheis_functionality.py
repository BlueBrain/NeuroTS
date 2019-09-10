'''Test tns.generate.section code'''

import json
import os
import numpy as np
from nose.tools import assert_dict_equal
from numpy.testing import assert_array_almost_equal, assert_equal
from tns.generate.algorithms.common import TMDStop
from tns.generate.algorithms.barcode import Barcode

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def test_barcode():
    '''Tests the barcode functionality'''

    with open(os.path.join(_PATH, 'dummy_distribution.json')) as f:
        ph_angles = json.load(f)['apical']['persistence_diagram'][0]

    barcode_test = Barcode(ph_angles)
    assert_equal(len(barcode_test.bifs), 7)
    assert_equal(len(barcode_test.terms), 8)
    assert_equal(len(barcode_test.angles), 8)
    assert_array_almost_equal(barcode_test.angles[0], [np.nan, np.nan, np.nan, np.nan])

    assert_equal(barcode_test.bifs[1], 26.3027)
    assert_equal(barcode_test.terms[1], 204.0442)
    assert_array_almost_equal(barcode_test.angles[1], [-0.279172, -0.138322,  1.598153,  0.672246])

    assert_array_almost_equal(barcode_test.get_bar(0), (0, 633.5966))
    assert_array_almost_equal(barcode_test.get_bar(1), (26.3027, 204.0442))

    assert_array_almost_equal(barcode_test.min_bif(),  (1, 26.3027))
    assert_array_almost_equal(barcode_test.min_term(), (2, 155.8809))
    assert_array_almost_equal(barcode_test.max_term(), (0, 633.5966))

    barcode_test.remove_bif(1)
    assert_array_almost_equal(barcode_test.min_bif(), (2, 52.4013))

    barcode_test.remove_term(2)
    assert_array_almost_equal(barcode_test.min_term(), (1, 204.0442))


def test_TMDStop():
    tmd_stop = TMDStop(1, 26.3027, 0, 633.5966, 10.0)
    assert_equal(tmd_stop.bif_id, 1)
    assert_equal(tmd_stop.term_id, 0)
    assert_equal(tmd_stop.bif, 26.3027)
    assert_equal(tmd_stop.term, 633.5966)
    assert_equal(tmd_stop.ref, 10.)
    assert_equal(tmd_stop.child_length(), 607.2939)
    assert_equal(tmd_stop.expected_length(), 16.3027)
    # Comparison should pass for same TMDstop
    assert(tmd_stop == TMDStop(1, 26.3027, 0, 633.5966, 10.0))
    # Comparison should fail for not same TMDstop
    assert(not tmd_stop == TMDStop(1, 20, 0, 633.5966, 10.0))
    # Comparison should fail for other object
    assert(not tmd_stop == 10)

    tmd_stop.update_bif(0, 11.)
    assert_equal(tmd_stop.bif_id, 0)
    assert_equal(tmd_stop.bif, 11.)

    tmd_stop.update_term(10, 110.)
    assert_equal(tmd_stop.term_id, 10)
    assert_equal(tmd_stop.term, 110.)

