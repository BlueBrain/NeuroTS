"""Functions to check that the given parameters and distributions will give relevant results.

The functions used as relevance checkers should have a name like 'check_*' and have the following
signature: `check_something(params, distrs, start_point=None, context=None)`. The `start_point` and
`context` parameters should always be optional, as they will not be known during the preprocessing
step.

These functions can be called either in validity checkers or inside the grower codes.
"""

# Copyright (C) 2022  Blue Brain Project, EPFL
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
