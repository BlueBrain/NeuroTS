"""Extracts the distributions associated with TMD module."""

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
