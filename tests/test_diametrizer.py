
'''Test tns.generate.diametrizer code'''
import os
from nose import tools as nt
import numpy as np
from numpy.testing import assert_array_almost_equal
from tns.generate import diametrizer
import morphio

_path = os.path.dirname(os.path.abspath(__file__))
NEU_PATH1 = os.path.join(_path, '../test_data/diam_simple.swc')
NEU_PATH2 = os.path.join(_path, '../test_data/simple.swc')

MODEL = {3: {'Rall_ratio': 2./3.,
             'siblings_ratio': 1.0,
             'taper': [0.1],
             'term':  [0.6],
             'trunk': [4., 3.],
             'trunk_taper': [0.2]}}

def test_sample():
    assert(diametrizer.sample([0.]) == 0.)
    np.random.seed(0)
    assert(diametrizer.sample([1., 1., 1., 2., 2., 3.]) == 2.)

def test_bifurcator():
    d1 = diametrizer.bifurcator(1.0, 2., 3./2., 1.)
    assert(d1 == 0.6299605249474366)
    d1 = diametrizer.bifurcator(1.0, 2., 1., 1.)
    assert(d1 == 0.5)
    d1 = diametrizer.bifurcator(1.0, 2., 1., 0.5)
    assert(d1 == 0.6666666666666666)


def test_taper_section_diam():
    neu1 = morphio.mut.Morphology(NEU_PATH1)
    section = neu1.root_sections[0]
    diametrizer.taper_section_diam(section, 4., 0.3, 0.07, 100.)
    assert_array_almost_equal(section.diameters,
                              [4. , 3.8, 3.6, 3.4, 3.2, 3. , 2.8])

def test_diametrize_constant_per_section():
    neu2 = morphio.mut.Morphology(NEU_PATH2) # has to be loaded to start clean
    diametrizer.diametrize_constant_per_section(neu2)
    assert_array_almost_equal(morphio.Morphology(neu2).diameters,
                              [2., 2., 2.5, 2.5, 2.5, 2.5, 2., 2., 3., 3., 3., 3.])

def test_diametrize_constant_per_neurite():
    neu2 = morphio.mut.Morphology(NEU_PATH2) # has to be loaded to start clean
    diametrizer.diametrize_constant_per_neurite(neu2)
    assert_array_almost_equal(morphio.Morphology(neu2).diameters,
                              [2.333333, 2.333333, 2.333333, 2.333333, 2.333333, 2.333333,
                               2.666667, 2.666667, 2.666667, 2.666667, 2.666667, 2.666667])

def test_diametrize_smoothing():
    neu1 = morphio.mut.Morphology(NEU_PATH1) # has to be loaded to start clean
    diametrizer.diametrize_smoothing(neu1)
    assert_array_almost_equal(morphio.Morphology(neu1).diameters,
                              [4.      , 3.6     , 3.2     , 2.8     , 2.4     , 2.      ,
                               1.599999, 2.8     , 2.8     , 2.5312  , 2.2624  , 1.9936  ,
                               1.7248  , 2.8     , 2.8     , 2.688   , 2.576   , 2.464   ,
                               2.352])

def test_diametrize_from_root():
    neu1 = morphio.mut.Morphology(NEU_PATH1) # has to be loaded to start clean
    np.random.seed(0) # ensure constant random number for sampling
    diametrizer.diametrize_from_root(neu1, MODEL)
    assert_array_almost_equal(morphio.Morphology(neu1).diameters,
                              [3.      , 2.9     , 2.8     , 2.7     , 2.6     , 2.5     ,
                               2.4     , 2.4     , 0.848528, 0.831558, 0.814587, 0.797616,
                               0.780646, 2.4     , 0.848528, 0.831558, 0.814587, 0.797616,
                               0.780646])

def test_diametrize_from_tips():
    neu1 = morphio.mut.Morphology(NEU_PATH1) # has to be loaded to start clean
    np.random.seed(0) # ensure constant random number for sampling
    diametrizer.diametrize_from_tips(neu1, MODEL)
    assert_array_almost_equal(morphio.Morphology(neu1).diameters,
                              [1.770291, 1.711282, 1.652272, 1.593262, 1.534253, 1.475243,
                               1.416233, 1.416233, 0.62    , 0.6076  , 0.6     , 0.6     ,
                               0.6     , 1.416233, 0.62    , 0.6076  , 0.6     , 0.6     ,
                               0.6])
