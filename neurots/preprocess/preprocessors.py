"""Functions to modify the given parameters and distributions before running the algorithm.

The functions used as preprocesses should have a name like 'preprocess_*' and have the following
signature: `check_something(params, distrs)`. These functions should be very generic and should
not depend on any context in which the related grower is used.

The preprocesses should be registered to be executed in the preprocess step using the
`@register_preprocess` decorator.
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

# TODO: uncomment the next line when a preprocess is added
# from neurots.preprocess.utils import register_preprocessor
