"""Input parameters functions."""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

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
    if isinstance(diameter_parameters, str):
        input_parameters["diameter_params"]["method"] = diameter_parameters
    elif diameter_parameters is None or (
        isinstance(diameter_parameters, dict)
        and list(diameter_parameters.keys()) == ["neurite_types"]
    ):
        input_parameters["diameter_params"]["method"] = "default"
        input_parameters["diameter_params"]["models"] = ["simpler"]
        if diameter_parameters is not None:
            input_parameters["diameter_params"]["neurite_types"] = diameter_parameters[
                "neurite_types"
            ]
    elif isinstance(diameter_parameters, dict) and list(diameter_parameters.keys()) != [
        "neurite_types"
    ]:
        input_parameters["diameter_params"] = diameter_parameters
        input_parameters["diameter_params"]["method"] = "external"
    else:
        raise ValueError(f"Diameter params not understood, {diameter_parameters}")

    return input_parameters
