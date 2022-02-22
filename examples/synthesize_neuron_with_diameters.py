"""Fix diameters."""

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

def run():
    # Extract distributions with diameters
    distr = extract_input.distributions(
            "data/neurons/", feature="path_distances",
            diameter_model="M5")

    # Load default parameters dictionary
    with open("data/bio_params.json", "r") as F:
        params = json.load(F)
    params["diameter_params"]["method"] = "M5"

    # Initialize a neuron
    N = neurots.NeuronGrower(input_distributions=distr,
                         input_parameters=params)

    # Grow your neuron
    neuron = N.grow()
    # Correct the diameters
    N._diametrize()

    neuron.write('generated_cell.asc')
    neuron.write('generated_cell.swc')
    neuron.write('generated_cell.h5')

run()
