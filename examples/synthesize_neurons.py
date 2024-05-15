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
Synthesize a population of neurons with the same parameters
===========================================================

This example shows how to synthesize a population of cells with the same parameters for all of them.
"""

from pathlib import Path

import numpy as np

import neurots


def run(output_dir, data_dir):
    """Run the example for generating a population of cells with the same parameters."""
    num_cells = 10

    # Generate any number of cells, based on the same input
    for i in np.arange(num_cells):
        # Initialize a neuron
        N = neurots.NeuronGrower(
            input_distributions=data_dir / "bio_distr.json",
            input_parameters=data_dir / "bio_params.json",
        )

        # Grow the neuron
        neuron = N.grow()

        # Export the synthesized cell
        neuron.write(output_dir / f"generated_cell_{i}.swc")


if __name__ == "__main__":
    result_dir = Path("results_neurons")
    result_dir.mkdir(parents=True, exist_ok=True)

    run(result_dir, Path("data"))
