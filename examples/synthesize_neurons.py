# noqa

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

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
