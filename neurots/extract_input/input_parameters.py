"""Input parameters functions."""

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

from neurots.utils import neurite_type_warning

tmd_algos = ("tmd", "tmd_gradient", "tmd_apical")


def parameters(
    origin=(0.0, 0.0, 0.0),
    method="tmd",
    neurite_types=None,
    feature="path_distances",
    diameter_parameters=None,
):  # pylint: disable=too-many-branches
    """Returns a default set of input parameters to be used as input for synthesis.

    Args:
        origin (list[float]): The origin point.
        method (str): The method to use.
        neurite_types (list[str]): The neurite types to consider.
        feature (str): Use the specified TMD feature.
        diameter_parameters (dict or str): The parameters used for the diameters.

    Returns:
        dict: The parameters.
    """
    if neurite_types is None:
        neurite_types = ["basal_dendrite", "apical_dendrite", "axon"]

    for i, neurite_type in enumerate(neurite_types):
        if neurite_type in ("basal", "apical"):
            neurite_type_warning(neurite_type)
            neurite_types[i] = neurite_type + "_dendrite"

    input_parameters = {
        "basal_dendrite": {},
        "apical_dendrite": {},
        "axon": {},
        "origin": list(origin),
        "grow_types": neurite_types,
    }

    def merged_params(data):
        """Use input method to set branching."""
        ret = {}
        if method == "trunk":
            branching = "random"
        elif method in tmd_algos:
            branching = "bio_oriented"
        else:
            raise KeyError(f"Method not recognized! Please select from: {tmd_algos}.")

        ret.update(
            {
                "randomness": 0.24,
                "targeting": 0.14,
                "radius": 0.3,
                "orientation": None,
                "growth_method": method,
                "branching_method": branching,
                "modify": None,
                "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
                "metric": feature,
            }
        )
        ret.update(data)
        return ret

    if "axon" in neurite_types:
        input_parameters["axon"] = merged_params(
            {
                "tree_type": 2,
                "orientation": [[0.0, -1.0, 0.0]],
            }
        )

    if "basal_dendrite" in neurite_types:
        input_parameters["basal_dendrite"] = merged_params({"tree_type": 3})

    if "apical_dendrite" in neurite_types:
        input_parameters["apical_dendrite"] = merged_params(
            {
                "tree_type": 4,
                "branching_method": "directional",
                "orientation": [[0.0, 1.0, 0.0]],
            }
        )
        if method == "tmd":
            input_parameters["apical_dendrite"]["growth_method"] = "tmd_apical"

    input_parameters["diameter_params"] = {}
    if diameter_parameters is None:
        input_parameters["diameter_params"]["method"] = "default"
        input_parameters["diameter_params"]["models"] = ["simpler"]
    elif isinstance(diameter_parameters, str):
        input_parameters["diameter_params"]["method"] = diameter_parameters
    elif isinstance(diameter_parameters, dict):
        input_parameters["diameter_params"] = diameter_parameters
        input_parameters["diameter_params"]["method"] = "external"
    else:
        raise ValueError(f"Diameter params not understood, {diameter_parameters}")

    return input_parameters
