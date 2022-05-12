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
import warnings

import neurom as nm
import numpy as np
from neurom import stats
from neurom.check.morphology_checks import has_apical_dendrite
from neurom.core.types import tree_type_checker as is_type
from scipy.integrate import quad
from scipy.optimize import curve_fit

from neurots.generate.orientations import prob_function


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
    params = stats.fit(soma_size, distribution="norm").params
    return {"size": {"norm": {"mean": params[0], "std": params[1]}}}


def _step_fit_prob_function(angle, scale, rate):
    """Probablity function to use for fitting angle distributions."""

    def _prob(_angle):
        return prob_function(_angle, [scale, rate], form="step") * np.sin(_angle)

    return _prob(angle) / quad(_prob, 0, np.pi)[0]


def _double_step_fit_prob_function(angle, scale_low, rate_low, scale_high, rate_high):
    """Probablity function to use for fitting angle distributions."""

    def _prob(_angle):
        return prob_function(
            _angle, [scale_low, rate_low, scale_high, rate_high], form="double_step"
        ) * np.sin(_angle)

    return _prob(angle) / quad(_prob, 0, np.pi)[0]


def get_fit_prob_function(morph_class="PC", neurite_type=nm.BASAL_DENDRITE, params=None):
    """Get probability function for trunk angles.

    Args:
        morph_class (str): morphological class (PC or IN)
        neurite_type (nm.NeuriteType): type of neurite to consider
        params (dict): if not None, can be used to overwrite the fit functions/bounds
    """
    # this is the form of the expected parameter dict.
    # The bounds correspond to the function's parameter min/max bounds for the fit
    default_params = {
        "PC": {
            "basal_dendrite": {"form": "step", "bounds": ([0.0, 0.01], [np.pi, 10])},
            "apical_dendrite": {"form": "step", "bounds": ([0.0, -10], [3.0, -0.010])},
            "axon": {"form": "step", "bounds": ([0.0, 0.01], [3.0, 10])},
        },
        "IN": {
            "basal_dendrite": {
                "form": "double_step",
                "bounds": ([-np.pi, 0.01, -np.pi, 0.01], [np.pi, 10, np.pi, 10]),
            },
            "axon": {"form": "step", "bounds": ([0.0, 0.01], [3.0, 10])},
        },
    }
    if params is not None:
        default_params.update(params)

    bound = default_params[morph_class][neurite_type.name]["bounds"]
    form = default_params[morph_class][neurite_type.name]["form"]
    function = _step_fit_prob_function if form == "step" else _double_step_fit_prob_function
    return function, bound, form


def _get_hist(data, bins=50):
    """Return density histogram with bin centers."""
    densities, bins = np.histogram(data, bins=bins, density=True)
    return 0.5 * (bins[1:] + bins[:-1]), densities


def trunk_vectors(morph, neurite_type, from_center_of_mass=True):
    """This is neurom.get('trunk_vectors') but wrt to [0, 0, 0] if from_center_of_mass=False.

    If one uses some.center (which is center of mass of soma points), it
    may not corresponds to [0, 0, 0], from which the trunk angles should be computed.
    """
    if from_center_of_mass:
        return nm.get("trunk_vectors", morph, neurite_type=neurite_type)
    return [
        nm.morphmath.vector(n.root_node.points[0], [0.0, 0.0, 0.0])
        for n in nm.iter_neurites(morph, filt=is_type(neurite_type))
    ]


def _have_apical_dendrites(pop):
    """Check if all morphologies in a population have apicals to find the population class."""
    apicals = list(has_apical_dendrite(morph).status for morph in pop.morphologies)
    if all(apicals):
        return "PC"
    if all(not a for a in apicals):
        return "IN"
    raise Exception("Population of neurons has inconsistent classes")


def _trunk_neurite(pop, neurite_type, bins, params=None):
    """Extract trunk angle data.

    Args:
        pop (neurom.core.population.Population): The given population.
        neurite_type (neurom.core.types.NeuriteType): Consider only the neurites of this type.
        bins (int or list[int] or str, optional): The bins to use (this pararmeter is passed to
            :func:`numpy.histogram`).
        params (dict): parameter to pass to fit functions to set the bounds

    Returns:
        dict: A dictionary with the following structure:

        .. code-block:: bash

            {
                "trunk": {
                    "3d_angle": {
                        "form": <form of fit function>,
                        "params": <fit params>,
                    }
                }
            }
    """
    # not yet implemented  for other neurite types
    if neurite_type not in [nm.BASAL_DENDRITE, nm.AXON]:
        return {"trunk": None}

    pop_morph_class = _have_apical_dendrites(pop)
    fit_prob_function, bounds, form = get_fit_prob_function(
        morph_class=pop_morph_class, neurite_type=neurite_type, params=params
    )
    angles = []
    for morph in pop.morphologies:
        # for PC neurons, we use apical-basal and apical-axon 3d angles, thus apical as reference
        if pop_morph_class == "PC":
            # to deal with multiple apical mtypes here, as we take first one only for now
            ref_vec = trunk_vectors(morph, neurite_type=nm.APICAL_DENDRITE)[0]

        # for IN we use pia direction as reference
        elif pop_morph_class == "IN":
            ref_vec = [0, 1, 0]

        vecs = trunk_vectors(morph, neurite_type=neurite_type)
        angles += [nm.morphmath.angle_between_vectors(ref_vec, vec) for vec in vecs]
    try:
        popt = curve_fit(fit_prob_function, *_get_hist(angles, bins=bins), bounds=bounds)[0]
    except RuntimeError:
        warnings.warn("Cannot fit some trunk angles")
        popt = None
    return {"trunk": {"3d_angle": {"form": form, "params": popt}}}


def _simple_trunk_neurite(pop, neurite_type, bins):
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


def trunk_neurite(pop, neurite_type=nm.BASAL_DENDRITE, bins=30, params=None, method="simple"):
    """Extract the trunk data for a specific tree type.

    Args:
        pop (neurom.core.population.Population): The given population.
        neurite_type (neurom.core.types.NeuriteType): Consider only the neurites of this type.
        bins (int or list[int] or str, optional): The bins to use (this pararmeter is passed to
            :func:`numpy.histogram`).
        method (str): Method to use

    Returns:
        dict: A dictionary with the trunk data.
    """
    if method == "simple":
        return _simple_trunk_neurite(pop, neurite_type=neurite_type, bins=bins)
    return _trunk_neurite(pop, neurite_type=neurite_type, bins=bins, params=params)


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
