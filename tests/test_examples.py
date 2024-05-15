"""Test the examples."""

# Copyright (C) 2022  Blue Brain Project, EPFL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=missing-function-docstring
import importlib.util as ilu
from pathlib import Path

EXAMPLES = Path(__file__).parent.parent / "examples"
DATA = EXAMPLES / "data"


def _run_example(example, tmpdir, data):
    name = example.split("/")[-1]
    spec = ilu.spec_from_file_location(name, example)
    current_example = ilu.module_from_spec(spec)
    spec.loader.exec_module(current_example)

    current_example.run(tmpdir, data)


def test_extract_synthesis_inputs(tmpdir):
    _run_example("examples/extract_synthesis_inputs.py", tmpdir, DATA)
    assert sorted([i.relto(tmpdir) for i in tmpdir.listdir()]) == [
        "generated_cell.asc",
        "generated_cell.h5",
        "generated_cell.swc",
        "test_distr.json",
        "test_params.json",
    ]


def test_synthesize_neuron_external_diameter(tmpdir):
    _run_example("examples/synthesize_neuron_external_diameter.py", tmpdir, DATA)
    assert sorted([i.relto(tmpdir) for i in tmpdir.listdir()]) == [
        "generated_cell.asc",
        "generated_cell.h5",
        "generated_cell.swc",
    ]


def test_synthesize_neuron_with_diameters(tmpdir):
    _run_example("examples/synthesize_neuron_with_diameters.py", tmpdir, DATA)
    assert sorted([i.relto(tmpdir) for i in tmpdir.listdir()]) == [
        "generated_cell.asc",
        "generated_cell.h5",
        "generated_cell.swc",
    ]


def test_synthesize_neurons(tmpdir):
    _run_example("examples/synthesize_neurons.py", tmpdir, DATA)
    assert sorted([i.relto(tmpdir) for i in tmpdir.listdir()]) == [
        f"generated_cell_{i}.swc" for i in range(10)
    ]


def test_synthesize_single_neuron(tmpdir):
    _run_example("examples/synthesize_single_neuron.py", tmpdir, DATA)
    assert sorted([i.relto(tmpdir) for i in tmpdir.listdir()]) == [
        "generated_cell.asc",
        "generated_cell.h5",
        "generated_cell.swc",
    ]
