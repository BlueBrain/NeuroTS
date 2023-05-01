"""NeuroTS utils used by multiple tools."""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

import warnings
from copy import deepcopy

import numpy as np
from neurom import COLS

PIA_DIRECTION = [0.0, 1.0, 0.0]


class NeuroTSError(Exception):
    """Raises NeuroTS error."""


def format_values(obj, decimals=None):
    """Format values of an object recursively."""
    if isinstance(obj, np.ndarray):
        obj = obj.tolist()
    elif isinstance(obj, np.floating):
        obj = float(obj)
        if decimals is not None:
            obj = round(obj, ndigits=decimals)
    elif isinstance(obj, np.integer):
        obj = int(obj)
    elif isinstance(obj, np.bool_):
        obj = bool(obj)
    elif isinstance(obj, dict):
        obj = {k: format_values(v, decimals=decimals) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        obj = type(obj)([format_values(i, decimals=decimals) for i in obj])
    return obj


def neurite_type_warning(key):
    """Print a deprecation warning for old neurite_type key."""
    warnings.warn(
        f"The '{key}' property is deprecated, please use '{key}_dendrite' instead",
        DeprecationWarning,
    )


def convert_from_legacy_neurite_type(data):
    """Convert legacy neurite type names, basal -> basal_dendrite and apical -> apical_dendrite."""
    old_data = deepcopy(data)
    for key, _data in old_data.items():
        if key == "apical":
            neurite_type_warning(key)
            data["apical_dendrite"] = data.pop("apical")
            key = "apical_dendrite"
        if key == "basal":
            neurite_type_warning(key)
            data["basal_dendrite"] = data.pop("basal")
            key = "basal_dendrite"

        if isinstance(_data, dict):
            data[key] = convert_from_legacy_neurite_type(data[key])

        if isinstance(_data, list):
            for i, d in enumerate(_data):
                if d == "apical":
                    neurite_type_warning(key)
                    data[key][i] = "apical_dendrite"
                if d == "basal":
                    neurite_type_warning(key)
                    data[key][i] = "basal_dendrite"

    return data


def point_to_section_segment(neuron, point, rtol=1e-05, atol=1e-08):
    """Find section and segment that matches the point (also in morph_tool.spatial).

    Only the first point found with the *exact* same coordinates as the point argument is considered

    Args:
        neuron (morphio.Morphology): neuron object
        point (point): value of the point to find in the h5 file
        rtol, atol (floats): precision of np.isclose

    Returns:
        Tuple: (NeuroM/MorphIO section ID, point ID) of the point the matches the input coordinates.
        Since NeuroM v2, section ids of NeuroM and MorphIO are the same excluding soma.
    """
    for section in neuron.iter():
        points = section.points
        offset = np.where(
            np.isclose(points[:, COLS.XYZ], point[COLS.XYZ], rtol=rtol, atol=atol).all(axis=1)
        )
        if offset[0].size:
            return section.id, offset[0][0]

    raise ValueError(f"Cannot find point in morphology that matches: {point}")


def accept_reject(propose, prob, rng, null=None, max_tries=100, noise_increase=0.5):
    """Generic accept reject algorithm."""
    n_try = 0
    while n_try < max_tries:
        proposal = propose(n_try * noise_increase)
        _prob = prob(proposal)

        if _prob == 1.0:
            # this ensures we don't change rng for the tests, but its not really needed
            return proposal

        if rng.binomial(1, _prob):
            return proposal
        n_try += 1
    warnings.warn(
        "We could not sample from distribution, so we take a random point. "
        "Consider checking the given probability distribution."
    )
    if null is not None:
        return null()
    return proposal
