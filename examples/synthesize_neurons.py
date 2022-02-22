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
import numpy as np
import neurots
from neurots import extract_input

def run():
    # Load default distributions dictionary
    with open("data/bio_distr.json", "r") as F:
        distr = json.load(F)
    # Load default parameters dictionary
    with open("data/bio_params.json", "r") as F:
        params = json.load(F)

    os.mkdir('Synthesized_cells')
    num_cells = 10

    # Generate any number of cells, based on the same input
    for i in np.arange(num_cells):
        # Initialize a neuron
        N = neurots.NeuronGrower(input_distributions=distr,
                             input_parameters=params)
        # Grow your neuron
        neuron = N.grow()
        neuron.write('Synthesized_cells/generated_cell_'+str(i)+'.swc')


run()
