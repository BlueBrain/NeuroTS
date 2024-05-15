# noqa

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

"""
Synthesize a single neuron
==========================

This example shows how to synthesize a single cell with simple parameters.
"""

from pathlib import Path

import neurots


def run(output_dir, data_dir):
    """Run the example for generating a single cell."""
    # Initialize a neuron
    N = neurots.NeuronGrower(
        input_distributions=data_dir / "bio_distr.json",
        input_parameters=data_dir / "bio_params.json",
    )

    # Grow the neuron
    neuron = N.grow()

    # Export the synthesized cell
    neuron.write(output_dir / "generated_cell.asc")
    neuron.write(output_dir / "generated_cell.swc")
    neuron.write(output_dir / "generated_cell.h5")


if __name__ == "__main__":
    result_dir = Path("results_single_neuron")
    result_dir.mkdir(parents=True, exist_ok=True)

    run(result_dir, Path("data"))
