"""Extracts the distributions associated with TMD module."""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

import tmd

from neurots.utils import NeuroTSError


def persistent_homology_angles(
    pop, threshold=2, neurite_type="basal_dendrite", feature="radial_distances"
):
    """Add the persistent homology extracted from a population of apicals to the distr dictionary.

    Each tree in the population is associated with a persistence barcode (diagram)
    and a set of angles that will be used as input for synthesis.

    Args:
        pop (neurom.core.population.Population): The given population.
        threshold (int): The minimum number of terminations.
        neurite_type (neurom.core.types.NeuriteType): Consider only the neurites of this type.
        feature (str): Use the specified TMD feature.
    """
    ph_ang = [
        tmd.methods.get_ph_angles(tree, feature=feature) for tree in getattr(pop, neurite_type)
    ]
    if not ph_ang:
        raise NeuroTSError(f"The given population does contain any tree of {neurite_type} type.")

    # Keep only the trees whose number of terminations is above the threshold
    # Saves the list of persistence diagrams for the selected neurite_type
    phs = [p for p in ph_ang if len(p) > threshold]
    if not phs:
        raise NeuroTSError(
            "The given threshold excluded all bars of the persistence diagram, please use a "
            "lower threshold value."
        )
    min_bar_length = min(min(tmd.analysis.get_lengths(ph)) for ph in phs)

    return {"persistence_diagram": phs, "min_bar_length": min_bar_length}
