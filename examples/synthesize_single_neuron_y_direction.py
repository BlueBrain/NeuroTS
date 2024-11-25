# noqa

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

"""
Synthesize a single neuron with global direction
================================================

This example shows how to synthesize a single cell with different y directions
"""

import json
from pathlib import Path

import numpy as np
from morph_tool.transform import rotate

import neurots


def run(output_dir, data_dir):
    """Run the example for generating a single cell."""
    np.random.seed(42)
    with open(data_dir / "bio_params.json", encoding="utf-8") as p_file:
        params = json.load(p_file)
    # use trunk angle with y_direction awareness
    params["basal_dendrite"]["orientation"] = {
        "mode": "pia_constraint",
        "values": {"form": "step", "params": [1.5, 0.25]},
    }
    params["apical_dendrite"]["orientation"] = {
        "mode": "normal_pia_constraint",
        "values": {"direction": {"mean": [0.0], "std": [0.0]}},
    }

    # Initialize a neuron
    N = neurots.NeuronGrower(
        input_distributions=data_dir / "bio_distr.json",
        input_parameters=params,
    )

    # Grow the neuron
    neuron = N.grow()

    # Export the synthesized cell
    neuron.write(output_dir / "generated_cell_orig.asc")

    np.random.seed(42)

    # Initialize a neuron
    N = neurots.NeuronGrower(
        input_distributions=data_dir / "bio_distr.json",
        input_parameters=params,
        # context={"y_direction": [0.0, 1.0, 0.0]},
    )

    # Grow the neuron
    neuron = N.grow()

    # Export the synthesized cell
    neuron.write(output_dir / "generated_cell_y.asc")

    np.random.seed(42)

    # Initialize a neuron
    N = neurots.NeuronGrower(
        input_distributions=data_dir / "bio_distr.json",
        input_parameters=params,
        context={"y_direction": [1.0, 0.0, 0.0]},
    )

    # Grow the neuron
    neuron = N.grow()

    # Export the synthesized cell
    neuron.write(output_dir / "generated_cell_x.asc")

    # the rotated neuron should be the same as original one

    rotate(neuron, [[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    neuron.write(output_dir / "generated_cell_x_rot.asc")


if __name__ == "__main__":
    result_dir = Path("results_single_neuron")
    result_dir.mkdir(parents=True, exist_ok=True)

    run(result_dir, Path("data"))
