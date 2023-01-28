"""Functions to check that the given parameters and distributions will give relevant results.

The functions used as relevance checkers should have a name like 'check_*' and have the following
signature: `check_something(params, distrs, start_point=None, context=None)`. The `start_point` and
`context` parameters should always be optional, as they will not be known during the preprocessing
step.

These functions can be called either in validity checkers or inside the grower codes.
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
