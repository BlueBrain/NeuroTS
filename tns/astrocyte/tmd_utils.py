""" Barcode utils
"""
import logging
import numpy as np
from tmd.Topology.transformations import tmd_scale
from tmd.Topology.statistics import get_lengths


L = logging.getLogger(__name__)


def scale_barcode(ph, target_distance):
    """ Given a target distance, scale the persistence homology
    in order to make sure that the neurite will reach the target
    """
    ph_distance = np.nanmax(ph)

    if target_distance > ph_distance:
        ph = tmd_scale(ph, target_distance / ph_distance)

    return ph


def barcodes_greater_than_distance(ph_list, target_extent):
    """ Returns all barcodes the max value of which is greater than target_extent
    """
    max_extents = np.asarray([max(get_lengths(ph)) for ph in ph_list])
    mask = (max_extents > target_extent) | np.isclose(max_extents, target_extent)

    if not mask.any():
        L.warning('All barcodes are smaller than target. The longest is returned.')
        return [ph_list[np.argmax(max_extents)]]

    return [ph_list[index] for index in np.where(mask)[0]]
