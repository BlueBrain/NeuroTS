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
Synthesize a single neuron
==========================

This example shows how to synthesize a single cell with simple parameters.
"""

import numpy as np
from pathlib import Path
import json

import neurots


def run(output_dir, data_dir):
    """Run the example for generating a single cell."""
    np.random.seed(42)
    params = json.load(open(data_dir / "bio_params.json"))
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
        context={"y_direction": [0.0, 1.0, 0.0]},
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
    from morph_tool.transform import rotate

    rotate(neuron, [[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    neuron.write(output_dir / "generated_cell_x_rot.asc")


if __name__ == "__main__":
    result_dir = Path("results_single_neuron")
    result_dir.mkdir(parents=True, exist_ok=True)

    run(result_dir, Path("data"))
