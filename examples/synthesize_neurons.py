# noqa
"""
Synthesize a population of neurons with the same parameters
===========================================================

This example shows how to synthesize a population of cells with the same parameters for all of them.
"""

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

import json
from pathlib import Path

import numpy as np

import neurots


def run(output_dir="results_neurons", data_dir="data"):
    """Run the example for generating a population of cells with the same parameters."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = Path(data_dir)

    # Load default distributions dictionary
    with open(data_dir / "bio_distr.json", "r", encoding="utf-8") as F:
        distr = json.load(F)
    # Load default parameters dictionary
    with open(data_dir / "bio_params.json", "r", encoding="utf-8") as F:
        params = json.load(F)

    num_cells = 10

    # Generate any number of cells, based on the same input
    for i in np.arange(num_cells):
        # Initialize a neuron
        N = neurots.NeuronGrower(input_distributions=distr, input_parameters=params)
        # Grow your neuron
        neuron = N.grow()
        # Export the synthesized cell
        neuron.write(output_dir / f"generated_cell_{i}.swc")


if __name__ == "__main__":
    run()
