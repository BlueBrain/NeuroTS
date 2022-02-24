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
Synthesize a cell with external diametrizer
===========================================

This example shows how to synthesize a cell with an external diametrizer.
An external diametrizer should have the signature described in
``neurots.generate.diametrizer.build``.

The code ``diameter_synthesis`` provides an example of such external diametrizer.

.. warning::

    Note that the ``diameter-synthesis`` package must be installed.
"""

from pathlib import Path

from diameter_synthesis import build_diameters  # pylint: disable=import-error

import neurots


def run(output_dir, data_dir):
    """Run the example for generating a cell with external diametrizer."""
    # Initialize a neuron with an external diametrizer
    N = neurots.NeuronGrower(
        input_distributions=data_dir / "IN_distr.json",
        input_parameters=data_dir / "IN_params.json",
        external_diametrizer=build_diameters.build,
    )

    # Grow the neuron
    neuron = N.grow()

    # Export the synthesized cell
    neuron.write(output_dir / "generated_cell.asc")
    neuron.write(output_dir / "generated_cell.swc")
    neuron.write(output_dir / "generated_cell.h5")


if __name__ == "__main__":
    result_dir = Path("results_neuron_external_diameter")
    result_dir.mkdir(parents=True, exist_ok=True)

    run(result_dir, Path("data"))
