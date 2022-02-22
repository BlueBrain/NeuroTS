"""Generate a cell."""

# Copyright (C) 2021  Blue Brain Project, EPFL
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

import os
import json
import neurots
from neurots import extract_input
from diameter_synthesis import build_diameters

def run():

    def external_diametrizer(neuron, model, neurite_type):
        return build_diameters.build(
            neuron,
            model,
            [neurite_type],
            params["diameter_params"]
        )

    # Load distributions from cells in input directory
    with open("data/IN_distr.json", "r") as F:
        distr = json.load(F)
    # Load default parameters dictionary
    with open("data/IN_params.json", "r") as F:
        params = json.load(F)

    # Initialize a neuron
    N = neurots.NeuronGrower(input_distributions=distr,
                             input_parameters=params,
                             external_diametrizer=external_diametrizer)

    # Grow your neuron
    neuron = N.grow()

    neuron.write('generated_cell.asc')
    neuron.write('generated_cell.swc')
    neuron.write('generated_cell.h5')


run()
