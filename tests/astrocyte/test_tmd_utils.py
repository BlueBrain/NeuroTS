import numpy as np
from numpy import testing as npt

from neurots.astrocyte import tmd_utils as _tu


def _barcode():
    return [
    [230.75389593157917, 174.56457422613303],
    [1072.5500821184357, 0]
]


def _barcode_list():
    return [
    [[230.75389593157917, 174.56457422613303], [1072.5500821184357, 0]],
    [[461.50779186315833, 349.12914845226607], [2145.1001642368715, 0]],
    [[692.2616877947376, 523.6937226783991], [3217.650246355307, 0]],
    [[923.0155837263167, 698.2582969045321], [4290.200328473743, 0]],
    [[1153.7694796578958, 872.8228711306651], [5362.750410592179, 0]]
]


def test_scale_barcode():

    barcode = _barcode()

    target_distance = 2. * 1072.5500821184357

    ph = _tu.scale_barcode(barcode, target_distance)

    expected = np.asarray(barcode) * 2.
    npt.assert_allclose(ph, expected)

    target_distance = 0.8 * 1072.5500821184357

    ph = _tu.scale_barcode(barcode, target_distance)
    npt.assert_allclose(ph, barcode)


def test_barcodes_greater_than_distance():

    barcode_list = _barcode_list()

    result = _tu.barcodes_greater_than_distance(barcode_list, 3000.)

    npt.assert_equal(len(result), 3)
    npt.assert_allclose(result, barcode_list[2:])
