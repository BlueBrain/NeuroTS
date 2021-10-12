"""Extracts the distributions associated with NeuroM module."""

import neurom as nm
import numpy as np
from neurom import stats


def transform_distr(opt_distr):
    """Transforms distributions."""
    if opt_distr.type == "norm":
        return {"norm": {"mean": opt_distr.params[0], "std": opt_distr.params[1]}}
    elif opt_distr.type == "uniform":
        return {
            "uniform": {
                "min": opt_distr.params[0],
                "max": opt_distr.params[1] + opt_distr.params[0],
            }
        }
    elif opt_distr.type == "expon":
        return {"expon": {"loc": opt_distr.params[0], "lambda": 1.0 / opt_distr.params[1]}}
    return None


def soma_data(pop):
    """Extract soma size."""
    # Extract soma size as a normal distribution
    # Returns a dictionary with the soma information
    soma_size = nm.get("soma_radius", pop)
    ss = stats.fit(soma_size, distribution="norm")

    return {"size": transform_distr(ss)}


def trunk_neurite(pop, neurite_type=nm.BASAL_DENDRITE, bins=30):
    """Extracts the trunk data for a specific tree type."""
    angles = [nm.get("trunk_angles", neuron, neurite_type=neurite_type) for neuron in pop]
    angles = np.concatenate(angles, axis=0)
    angle_heights, angle_bins = np.histogram(angles, bins=bins)

    # Extract trunk relative orientations to resample
    actual_angle_bins = (angle_bins[1:] + angle_bins[:-1]) / 2.0

    elevations = [
        nm.get("trunk_origin_elevations", neuron, neurite_type=neurite_type) for neuron in pop
    ]
    elevations = np.concatenate(elevations, axis=0)
    elevation_heights, elevation_bins = np.histogram(elevations, bins=bins)

    # Extract trunk absolute orientations to resample
    actual_elevation_bins = (elevation_bins[1:] + elevation_bins[:-1]) / 2.0

    return {
        "trunk": {
            "orientation_deviation": {
                "data": {"bins": actual_angle_bins, "weights": angle_heights}
            },
            "azimuth": {"uniform": {"min": np.pi, "max": 0.0}},
            "absolute_elevation_deviation": {
                "data": {
                    "bins": actual_elevation_bins,
                    "weights": elevation_heights,
                }
            },
        }
    }


def number_neurites(pop, neurite_type=nm.BASAL_DENDRITE):
    """Extracts the number of trees for a specific tree type."""
    # Extract number of neurites as a precise distribution
    # The output is given in integer numbers which are
    # the permitted values for the number of trees.
    nneurites = np.asarray(
        nm.get("number_of_neurites", pop, neurite_type=neurite_type), dtype=np.int32
    )
    # Clean the data from single basal trees cells
    if neurite_type == nm.BASAL_DENDRITE and len(np.where(nneurites == 1)[0]) > 0:
        nneurites[np.where(nneurites == 1)[0]] = 2
        print(
            "Warning, input population includes cells with single basal trees! "
            + "The distribution has been altered to include 2 basals minimum."
        )

    heights, bins = np.histogram(
        nneurites, bins=np.arange(np.min(nneurites), np.max(nneurites) + 2)
    )

    # pylint: disable=no-member
    return {"num_trees": {"data": {"bins": bins[:-1], "weights": heights}}}