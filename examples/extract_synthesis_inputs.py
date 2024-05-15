# noqa

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

"""
Extract inputs for synthesis
============================

This example shows how to extract the inputs required for synthesis from a set of existing
morphologies.
"""

import json
from pathlib import Path

import neurots
from neurots import extract_input


def run(output_dir, data_dir):
    """Run the example for extracting inputs for synthesis."""
    # Generate distribution from directory of neurons
    distr = extract_input.distributions(
        data_dir / "neurons", feature="path_distances", diameter_model="default"
    )

    # Save distributions in a json file
    with open(output_dir / "test_distr.json", "w", encoding="utf-8") as f:
        json.dump(distr, f, sort_keys=True, indent=2)

    # Generate default parameters for topological synthesis of basal dendrites
    params = extract_input.parameters(
        neurite_types=["basal_dendrite"], feature="path_distances", method="tmd"
    )

    # Save parameters in a json file
    with open(output_dir / "test_params.json", "w", encoding="utf-8") as f:
        json.dump(params, f, sort_keys=True, indent=2)

    # Re-load data from saved distributions
    with open(output_dir / "test_distr.json", "r", encoding="utf-8") as F:
        distr = json.load(F)

    # Re-load data from saved parameters
    with open(output_dir / "test_params.json", "r", encoding="utf-8") as F:
        params = json.load(F)

    # Initialize a neuron
    N = neurots.NeuronGrower(input_distributions=distr, input_parameters=params)

    # Grow the neuron
    neuron = N.grow()

    # Export the synthesized cell
    neuron.write(output_dir / "generated_cell.asc")
    neuron.write(output_dir / "generated_cell.swc")
    neuron.write(output_dir / "generated_cell.h5")


if __name__ == "__main__":
    result_dir = Path("results_extract_synthesis_inputs")
    result_dir.mkdir(parents=True, exist_ok=True)

    run(result_dir, Path("data"))
