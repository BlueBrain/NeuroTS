"""Generate a cell with external diametrizer.

The ``diameter-synthesis`` package must be installed.
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

from diameter_synthesis import build_diameters  # pylint: disable=import-error

import neurots


def run(output_dir="results_neuron_external_diameter", data_dir="data"):
    """Run the example for generating a cell with external diametrizer."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = Path(data_dir)

    # An external diametrizer should have the signature described in
    # ``neurots.generate.diametrizer.build``.
    # The code ``diameter_synthesis`` provides an example of such external diametrizer.
    external_diametrizer = build_diameters.build

    # Load distributions from cells in input directory
    with open(data_dir / "IN_distr.json", "r", encoding="utf-8") as F:
        distr = json.load(F)
    # Load default parameters dictionary
    with open(data_dir / "IN_params.json", "r", encoding="utf-8") as F:
        params = json.load(F)

    # Initialize a neuron
    N = neurots.NeuronGrower(
        input_distributions=distr,
        input_parameters=params,
        external_diametrizer=external_diametrizer,
    )

    # Grow your neuron
    neuron = N.grow()

    # Export the synthesized cell
    neuron.write(output_dir / "generated_cell.asc")
    neuron.write(output_dir / "generated_cell.swc")
    neuron.write(output_dir / "generated_cell.h5")


if __name__ == "__main__":
    run()
