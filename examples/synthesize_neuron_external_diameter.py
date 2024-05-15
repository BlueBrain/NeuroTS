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
