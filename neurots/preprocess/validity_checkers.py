"""Functions to check that the given parameters and distributions will not break the algorithm.

The functions used as validity checkers should have a name like 'check_*' and have the following
signature: `check_something(params, distrs)`. These functions should be very generic and should
not depend on any context in which the related grower is used.

The checkers should be registered to be executed in the preprocess step using the
`@register_validator` decorator.
"""

# Copyright (C) 2022  Blue Brain Project, EPFL
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

from neurots.preprocess.relevancy_checkers import check_min_bar_length
from neurots.preprocess.utils import register_validator


@register_validator("trunk")
def check_num_seg(params, distrs):
    """Check that params contains a 'num_seg' entry."""
    # pylint: disable=unused-argument
    if "num_seg" not in params:
        raise KeyError(
            "The parameters must contain a 'num_seg' entry when the "
            "'growth_method' entry in parameters is 'trunk'."
        )


@register_validator("tmd", "tmd_apical", "tmd_gradient")
def check_bar_length(params, distrs):
    """Check consistency between parameters and persistence diagram."""
    if "min_bar_length" not in distrs:
        raise KeyError(
            "The distributions must contain a 'min_bar_length' entry when the "
            "'growth_method' entry in parameters is in ['tmd', 'tmd_apical', 'tmd_gradient']."
        )
    if "mean" not in params.get("step_size", {}).get("norm", {}):
        raise KeyError(
            "The parameters must contain a 'step_size' entry when the "
            "'growth_method' entry in parameters is in ['tmd', 'tmd_apical', 'tmd_gradient']."
        )
    check_min_bar_length(params, distrs)
