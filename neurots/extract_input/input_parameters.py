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


def _sort_neurite_types(neurite_types):
    """Sort neurite types to comply with internal requirements.

    For now, only apical should be first, so it is placed first, and other neurite_types can be
    placed with respect to it.
    """
    if "apical" in neurite_types:
        return list(["apical"] + [t for t in neurite_types if t != "apical"])
    return list(neurite_types)


def parameters(
    origin=(0.0, 0.0, 0.0),
    method="tmd",
    neurite_types=("basal", "apical", "axon"),
    feature="path_distances",
    diameter_parameters=None,
    trunk_method="simple",
):
    """Return a default set of input parameters to be used as input for synthesis.

    Args:
        origin (list[float]): The origin point.
        method (str): The method to use.
        neurite_types (list[str]): The neurite types to consider.
        feature (str): Use the specified TMD feature.
        diameter_parameters (dict or str): The parameters used for the diameters.
        trunk_method (str): 'simple' for simple trunk method, or '3d_angles'

    Returns:
        dict: The parameters.
    """
    if method not in ("trunk", "tmd", "tmd_gradient", "tmd_apical"):
        raise KeyError(f"Method {method} not recognized!.")
    if trunk_method not in ("simple", "3d_angles"):
        raise KeyError(f"trunk_method {trunk_method} not understood")

    base_params = {
        "randomness": 0.24,
        "targeting": 0.14,
        "radius": 0.3,
        "orientation": None
        if trunk_method == "simple"
        else {"mode": "apical_constraint", "values": None},
        "growth_method": method,
        "branching_method": "random" if method == "trunk" else "bio_oriented",
        "modify": None,
        "step_size": {"norm": {"mean": 1.0, "std": 0.2}},
        "metric": feature,
    }

    input_parameters = {
        "axon": {**base_params, "tree_type": 2},
        "basal": {**base_params, "tree_type": 3},
        "apical": {**base_params, "tree_type": 4},
        "origin": list(origin),
        "grow_types": neurite_types
        if trunk_method == "simple"
        else _sort_neurite_types(neurite_types),
    }

    input_parameters["axon"].update(
        {
            "branching_method": "directional",
            "orientation": [[0.0, 1.0, 0.0]]
            if trunk_method == "simple"
            else {"mode": "use_predefined", "values": {"orientations": [[0.0, 1.0, 0.0]]}},
        }
    )

    input_parameters["apical"].update(
        {
            "branching_method": "directional",
            "growth_method": "tmd_apical" if method == "tmd" else None,
            "orientation": [[0.0, 1.0, 0.0]]
            if trunk_method == "simple"
            else {"mode": "use_predefined", "values": {"orientations": [[0.0, 1.0, 0.0]]}},
        }
    )

    input_parameters["diameter_params"] = {}
    if diameter_parameters is None:
        input_parameters["diameter_params"]["method"] = "default"
    elif isinstance(diameter_parameters, str):
        input_parameters["diameter_params"]["method"] = diameter_parameters
    elif isinstance(diameter_parameters, dict):
        input_parameters["diameter_params"] = diameter_parameters
        input_parameters["diameter_params"]["method"] = "external"
    else:
        raise ValueError(f"Diameter params not understood, {diameter_parameters}")

    return input_parameters
