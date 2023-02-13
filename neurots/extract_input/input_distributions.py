"""Input distributions."""

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

import logging

import tmd
from diameter_synthesis.build_models import build as build_diameter_models
from neurom import NeuriteType
from neurom import load_morphologies

from neurots.extract_input import from_diameter
from neurots.extract_input.from_neurom import number_neurites
from neurots.extract_input.from_neurom import soma_data
from neurots.extract_input.from_neurom import trunk_neurite
from neurots.extract_input.from_TMD import persistent_homology_angles
from neurots.utils import format_values
from neurots.utils import neurite_type_warning

L = logging.getLogger(__name__)


def _append_dicts(*args):
    """Merge all dicts into the first one."""
    ret = args[0]
    for other_dict in args[1:]:
        ret.update(other_dict)
    return ret


def distributions(
    filepath,
    neurite_types=None,
    threshold_sec=2,
    diameter_input_morph=None,
    feature="path_distances",
    diameter_model=None,
):
    """Extracts the input distributions from an input population.

    The population is defined by a directory of swc or h5 files.

    Args:
        filepath (str): the morphology file.
        neurite_types (list[str]): the neurite types to consider.
        threshold_sec (int): defines the minimum accepted number of terminations.
        diameter_input_morph (str): if input set of morphologies is provided it will be used for the
            generation of diameter model, if no input is provided no diameter model will be
            generated.
        feature (str): defines the TMD feature that will be used to extract the persistence barcode
            (can be `radial_distances`, `path_distances` or `trunk_length`). It is also possible to
            define one different feature per neurite type using a dict like
            ``{<neurite type 1>: <feature 1>, ...}``.
        diameter_model (str): model for diameters, internal models are `M1`, `M2`, `M3`, `M4` and
            `M5`. Can be set to `external` for external model.

    Returns:
        dict: The input distributions.
    """
    if neurite_types is None:
        neurite_types = ["basal_dendrite", "apical_dendrite", "axon"]

    for i, neurite_type in enumerate(neurite_types):
        if neurite_type in ("basal", "apical"):
            neurite_type_warning(neurite_type)
            neurite_types[i] = neurite_type + "_dendrite"

    pop_tmd = tmd.io.load_population(filepath, use_morphio=True)
    pop_nm = load_morphologies(filepath)

    input_distributions = {"soma": {}, "basal_dendrite": {}, "apical_dendrite": {}, "axon": {}}
    input_distributions["soma"] = soma_data(pop_nm)

    if diameter_input_morph is None:
        diameter_input_morph = filepath
    morphology = load_morphologies(diameter_input_morph)
    if isinstance(diameter_model, str) and diameter_model.startswith("M"):
        input_distributions["diameter"] = from_diameter.model(morphology)
        input_distributions["diameter"]["method"] = diameter_model

    elif hasattr(diameter_model, "__call__"):
        input_distributions["diameter"] = diameter_model(morphology)
        input_distributions["diameter"]["method"] = "external"
    elif (
        isinstance(diameter_model, str) and diameter_model == "default"
    ) or diameter_model is None:
        input_distributions["diameter"] = {}
        input_distributions["diameter"]["method"] = "default"
        input_distributions["diameter"]["diameter"] = build_diameter_models(
            morphology, config={"models": ["simpler"], "neurite_types": neurite_types}
        )
    else:
        raise NotImplementedError(f"Diameter model {diameter_model} not understood")

    for neurite_type in neurite_types:
        if isinstance(feature, str):
            type_feature = feature
        else:
            type_feature = feature.get(neurite_type, "path_distances")
        nm_type = getattr(NeuriteType, neurite_type)

        input_distributions[neurite_type] = _append_dicts(
            trunk_neurite(pop_nm, nm_type), number_neurites(pop_nm, nm_type)
        )
        if type_feature in ["path_distances", "radial_distances"]:
            _append_dicts(
                input_distributions[neurite_type],
                persistent_homology_angles(
                    pop_tmd,
                    threshold=threshold_sec,
                    neurite_type=neurite_type,
                    feature=type_feature,
                ),
                {"filtration_metric": type_feature},
            )
    return format_values(input_distributions)
