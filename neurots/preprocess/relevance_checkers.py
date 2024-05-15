"""Functions to check that the given parameters and distributions will give relevant results.

The functions used as relevance checkers should have a name like 'check_*' and have the following
signature: `check_something(params, distrs, start_point=None, context=None)`. The `start_point` and
`context` parameters should always be optional, as they will not be known during the preprocessing
step.

These functions can be called either in validity checkers or inside the grower codes.
"""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

import logging

L = logging.getLogger(__name__)


def check_min_bar_length(params, distrs, start_point=None, context=None):
    """Consistency check between parameters - persistence diagram."""
    # pylint: disable=unused-argument
    barSZ = distrs["min_bar_length"]
    stepSZ = params["step_size"]["norm"]["mean"]
    if stepSZ >= barSZ:
        L.warning(
            "Selected step size %f is too big for bars of size %f",
            stepSZ,
            barSZ,
        )
