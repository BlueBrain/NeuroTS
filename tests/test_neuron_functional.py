'''
This test ensures that the radial and path distances are computed correctly through TNS,
so that the code is treating the input barcode, according to the given parameters.
For this reason, we need to check that the same input distribution
will generate cells with different properties, according to their input parameters.
Finally, we need to check the TMD of the produced cells.
'''


import json
import os
from os.path import join
import numpy as np
from scipy.spatial.distance import cdist
from numpy.testing import assert_almost_equal, assert_array_almost_equal
from nose.tools import assert_raises

from tns.generate.grower import NeuronGrower
import tmd

_path = os.path.dirname(os.path.abspath(__file__))


persistence_path = [
 [147.20000053458375, 147.00000569874925],
 [209.20000351715382, 209.00000285171186],
 [51.79999926202536, 45.60000046346291],
 [219.60000582145892, 213.40000277616616],
 [90.99999882765516, 83.79999833784163],
 [727.0000125966322, 717.799974552356],
 [121.40000016956628, 106.19999839239988],
 [165.9999995161345, 148.8000011061286],
 [198.40000363708106, 181.2000014053565],
 [208.60000476796716, 190.40000604333474],
 [72.99999905769667, 53.79999978116803],
 [108.80000051677195, 83.59999926890146],
 [709.7999715012121, 682.6000110498246],
 [123.19999930450683, 89.99999970054269],
 [68.79999901964474, 34.399999471106874],
 [728.999980328755, 688.7999963493486],
 [215.600009276099, 175.20000418871288],
 [744.7999542588817, 693.5999975344931],
 [236.39999784328506, 161.00000286102295],
 [119.80000059501508, 44.40000057220459],
 [229.6000052267389, 145.80000591278076],
 [740.8000026628766, 655.5999807987467],
 [734.7999928816595, 643.5999910995974],
 [751.9999915038767, 655.3999814987183],
 [146.00000041634328, 42.59999956069521],
 [744.7999574589456, 622.4000048848823],
 [744.7999952073446, 609.199969291687],
 [221.20000486659995, 82.60000133514404],
 [167.39999445969153, 20.199999809265137],
 [787.9999858934324, 0.0]]


persistence_radial = [
 [206.80955996771064, 206.86562892203708],
 [149.51820214944297, 149.39999675750732],
 [216.68650190579416, 215.19999980926514],
 [117.77417128677507, 112.00000286102295],
 [50.83036105178722, 44.999999046325684],
 [167.97137576792525, 161.80964800109118],
 [725.5780920061723, 717.8000059127808],
 [92.11149514692896, 82.6437332668348],
 [710.3171712922573, 694.0011477152542],
 [217.90529896077575, 192.00000286102295],
 [73.70359646776672, 44.60000133514404],
 [121.45646944204107, 91.79999828338623],
 [210.9271441094319, 180.71577056186493],
 [116.5152201795077, 83.60000133514404],
 [68.92560440817996, 35.40000057220459],
 [734.4158157185843, 690.5999937057495],
 [235.72340888487685, 174.80000591278076],
 [746.743180383091, 683.3999814987183],
 [111.8269357827278, 44.79999828338623],
 [221.27957651106047, 149.5999937057495],
 [738.3718498415333, 658.199969291687],
 [228.47602958292111, 145.19999980926514],
 [166.78606841863785, 82.39999675750732],
 [145.41052757563006, 58.19999980926514],
 [733.6087793797262, 645.8000059127808],
 [752.4153030211291, 658.000018119812],
 [743.7305702900078, 622.5999937057495],
 [744.0235203944701, 606.3999814987183],
 [197.30083785561723, 20.199999809265137],
 [789.000018119812, 0.0]]


def test_radial_grower():
    np.random.seed(0)
    with open(join(_path, 'bio_distribution.json')) as f:
        distributions = json.load(f)

    with open(join(_path, 'bio_radial_params.json')) as f:
        params = json.load(f)
    n = NeuronGrower(input_distributions=distributions,
                     input_parameters=params).grow()
    n.write('test_output_neuron.h5')
    # Load with TMD and extract radial persistence
    n0 = tmd.io.load_neuron('test_output_neuron.h5')
    persistence_radial0 = tmd.methods.get_persistence_diagram(n0.apical[0])
    # compute distances between points
    distances = np.min(cdist(np.array(tmd.analysis.sort_ph(persistence_radial0)), persistence_radial), axis=0)
    # We compare distances between expected and generated peristence as it is more stable to check.
    # This comparison does not depend on ordering of the points
    # and ensures that the points of the original persistence are consistently generated.
    assert_array_almost_equal(distances, np.zeros(len(distances)), decimal=0.1)
    assert_almost_equal(0.1*np.max(persistence_radial0[-1]), 0.1*789, decimal=1)
    assert_almost_equal(len(persistence_radial0), 30)
    os.remove('test_output_neuron.h5')

def test_path_grower():
    np.random.seed(0)
    with open(join(_path, 'bio_distribution.json')) as f:
        distributions = json.load(f)

    with open(join(_path, 'bio_path_params.json')) as f:
        params = json.load(f)

    assert_raises(TypeError, NeuronGrower, input_distributions=distributions, input_parameters=params)

    # Modify the filtration metric from 'radial' to 'path' to create a path-based tree
    for tree_type in params["grow_types"]:
        distributions[tree_type]["filtration_metric"] = "path_distances"

    n = NeuronGrower(input_distributions=distributions,
                         input_parameters=params).grow()

    n.write('test_output_neuron.h5')
    # Load with TMD and extract path persistence
    n0 = tmd.io.load_neuron('test_output_neuron.h5')
    persistence_path0 = tmd.methods.get_persistence_diagram(n0.apical[0], feature='path_distances')
    # compute distances between points
    distances = np.min(cdist(np.array(tmd.analysis.sort_ph(persistence_path0)), persistence_path), axis=0)
    # We compare distances between expected and generated peristence as it is more stable to check.
    # This comparison does not depend on ordering of the points
    # and ensures that the points of the original persistence are consistently generated.
    assert_array_almost_equal(distances, np.zeros(len(distances)), decimal=0.1)
    assert_almost_equal(0.1*np.max(persistence_path0[-1]), 0.1*789, decimal=1)
    assert_almost_equal(len(persistence_path0), 30)
    os.remove('test_output_neuron.h5')
