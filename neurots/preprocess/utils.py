"""Some utils for preprocessing."""

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

from collections import defaultdict
from copy import deepcopy
from itertools import chain

_REGISTERED_FUNCTIONS = {
    "preprocessors": defaultdict(set),
    "validators": defaultdict(set),
    "global_preprocessors": set(),
    "global_validators": set(),
}


def register_global_preprocessor():
    """Register a global preprocess function."""

    def inner(func):
        _REGISTERED_FUNCTIONS["global_preprocessors"].add(func)
        return func

    return inner


def register_preprocessor(*growth_methods):
    """Register a preprocess function."""

    def inner(func):
        for i in growth_methods:
            _REGISTERED_FUNCTIONS["preprocessors"][i].add(func)
        return func

    return inner


def register_global_validator():
    """Register a global validation function."""

    def inner(func):
        _REGISTERED_FUNCTIONS["global_validators"].add(func)
        return func

    return inner


def register_validator(*growth_methods):
    """Register a validation function."""

    def inner(func):
        for i in growth_methods:
            _REGISTERED_FUNCTIONS["validators"][i].add(func)
        return func

    return inner


def preprocess_inputs(params, distrs):
    """Validate and preprocess all inputs."""
    params = deepcopy(params)
    distrs = deepcopy(distrs)
    for preprocess_func in chain(
        _REGISTERED_FUNCTIONS["global_validators"],
        _REGISTERED_FUNCTIONS["global_preprocessors"],
    ):
        preprocess_func(params, distrs)

    for grow_type in params["grow_types"]:
        growth_method = params[grow_type]["growth_method"]
        for preprocess_func in chain(
            _REGISTERED_FUNCTIONS["validators"][growth_method],
            _REGISTERED_FUNCTIONS["preprocessors"][growth_method],
        ):
            preprocess_func(params[grow_type], distrs[grow_type])

    return params, distrs
