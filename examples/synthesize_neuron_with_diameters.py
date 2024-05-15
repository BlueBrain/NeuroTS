# noqa

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
