"""Test the examples."""

# Copyright (C) 2022  Blue Brain Project, EPFL
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
