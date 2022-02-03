"""Extracts the distributions associated with NeuroM module."""

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

import neurom as nm
import numpy as np
from neurom import stats


def transform_distr(opt_distr):
    """Transform distributions.

    Args:
        opt_distr (neurom.stats.FitResults): The fitted distribution.

    Returns:
        dict: A dictionary whose structure depends on the type of distribution:

        * if `type == "norm"`:

        .. code-block:: bash

            {
                "norm": {
                    "mean": <mean value>,
                    "std": <std value>
                }
            }

        * if `type == "uniform"`:

        .. code-block:: bash

            {
                "uniform": {
                    "min": <min value>,
                    "max": <max value>
                }
            }

        * if `type == "expon"`:

        .. code-block:: bash

            {
                "expon": {
                    "loc": <loc value>,
                    "lambda": <lambda value>
                }
            }
    """
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
    """Extract soma size.

    Args:
        pop (neurom.core.population.Population): The given population.

    Returns:
        dict: A dictionary with the following structure:

        .. code-block:: bash

            {
                "size": <the soma size>
            }
    """
    # Extract soma size as a normal distribution
    # Returns a dictionary with the soma information
    soma_size = nm.get("soma_radius", pop)
    ss = stats.fit(soma_size, distribution="norm")

    return {"size": transform_distr(ss)}


def trunk_neurite(pop, neurite_type=nm.BASAL_DENDRITE, bins=30):
    """Extract the trunk data for a specific tree type.

    Args:
        pop (neurom.core.population.Population): The given population.
        neurite_type (neurom.core.types.NeuriteType): Consider only the neurites of this type.
        bins (int or list[int] or str, optional): The bins to use (this pararmeter is passed to
            :func:`numpy.histogram`).

    Returns:
        dict: A dictionary with the following structure:

        .. code-block:: bash

            {
                "trunk": {
                    "orientation_deviation": {
                        "data": {
                            "bins": <bin values>,
                            "weights": <weights>
                        }
                    },
                    "azimuth": {
                        "inuform": {
                            "min": <min value>,
                            "max": <max value>
                        }
                    },
                    "absolute_elevation_deviation": {
                        "data": {
                            "bins": <bin values>,
                            "weights": <weights>
                        }
                    }
                }
            }
    """
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
                "data": {"bins": actual_angle_bins.tolist(), "weights": angle_heights.tolist()}
            },
            "azimuth": {"uniform": {"min": np.pi, "max": 0.0}},
            "absolute_elevation_deviation": {
                "data": {
                    "bins": actual_elevation_bins.tolist(),
                    "weights": elevation_heights.tolist(),
                }
            },
        }
    }


def number_neurites(pop, neurite_type=nm.BASAL_DENDRITE):
    """Extract the number of trees for a specific tree type from a given population.

    Args:
        pop (neurom.core.population.Population): The given population.
        neurite_type (neurom.core.types.NeuriteType): Consider only the neurites of this type.

    Returns:
        dict: A dictionary with the following structure:

        .. code-block:: bash

            {
                "num_trees": {
                    "data": {
                        "bins": <bin values>,
                        "weights": <weights>
                    }
                }
            }
    """
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
    return {"num_trees": {"data": {"bins": bins[:-1].tolist(), "weights": heights.tolist()}}}
