
'''Test tns.generate.diametrizer code'''
import os
from nose import tools as nt
import numpy as np
from numpy.testing import assert_array_almost_equal
from tns.generate import diametrizer
import morphio
from morphio import SectionType

_path = os.path.dirname(os.path.abspath(__file__))
NEU_PATH1 = os.path.join(_path, '../test_data/diam_simple.swc')
NEU_PATH2 = os.path.join(_path, '../test_data/simple.swc')
NEU_PATH3 = os.path.join(_path, '../test_data/diam_simple_axon.swc')

MODEL = {3: {'Rall_ratio': 2./3.,
             'siblings_ratio': 1.0,
             'taper': [0.1],
             'term':  [0.6],
             'trunk': [4., 3.],
             'trunk_taper': [0.6]},
         2: {'Rall_ratio': 2./3.,
             'siblings_ratio': 1.0,
             'taper': [0.1],
             'term':  [0.6],
             'trunk': [4., 3.],
             'trunk_taper': [0.6]}}

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


def test_taper_section_diam_from_root():
    neu1 = morphio.mut.Morphology(NEU_PATH1)
    section = neu1.root_sections[0]
    diametrizer.taper_section_diam_from_root(section, 4., 0.6, 0.07, 100.)
    assert_array_almost_equal(section.diameters,
                              [4., 3.9, 3.8, 3.7, 3.6, 3.5, 3.4])

    section1 = section.children[0]
    diametrizer.taper_section_diam_from_root(section1, 4., 0.5, 0.07, 100.)
    assert_array_almost_equal(section1.diameters,
                              [4., 4., 3.9, 3.8, 3.7, 3.6])

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
                              [4.   , 3.9  , 3.8  , 3.7  , 3.6  , 3.5  , 3.4  , 2.8  , 2.8  ,
                               2.704, 2.608, 2.512, 2.416, 2.8  , 2.8  , 2.76 , 2.72 , 2.68 ,
                               2.64])

def test_diametrize_from_root():
    neu1 = morphio.mut.Morphology(NEU_PATH1) # has to be loaded to start clean
    np.random.seed(0) # ensure constant random number for sampling
    diametrizer.diametrize_from_root(neu1, MODEL)
    assert_array_almost_equal(morphio.Morphology(neu1).diameters,
                              [4.      , 3.9     , 3.8     , 3.7     , 3.6     , 3.5     ,
                               3.4     , 3.4     , 1.202082, 1.182082, 1.162082, 1.142082,
                               1.122082, 3.4     , 1.202082, 1.182082, 1.162082, 1.142082,
                               1.122082])

    neu2 = morphio.mut.Morphology(NEU_PATH3) # has to be loaded to start clean
    np.random.seed(0) # ensure constant random number for sampling
    diametrizer.diametrize_from_root(neu2, MODEL, neurite_type=SectionType.axon)
    assert_array_almost_equal(morphio.Morphology(neu2).diameters,
                              [4.,         3.8,        3.6,        3.4,        3.2,       3.,
                               2.8 ,       2.8,        2.8,        2.6,        2.4,       2.2,
                               2.  ,       2.8,        2. ,        2.4,        2. ,       2.2,
                               2.  ,       4.,        3.9142857,   3.8285713, 3.7428572,  3.6571429,
                               3.5714285, 3.4857142, 3.4])

def test_diametrize_from_tips():
    neu1 = morphio.mut.Morphology(NEU_PATH1) # has to be loaded to start clean
    np.random.seed(0) # ensure constant random number for sampling
    diametrizer.diametrize_from_tips(neu1, MODEL)
    assert_array_almost_equal(morphio.Morphology(neu1).diameters,
                              [2.52333 , 2.423331, 2.32333 , 2.22333 , 2.12333 , 2.02333 ,
                               1.92333 , 1.92333 , 0.68    , 0.66    , 0.64    , 0.62    ,
                               0.6     , 1.92333 , 0.68    , 0.66    , 0.64    , 0.62    ,
                               0.6])

    neu2 = morphio.mut.Morphology(NEU_PATH3) # has to be loaded to start clean
    np.random.seed(0) # ensure constant random number for sampling
    diametrizer.diametrize_from_tips(neu2, MODEL, neurite_type=SectionType.axon)
    assert_array_almost_equal(morphio.Morphology(neu2).diameters,
                              [4.,         3.8,        3.6,        3.4,        3.2,       3.,
                               2.8 ,       2.8,        2.8,        2.6,        2.4,       2.2,
                               2.  ,       2.8,        2. ,        2.4,        2. ,       2.2,
                               2.  ,      1.2,         1.1142857,  1.0285715,  0.94285715, 0.85714287,
                               0.7714286,  0.6857143,  0.6])
