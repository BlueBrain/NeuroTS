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
 [207.37242864008527, 206.67304991586843],
 [149.13219860221605, 148.19999980926514],
 [218.48465485835692, 212.8462813552555],
 [116.58430734281842, 109.19999980926514],
 [51.41230365496356, 43.860170225208336],
 [90.92654821288686, 83.03557944343636],
 [726.8239034596626, 717.8823462115529],
 [166.88508976430717, 148.91448097525185],
 [197.92150592758176, 175.94622190045175],
 [707.7245639335821, 681.8208743050907],
 [218.3607296988281, 188.8559447892736],
 [122.24710223386323, 90.25428613028305],
 [75.13862741069278, 42.76816159646294],
 [68.16083603612628, 34.7856245174865],
 [117.60843803650725, 82.26322490283218],
 [733.8826777977234, 689.9424250159067],
 [740.747478612731, 692.7700874614688],
 [210.9299857421062, 161.19999980926514],
 [234.83429770981786, 183.19999980926514],
 [110.80990926288878, 44.19999980926514],
 [221.66190848935105, 145.91627562155324],
 [744.8208380804692, 657.9034012027264],
 [144.25147057637847, 56.43839878937238],
 [733.9213577212244, 644.9535488497276],
 [752.900810058582, 657.1622152787452],
 [745.624293931535, 626.199969291687],
 [743.886632011925, 606.199969291687],
 [228.21311104025045, 82.19999980926514],
 [166.31058997497564, 20.199999809265137],
 [789.0284158932299, 0.0]]

persistence_radial = [
 [207.9942460620183, 207.27943220500885],
 [148.11820907627123, 147.19999980926514],
 [48.72439347701012, 45.02626514123144],
 [219.61356260041325, 215.19999980926514],
 [90.73260098017508, 84.01160795183155],
 [726.2355439335804, 718.0262837049702],
 [119.71268016006206, 111.19999980926514],
 [211.1371074067961, 190.8990322636309],
 [710.1861276659496, 683.199969291687],
 [122.8035742533468, 93.19999980926514],
 [74.46797715604012, 44.19999980926514],
 [67.22887232947798, 32.24752620742019],
 [120.37231942373472, 84.19999980926514],
 [198.4335188719044, 162.19999980926514],
 [215.68999605806226, 177.19999980926514],
 [734.3471094781196, 690.199969291687],
 [745.9648254120617, 693.199969291687],
 [236.3182839196952, 183.19999980926514],
 [110.38007388102761, 45.19999980926514],
 [220.74925166793224, 148.28991552829015],
 [164.0720416126582, 83.19999980926514],
 [740.1594315044697, 659.199969291687],
 [140.4427147680882, 58.19999980926514],
 [227.97786779351713, 145.19999980926514],
 [732.7645254452814, 644.199969291687],
 [751.6084341031545, 658.199969291687],
 [743.6891716302976, 623.199969291687],
 [744.0381973306002, 608.199969291687],
 [167.37710860008943, 20.199999809265137],
 [787.199969291687, 0.0]]


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
    assert_almost_equal(0.1*np.max(persistence_radial0[-1]), 0.1*789, decimal=0.1)
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
    assert_almost_equal(0.1*np.max(persistence_path0[-1]), 0.1*789, decimal=0.1)
    assert_almost_equal(len(persistence_path0), 30)
    os.remove('test_output_neuron.h5')
