import json
import os
from os.path import join
from nose.tools import assert_equal
import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal
from mock import patch

import morphio

from tns.extract_input import distributions
from tns.generate.grower import NeuronGrower

import tns

_path = os.path.dirname(os.path.abspath(__file__))

