# noqa

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

"""
Synthesize neuron with a simple diameter model
==============================================

This example shows how to synthesize a cell with one of the simple provided diameter models.
"""

import json
from pathlib import Path

import neurots
from neurots import extract_input


def run(output_dir, data_dir):
    """Run the example for generating a cell with a simple diameter model."""
    # Extract distributions with diameters
    distr = extract_input.distributions(
        data_dir / "neurons", feature="path_distances", diameter_model="M5"
    )

    # Load default parameters dictionary
    with open(data_dir / "bio_params.json", "r", encoding="utf-8") as F:
        params = json.load(F)

    # Set the diameter method
    params["diameter_params"]["method"] = "M5"

    # Initialize a neuron
    N = neurots.NeuronGrower(input_distributions=distr, input_parameters=params)

    # Grow the neuron
    neuron = N.grow()

    # Export the synthesized cell
    neuron.write(output_dir / "generated_cell.asc")
    neuron.write(output_dir / "generated_cell.swc")
    neuron.write(output_dir / "generated_cell.h5")


if __name__ == "__main__":
    result_dir = Path("results_neuron_with_diameters")
    result_dir.mkdir(parents=True, exist_ok=True)

    run(result_dir, Path("data"))
