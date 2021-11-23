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
import neurots


def run():
    # Cell to use as input for the diameter model
    dir_path = os.path.dirname(os.path.realpath(__file__))
    input_cell = os.path.join(dir_path, '../test_data/bio/C220197A-P2.h5')

    # Outputcell to be saved
    output_cell_name = os.path.join(dir_path, './local/Neuron_diam')

    # Generate model from input cell

    model = neurots.extract_input.diameter_distributions(input_cell)

    # Create the object to modify the input cell to be diametrized
    # Initialize tha cell with the output cell name
    G = neurots.NeuronGrower(input_parameters=None, input_distributions=model, name=output_cell_name)

    # Modify the diameters using the generated model
    G.diametrize()

    G.neuron.write_asc('fixed_diameters.asc')


run()
