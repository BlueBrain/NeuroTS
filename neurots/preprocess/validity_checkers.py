"""Functions to check that the given parameters and distributions will not break the algorithm.

The functions for validity checkers should have the signature: `check_something(params, distrs)`.
These functions should be very generic and should not depend on any context in which the related
grower is used.

The checkers should be registered to be executed in the preprocess step using the
`@register_validator` decorator if they are applied per grow_type and growth_method, or with
`@register_global_validator` if they need the entire data.
"""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

import warnings

from neurots.preprocess.exceptions import NeuroTSValidationError
from neurots.preprocess.relevance_checkers import check_min_bar_length
from neurots.preprocess.utils import register_global_validator
from neurots.preprocess.utils import register_validator
from neurots.validator import validate_neuron_distribs
from neurots.validator import validate_neuron_params


@register_validator("trunk")
def check_num_seg(params, distrs):
    """Check that params contains a 'num_seg' entry."""
    # pylint: disable=unused-argument
    if "num_seg" not in params:
        raise NeuroTSValidationError(
            "The parameters must contain a 'num_seg' entry when the "
            "'growth_method' entry in parameters is 'trunk'."
        )


@register_global_validator()
def validate_parameters(params, _):
    """Validate parameters."""
    validate_neuron_params(params)


@register_global_validator()
def validate_distributions(_, distrs):
    """Validate distributions."""
    validate_neuron_distribs(distrs)


@register_validator("tmd", "tmd_apical", "tmd_gradient")
def check_bar_length(params, distrs):
    """Check consistency between parameters and persistence diagram."""
    if "min_bar_length" not in distrs:
        raise NeuroTSValidationError(
            "The distributions must contain a 'min_bar_length' entry when the "
            "'growth_method' entry in parameters is in ['tmd', 'tmd_apical', 'tmd_gradient']."
        )
    if "mean" not in params.get("step_size", {}).get("norm", {}):
        raise NeuroTSValidationError(
            "The parameters must contain a 'step_size' entry when the "
            "'growth_method' entry in parameters is in ['tmd', 'tmd_apical', 'tmd_gradient']."
        )
    check_min_bar_length(params, distrs)


@register_global_validator()
def check_metric_consistency(params, distrs):
    """Check consistency between metric parameters and distributions values."""
    for tree_type in params["grow_types"]:
        metric1 = params[tree_type].get("metric")
        metric2 = distrs[tree_type].get("filtration_metric")
        if metric1 not in ["trunk_length", metric2]:
            raise ValueError(
                "Metric of parameters and distributions is inconsistent:"
                + f" {metric1} != {metric2}"
            )


@register_global_validator()
def check_diameter_consistency(params, distrs):
    """Check consistency between diameter parameters and distributions values."""
    method1 = params["diameter_params"]["method"]
    method2 = distrs["diameter"]["method"]
    if method1 != method2:
        raise ValueError(
            "Diameters methods of parameters and distributions is inconsistent:"
            + f" {method1} != {method2}"
        )


@register_global_validator()
def check_deprecated_radius(params, distrs):  # pylint: disable=unused-argument
    """Check that the 'radius' parameter is not present or raise a warning."""
    grow_types = params.get("grow_types", [])
    for i in grow_types:
        neurite_type_params = params.get(i, {})
        if "radius" in neurite_type_params:
            warnings.warn(
                f"The 'radius' parameter (in {i}) is deprecated and will be forbidden in a future "
                "version, most of the time it's not used but if you want to retrieve the same "
                "results as before please use the 'uniform' diameter model.",
                FutureWarning,
            )
