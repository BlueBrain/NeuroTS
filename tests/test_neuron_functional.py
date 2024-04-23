"""Test the neurots.generate.grower.NeuronGrower class.

This test ensures that the radial and path distances are computed correctly through NeuroTS,
so that the code is treating the input barcode, according to the given parameters.
For this reason, we need to check that the same input distribution
will generate cells with different properties, according to their input parameters.
Finally, we need to check the TMD of the produced cells.
"""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=protected-access
import json
import os
from os.path import basename
from os.path import join
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pytest
import tmd
from morph_tool import diff
from morphio import PointLevel
from morphio import SectionType
from morphio.mut import Morphology as MorphioMorphology
from neurom.core import Morphology
from numpy.testing import assert_almost_equal
from numpy.testing import assert_array_almost_equal
from numpy.testing import assert_array_equal
from scipy.spatial.distance import cdist

from neurots import extract_input
from neurots.generate.diametrizer import diametrize_constant_per_neurite
from neurots.generate.grower import NeuronGrower
from neurots.preprocess.exceptions import NeuroTSValidationError

DATA_PATH = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_data"))
_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def build_random_generator(seed=None):
    mt = np.random.MT19937()
    mt._legacy_seeding(seed)  # Use legacy seeding to get the same result as with np.random.seed()
    return np.random.RandomState(mt)


def assert_close_persistent_diagram(actual, expected):
    # compute distances between points
    distances = np.min(cdist(np.array(tmd.analysis.sort_ph(expected)), actual), axis=0)
    # We compare distances between expected and generated persistence as it is more stable to check.
    # This comparison does not depend on ordering of the points
    # and ensures that the points of the original persistence are consistently generated.
    assert_almost_equal(len(expected), len(actual))
    assert_array_almost_equal(distances, np.zeros(len(distances)), decimal=0.1)
    assert_almost_equal(np.max(expected[-1]), np.max(actual[-1]), decimal=0.1)


def _load_inputs(distributions, parameters):
    with open(distributions, encoding="utf-8") as f:
        distributions = json.load(f)

    with open(parameters, encoding="utf-8") as f:
        params = json.load(f)

    return distributions, params


def _test_full(
    feature,
    distributions,
    parameters,
    ref_cell,
    ref_persistence_diagram,
    rng_or_seed=None,
    skip_preprocessing=False,
    output_dir=None,
):
    distributions, params = _load_inputs(join(_path, distributions), join(_path, parameters))
    if rng_or_seed is None:
        np.random.seed(0)
        n = NeuronGrower(
            input_distributions=distributions,
            input_parameters=params,
            skip_preprocessing=skip_preprocessing,
        ).grow()
    else:
        n = NeuronGrower(
            input_distributions=distributions,
            input_parameters=params,
            rng_or_seed=rng_or_seed,
            skip_preprocessing=skip_preprocessing,
        ).grow()

    with TemporaryDirectory("test_grower") as folder:
        out_neuron = join(folder, "test_output_neuron_.h5")
        n.write(out_neuron)

        # For checking purposes, we can output the cells as swc
        if output_dir is not None:
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            n.write(join(output_dir, basename(ref_cell)))

        if ref_persistence_diagram is not None:
            # Load with TMD and extract radial persistence
            n0 = tmd.io.load_neuron(out_neuron)

            actual_persistence_diagram = tmd.methods.get_persistence_diagram(
                n0.apical_dendrite[0], feature=feature
            )
            if output_dir is not None:
                with open(
                    join(output_dir, basename(ref_persistence_diagram)), "w", encoding="utf-8"
                ) as f:
                    json.dump(actual_persistence_diagram, f, sort_keys=True, indent=2)

            with open(join(_path, ref_persistence_diagram), encoding="utf-8") as f:
                expected_persistence_diagram = json.load(f)
            assert_close_persistent_diagram(
                actual_persistence_diagram, expected_persistence_diagram
            )
        assert not diff(out_neuron, join(_path, ref_cell))


def test_wrong_filtration():
    """Test filtration metric inconsistency in distrib and params: path != radial"""
    distributions, parameters = _load_inputs(
        os.path.join(_path, "bio_path_distribution.json"),
        os.path.join(_path, "bio_radial_params.json"),
    )
    with pytest.raises(ValueError):
        NeuronGrower(parameters, distributions)


def test_seeding():
    """Test seeding of internal random number generator"""
    distributions, parameters = _load_inputs(
        os.path.join(_path, "bio_path_distribution.json"),
        os.path.join(_path, "bio_path_params.json"),
    )
    ng = NeuronGrower(parameters, distributions, rng_or_seed=0)
    assert ng._rng.bit_generator.state == {
        "bit_generator": "PCG64",
        "state": {
            "state": 80186449399738619878794082838194943960,
            "inc": 87136372517582989555478159403783844777,
        },
        "has_uint32": 0,
        "uinteger": 0,
    }

    ng = NeuronGrower(parameters, distributions, rng_or_seed=None)
    assert ng._rng.bit_generator.state["bit_generator"] == "PCG64"


def test_grow_trunk_1_basal():
    """Test NeuronGrower._grow_trunk() with only 1 basal (should raise an Exception)"""
    distributions, parameters = _load_inputs(
        os.path.join(_path, "bio_path_distribution.json"),
        os.path.join(_path, "bio_path_params.json"),
    )
    distributions["basal_dendrite"]["num_trees"]["data"]["bins"] = [1]
    ng = NeuronGrower(parameters, distributions)
    with pytest.raises(Exception, match=r"There should be at least 2 basal dendrites \(got 1\)"):
        ng.grow()

    parameters["basal_dendrite"]["orientation"] = {
        "mode": "use_predefined",
        "values": {"orientations": [[0.0, 1.0, 0.0]]},
    }
    ng = NeuronGrower(parameters, distributions)
    with pytest.raises(Exception, match=r"There should be at least 2 basal dendrites \(got 1\)"):
        ng.grow()


def test_external_diametrizer():
    """Test external diametrizer"""
    distributions, parameters = _load_inputs(
        os.path.join(_path, "bio_path_distribution.json"),
        os.path.join(_path, "bio_path_params.json"),
    )
    distributions["diameter"] = {"method": "M1"}
    parameters["diameter_params"] = {"method": "M1"}
    ng = NeuronGrower(parameters, distributions, rng_or_seed=0)
    ng.grow()

    # Inconsistent methods
    distributions["diameter"]["method"] = "external"
    parameters["diameter_params"]["method"] = "M1"
    with pytest.raises(
        ValueError,
        match="Diameters methods of parameters and distributions is inconsistent: M1 != external",
    ):
        NeuronGrower(parameters, distributions)

    # No external diametrizer provided
    distributions["diameter"]["method"] = "external"
    parameters["diameter_params"]["method"] = "external"
    with pytest.raises(
        ValueError, match="External diametrizer is missing the diametrizer function."
    ):
        NeuronGrower(parameters, distributions)

    # Test with an external diametrizer and neurite_types in diameter_params
    distributions["diameter"]["method"] = "external"
    parameters["diameter_params"]["method"] = "external"
    parameters["diameter_params"]["neurite_types"] = parameters["grow_types"]
    ng_external = NeuronGrower(
        parameters,
        distributions,
        external_diametrizer=diametrize_constant_per_neurite,
        rng_or_seed=0,
    )
    ng_external.grow()

    assert (Morphology(ng.neuron).points == Morphology(ng_external.neuron).points).all()


def test_convert_orientation2points():
    """Test NeuronGrower._convert_orientation2points()"""
    np.random.seed(0)
    distributions, parameters = _load_inputs(
        os.path.join(_path, "bio_path_distribution.json"),
        os.path.join(_path, "bio_path_params.json"),
    )
    distributions["diameter"] = {"method": "M1"}
    parameters["diameter_params"] = {"method": "M1"}
    ng = NeuronGrower(parameters, distributions)

    pts = ng._convert_orientation2points([[0, 1, 0]], 1, distributions["apical_dendrite"], {})
    assert_array_almost_equal(pts, [[0, 15.27995, 0]])

    # Test with no existing trunk
    ng = NeuronGrower(parameters, distributions)
    pts = ng._convert_orientation2points(None, 2, distributions["apical_dendrite"], {})
    assert_array_almost_equal(
        pts, [[-10.399604, -0.173343, 0.937449], [10.31932, 0.172005, -1.594578]]
    )

    with pytest.raises(ValueError):
        ng._convert_orientation2points("from_space", 1, distributions["apical_dendrite"], {})

    # Test with existing trunks
    ng.grow()
    pts = ng._convert_orientation2points(None, 2, distributions["apical_dendrite"], {})
    assert_array_almost_equal(
        pts, [[7.67743835, -1.93761793, 6.80905306], [9.98169472, 2.83123167, -1.18765494]]
    )

    with pytest.raises(ValueError):
        ng._convert_orientation2points(object(), 1, distributions["apical_dendrite"], {})

    with pytest.raises(ValueError):
        ng._convert_orientation2points([[0, 1, 0]], 99, distributions["apical_dendrite"], {})

    distributions, parameters = _load_inputs(
        os.path.join(_path, "axon_trunk_distribution.json"),
        os.path.join(_path, "axon_trunk_parameters_absolute.json"),
    )
    with pytest.raises(ValueError):
        ng._convert_orientation2points(
            [[0, 1, 0], [0, 1, 0]],
            1,
            distributions["axon"],
            {"trunk_absolute_orientation": True},
        )

    del distributions["axon"]["trunk"]["absolute_elevation_deviation"]
    with pytest.raises(KeyError):
        ng._convert_orientation2points(
            [[0, 1, 0]], 1, distributions["axon"], {"trunk_absolute_orientation": True}
        )


def test_breaker_of_tmd_algo():
    """Test example that could break tmd_algo. Test should fail if problem occurs.
    Otherwise, this grower should run smoothly.
    """
    distributions, params = _load_inputs(
        join(_path, "bio_distr_breaker.json"), join(_path, "bio_params_breaker.json")
    )
    np.random.seed(3367155)
    N = NeuronGrower(input_distributions=distributions, input_parameters=params)
    n = N.grow()

    assert_array_equal(N.apical_sections, [10])
    assert_array_almost_equal(
        n.sections[118].points[-1],
        np.array([-170.45485, 42.04766, -26.375393]),
        decimal=5,
    )
    assert_array_almost_equal(
        n.sections[30].points[-1], np.array([55.375633, 63.321762, -3.612582]), decimal=5
    )

    # Test with a specific random generator
    rng = build_random_generator(3367155)

    N = NeuronGrower(input_distributions=distributions, input_parameters=params, rng_or_seed=rng)
    n = N.grow()

    assert_array_equal(N.apical_sections, [10])
    assert_array_almost_equal(
        n.sections[118].points[-1],
        np.array([-170.45485, 42.04766, -26.375393]),
        decimal=5,
    )
    assert_array_almost_equal(
        n.sections[30].points[-1], np.array([55.375633, 63.321762, -3.612582]), decimal=5
    )


def test_axon_grower(tmpdir):
    """Test axon grower, which should only grow trunks with 1 section to allow later axon grafting.

    The num_seg value in the parameters is set to 999 but only 1 segment should be synthesized.
    """

    _test_full(
        "radial_distances",
        "axon_trunk_distribution.json",
        "axon_trunk_parameters.json",
        "test_axon_grower.h5",
        None,
        output_dir=tmpdir / "default",
    )
    _test_full(
        "radial_distances",
        "axon_trunk_distribution.json",
        "axon_trunk_parameters.json",
        "test_axon_grower.h5",
        None,
        rng_or_seed=build_random_generator(0),
        output_dir=tmpdir / "rng",
    )
    _test_full(
        "radial_distances",
        "axon_trunk_distribution.json",
        "axon_trunk_parameters_orientation_manager.json",
        "test_axon_grower.h5",
        None,
        skip_preprocessing=True,
        output_dir=tmpdir / "skip_preprocessing",
    )
    _test_full(
        "radial_distances",
        "axon_trunk_distribution.json",
        "axon_trunk_parameters_orientation_manager.json",
        "test_axon_grower.h5",
        None,
        rng_or_seed=build_random_generator(0),
        skip_preprocessing=True,
        output_dir=tmpdir / "rng_and_skip_preprocessing",
    )

    _test_full(
        "radial_distances",
        "axon_trunk_distribution.json",
        "axon_trunk_parameters_absolute.json",
        "test_axon_grower_absolute.h5",
        None,
        output_dir=tmpdir / "default_absolute",
    )
    _test_full(
        "radial_distances",
        "axon_trunk_distribution.json",
        "axon_trunk_parameters_absolute.json",
        "test_axon_grower_absolute.h5",
        None,
        rng_or_seed=build_random_generator(0),
        output_dir=tmpdir / "rng_absolute",
    )
    _test_full(
        "radial_distances",
        "axon_trunk_distribution.json",
        "axon_trunk_parameters_absolute_orientation_manager.json",
        "test_axon_grower_absolute.h5",
        None,
        skip_preprocessing=True,
        output_dir=tmpdir / "skip_preprocessing_absolute",
    )
    _test_full(
        "radial_distances",
        "axon_trunk_distribution.json",
        "axon_trunk_parameters_absolute_orientation_manager.json",
        "test_axon_grower_absolute.h5",
        None,
        rng_or_seed=build_random_generator(0),
        skip_preprocessing=True,
        output_dir=tmpdir / "rng_and_skip_preprocessing_absolute",
    )


def test_basic_grower(tmpdir):
    _test_full(
        "radial_distances",
        "bio_trunk_distribution.json",
        "trunk_parameters.json",
        "test_trunk_grower.h5",
        None,
        output_dir=tmpdir / "default",
    )
    _test_full(
        "radial_distances",
        "bio_trunk_distribution.json",
        "trunk_parameters.json",
        "test_trunk_grower.h5",
        None,
        rng_or_seed=build_random_generator(0),
        output_dir=tmpdir / "rng",
    )


def test_basic_grower_with_generator():
    distributions, params = _load_inputs(
        join(_path, "bio_trunk_distribution.json"),
        join(_path, "trunk_parameters.json"),
    )
    expected_pts = [
        [-0.7312348484992981, 7.604228973388672, 11.173797607421875],
        [-13.377432823181152, -1.2863954305648804, 2.9336819648742676],
        [11.861421585083008, -0.049414388835430145, 6.1279988288879395],
        [-2.3804218769073486, 12.54181957244873, 1.118072748184204],
    ]

    rng = np.random.default_rng(0)
    rng_or_seeds = [0, rng]

    for rng_or_seed in rng_or_seeds:
        n = NeuronGrower(
            input_distributions=distributions,
            input_parameters=params,
            rng_or_seed=rng_or_seed,
        ).grow()
        assert len(n.root_sections) == 4
        assert_array_almost_equal(
            [i.points[-1].tolist() for i in n.root_sections],
            expected_pts,
        )

    with pytest.raises(TypeError):
        NeuronGrower(params, distributions, rng_or_seed="NOT A SEED")


class TestPathGrower:
    """test tmd_path and tmd_apical_path"""

    def test_default(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_distribution.json",
            "bio_path_params.json",
            "path_grower.h5",
            "bio_path_persistence_diagram.json",
            output_dir=tmpdir,
        )

    def test_with_rng(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_distribution.json",
            "bio_path_params.json",
            "path_grower.h5",
            "bio_path_persistence_diagram.json",
            rng_or_seed=build_random_generator(0),
            output_dir=tmpdir,
        )

    def test_skip_preprocessing(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_distribution.json",
            "bio_path_params_orientation_manager.json",
            "path_grower.h5",
            "bio_path_persistence_diagram.json",
            skip_preprocessing=True,
            output_dir=tmpdir,
        )

    def test_skip_rng_and_preprocessing(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_distribution.json",
            "bio_path_params_orientation_manager.json",
            "path_grower.h5",
            "bio_path_persistence_diagram.json",
            skip_preprocessing=True,
            rng_or_seed=build_random_generator(0),
            output_dir=tmpdir,
        )

    def test_min_bar_length_missing(self, tmpdir):
        """Check that the proper exception is raised when the min_bar_length entry is missing."""
        with open(join(_path, "bio_distribution.json"), encoding="utf-8") as f:
            distributions = json.load(f)
        del distributions["apical_dendrite"]["min_bar_length"]
        broken_distribution = tmpdir / "bio_distribution.json"
        with open(broken_distribution, mode="w", encoding="utf-8") as f:
            json.dump(distributions, f)

        with pytest.raises(
            NeuroTSValidationError,
            match="'min_bar_length'",
        ):
            _test_full(
                "path_distances",
                broken_distribution,
                "bio_path_params.json",
                "path_grower.h5",
                "bio_path_persistence_diagram.json",
                output_dir=tmpdir,
            )


class TestGradientPathGrower:
    """test tmd_path"""

    def test_default(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_distribution.json",
            "bio_gradient_path_params.json",
            "gradient_path_grower.h5",
            "gradient_path_persistence_diagram.json",
            output_dir=tmpdir,
        )

    def test_with_rng(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_distribution.json",
            "bio_gradient_path_params.json",
            "gradient_path_grower.h5",
            "gradient_path_persistence_diagram.json",
            rng_or_seed=build_random_generator(0),
            output_dir=tmpdir,
        )

    def test_skip_preprocessing(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_distribution.json",
            "bio_gradient_path_params_orientation_manager.json",
            "gradient_path_grower.h5",
            "gradient_path_persistence_diagram.json",
            skip_preprocessing=True,
            output_dir=tmpdir,
        )

    def test_skip_rng_and_preprocessing(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_distribution.json",
            "bio_gradient_path_params_orientation_manager.json",
            "gradient_path_grower.h5",
            "gradient_path_persistence_diagram.json",
            skip_preprocessing=True,
            rng_or_seed=build_random_generator(0),
            output_dir=tmpdir,
        )


class TestBioRatL5Tpc1:
    def test_default(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params1.json",
            "expected_bio_rat_L5_TPC_B_with_params1.h5",
            "expected_bio_rat_L5_TPC_B_with_params1_persistence_diagram.json",
            output_dir=tmpdir,
        )

    def test_with_rng(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params1.json",
            "expected_bio_rat_L5_TPC_B_with_params1.h5",
            "expected_bio_rat_L5_TPC_B_with_params1_persistence_diagram.json",
            rng_or_seed=build_random_generator(0),
            output_dir=tmpdir,
        )

    def test_skip_preprocessing(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params1_orientation_manager.json",
            "expected_bio_rat_L5_TPC_B_with_params1.h5",
            "expected_bio_rat_L5_TPC_B_with_params1_persistence_diagram.json",
            skip_preprocessing=True,
            output_dir=tmpdir,
        )

    def test_skip_rng_and_preprocessing(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params1_orientation_manager.json",
            "expected_bio_rat_L5_TPC_B_with_params1.h5",
            "expected_bio_rat_L5_TPC_B_with_params1_persistence_diagram.json",
            skip_preprocessing=True,
            rng_or_seed=build_random_generator(0),
            output_dir=tmpdir,
        )


class TestBioRatL5Tpc2:
    def test_default(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params2.json",
            "expected_bio_rat_L5_TPC_B_with_params2.h5",
            "expected_bio_rat_L5_TPC_B_with_params2_persistence_diagram.json",
            output_dir=tmpdir,
        )

    def test_with_rng(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params2.json",
            "expected_bio_rat_L5_TPC_B_with_params2.h5",
            "expected_bio_rat_L5_TPC_B_with_params2_persistence_diagram.json",
            rng_or_seed=build_random_generator(0),
            output_dir=tmpdir,
        )

    def test_skip_preprocessing(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params2_orientation_manager.json",
            "expected_bio_rat_L5_TPC_B_with_params2.h5",
            "expected_bio_rat_L5_TPC_B_with_params2_persistence_diagram.json",
            skip_preprocessing=True,
            output_dir=tmpdir,
        )

    def test_skip_rng_and_preprocessing(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params2_orientation_manager.json",
            "expected_bio_rat_L5_TPC_B_with_params2.h5",
            "expected_bio_rat_L5_TPC_B_with_params2_persistence_diagram.json",
            skip_preprocessing=True,
            rng_or_seed=build_random_generator(0),
            output_dir=tmpdir,
        )


class TestBioRatL5Tpc3:
    def test_default(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params3.json",
            "expected_bio_rat_L5_TPC_B_with_params3.h5",
            "expected_bio_rat_L5_TPC_B_with_params3_persistence_diagram.json",
            output_dir=tmpdir,
        )

    def test_with_rng(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params3.json",
            "expected_bio_rat_L5_TPC_B_with_params3.h5",
            "expected_bio_rat_L5_TPC_B_with_params3_persistence_diagram.json",
            rng_or_seed=build_random_generator(0),
            output_dir=tmpdir,
        )

    def test_skip_preprocessing(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params3_orientation_manager.json",
            "expected_bio_rat_L5_TPC_B_with_params3.h5",
            "expected_bio_rat_L5_TPC_B_with_params3_persistence_diagram.json",
            skip_preprocessing=True,
            output_dir=tmpdir,
        )

    def test_skip_rng_and_preprocessing(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params3_orientation_manager.json",
            "expected_bio_rat_L5_TPC_B_with_params3.h5",
            "expected_bio_rat_L5_TPC_B_with_params3_persistence_diagram.json",
            skip_preprocessing=True,
            rng_or_seed=build_random_generator(0),
            output_dir=tmpdir,
        )


class TestBioRatL5Tpc4:
    def test_default(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params4.json",
            "expected_bio_rat_L5_TPC_B_with_params4.h5",
            "expected_bio_rat_L5_TPC_B_with_params4_persistence_diagram.json",
            output_dir=tmpdir,
        )

    def test_with_rng(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params4.json",
            "expected_bio_rat_L5_TPC_B_with_params4.h5",
            "expected_bio_rat_L5_TPC_B_with_params4_persistence_diagram.json",
            rng_or_seed=build_random_generator(0),
            output_dir=tmpdir,
        )

    def test_skip_preprocessing(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params4_orientation_manager.json",
            "expected_bio_rat_L5_TPC_B_with_params4.h5",
            "expected_bio_rat_L5_TPC_B_with_params4_persistence_diagram.json",
            skip_preprocessing=True,
            output_dir=tmpdir,
        )

    def test_skip_rng_and_preprocessing(self, tmpdir):
        _test_full(
            "path_distances",
            "bio_rat_L5_TPC_B_distribution.json",
            "params4_orientation_manager.json",
            "expected_bio_rat_L5_TPC_B_with_params4.h5",
            "expected_bio_rat_L5_TPC_B_with_params4_persistence_diagram.json",
            skip_preprocessing=True,
            rng_or_seed=build_random_generator(0),
            output_dir=tmpdir,
        )


def test_early_apical_bifurcation(tmpdir):
    """Ensures that we get an equal number of obliques on each subtrunk."""
    np.random.seed(42)
    morpho = MorphioMorphology(DATA_PATH / "bio" / "Fluo55_left.h5")
    for section in morpho.root_sections:
        if section.type in [SectionType.apical_dendrite, SectionType.axon]:
            morpho.delete_section(section, recursive=True)

    root = morpho.append_root_section(
        PointLevel([[0, 1, 0], [0, 10, 0]], [2, 2]), SectionType.apical_dendrite
    )
    main1_0 = root.append_section(PointLevel([[0, 10, 0], [-10, 20, 0]], [1, 1]))
    main2_0 = root.append_section(PointLevel([[0, 10, 0], [10, 30, 0]], [1, 1]))

    main1_0.append_section(PointLevel([[-10, 20, 0], [-20, 20, 0]], [0.5, 0.5]))
    main1_1 = main1_0.append_section(PointLevel([[-10, 20, 0], [-15, 50, 0]], [1, 1]))

    main2_0.append_section(PointLevel([[10, 30, 0], [20, 30, 0]], [0.5, 0.5]))
    main2_1 = main2_0.append_section(PointLevel([[10, 30, 0], [15, 40, 0]], [1, 1]))

    main1_1.append_section(PointLevel([[-15, 50, 0], [-25, 50, 0]], [0.5, 0.5]))
    main1_1.append_section(PointLevel([[-15, 50, 0], [-20, 100, 0]], [1, 1]))

    main2_1.append_section(PointLevel([[15, 40, 0], [25, 40, 0]], [0.5, 0.5]))
    main2_1.append_section(PointLevel([[15, 40, 0], [20, 110, 0]], [1, 1]))

    morpho.write(tmpdir / "input_cell.asc")
    distr = extract_input.distributions(
        str(tmpdir / "input_cell.asc"), neurite_types=["apical_dendrite"]
    )
    params = extract_input.parameters(neurite_types=["apical_dendrite"])
    params["apical_dendrite"]["randomness"] = 0.05
    params["apical_dendrite"]["bias"] = 1.0
    params["apical_dendrite"]["bias_length"] = 0.9
    params["apical_dendrite"]["growth_method"] = "tmd_gradient"
    params["apical_dendrite"]["branching_method"] = "bio_oriented"
    params["apical_dendrite"]["step_size"]["norm"]["mean"] = 5

    synth_morph = NeuronGrower(
        input_distributions=distr, input_parameters=params, skip_preprocessing=True
    ).grow()
    difference = diff(synth_morph, _path + "/bi_apical.asc", rtol=1e-3, atol=1e-2)
    assert not difference, difference.info
