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

import numpy as np
import json
import neurots
from neurots import extract_input


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if type(obj) is np.float32:
            return np.float64(obj)
        return json.JSONEncoder.default(self, obj)


def run():

    # Generate distribution from directory of neurons
    distr = extract_input.distributions(
        "data/neurons/", feature="path_distances", diameter_model="default")

    # Save distributions in a json file
    with open("./test_distr.json", "w") as f: json.dump(distr, f, sort_keys=True, indent=2, cls=NumpyEncoder)

    # Generate defaukt parameters for topological synthesis of basal dendrites
    params = extract_input.parameters(
        neurite_types=["basal"], feature="path_distances", method="tmd")

    # Save parameters in a json file
    with open("./test_params.json", "w") as f: json.dump(params, f, sort_keys=True, indent=2)


    # Re-load data from saved files
    with open("test_distr.json", "r") as F:
        distr = json.load(F)
    # Load default parameters dictionary
    with open("test_params.json", "r") as F:
        params = json.load(F)

    # Initialize a neuron
    N = neurots.NeuronGrower(input_distributions=distr,
                         input_parameters=params)

    # Grow your neuron
    neuron = N.grow()

    neuron.write('generated_cell.asc')
    neuron.write('generated_cell.swc')
    neuron.write('generated_cell.h5')

run()
