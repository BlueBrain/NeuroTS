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


def accept_reject(
    propose,
    probability,
    rng,
    default_propose=None,
    max_tries=100,
    randomness_increase=0.5,
    **probability_kwargs,
):
    """Generic accept/reject algorithm.

    Args:
        propose (callable): function to propose a move, which has an 'noise' argument to allow
            for increasing randomness and faster acceptance (to allow sharp turns, etc...)
        probability (callable): function to compute probability, first arg is the poposal (output of
            `propose` function), and takes extra kwargs via `probability_kwargs`
        rng (np.random._generator.Generator): random number generator
        default_propose (callable): function to use if we cannot accept a proposal,
            if None, propose is used
        max_tries (int): maximum number of tries to accept before `default_propose` is called
        randomness_increase (float): increase of noise amplitude after each try
        probability_kwargs (dict): parameters for `probability` function

    """
    n_tries = 0
    while n_tries < max_tries:
        proposal = propose(n_tries * randomness_increase)
        _prob = probability(proposal, **probability_kwargs)
        if _prob == 1.0:
            # this ensures we don't change rng for the tests, but its not really needed
            return proposal

        if rng.binomial(1, _prob):
            return proposal
        n_tries += 1
    warnings.warn(
        "We could not sample from distribution, we take a random point unless a 'default_propose' "
        "function is provided. Consider checking the given probability distribution."
    )
    if default_propose is not None:
        return default_propose()
    return proposal
