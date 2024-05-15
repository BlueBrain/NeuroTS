"""Functions to modify the given parameters and distributions before running the algorithm.

The functions used as preprocesses should have the signature: `check_something(params, distrs)`.
These functions should be very generic and should not depend on any context in which the related
grower is used.

The preprocesses should be registered to be executed in the preprocess step using the
`@register_preprocessor` decorator if they are applied per grow_type and growth_method, or with
`@register_global_processor` if they need the entire data.
"""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

from neurots.generate.orientations import fit_3d_angles
from neurots.preprocess.utils import register_global_preprocessor


@register_global_preprocessor()
def preprocess_3d_angles(params, distrs):
    """Fit 3d angle data if enabled."""
    fit_3d_angles(params, distrs)
