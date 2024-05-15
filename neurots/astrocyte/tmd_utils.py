"""Barcode utils."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import numpy as np
from tmd.Topology.statistics import get_lengths
from tmd.Topology.transformations import tmd_scale

L = logging.getLogger(__name__)


def scale_barcode(ph, target_distance):
    """Scale a persistence homology from a given target distance.

    Given a target distance, scale the persistence homology in order to make sure that the neurite
    will reach the target.

    Args:
        ph (list[list]): The persistence homology.
        target_distance (float): The target distance.

    Returns:
        list[list]: The rescaled persistence homology.
    """
    ph_distance = np.nanmax(ph)

    if target_distance > ph_distance:
        ph = tmd_scale(ph, target_distance / ph_distance)

    return ph


def barcodes_greater_than_distance(ph_list, target_extent):
    """Returns all barcodes the max value of which is greater than target_extent.

    Args:
        ph_list (list[list[list]]): A list of persistence homologies.
        target_extent (float): The target barcode extent.

    Returns:
        list[list[list]]: The list of the selected barcodes.
    """
    max_extents = np.asarray([max(get_lengths(ph)) for ph in ph_list])
    mask = (max_extents > target_extent) | np.isclose(max_extents, target_extent)

    if not mask.any():
        L.warning("All barcodes are smaller than target. The longest is returned.")
        return [ph_list[np.argmax(max_extents)]]

    return [ph_list[index] for index in np.where(mask)[0]]
