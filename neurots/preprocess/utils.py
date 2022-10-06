"""Some utils for preprocessing."""
from collections import defaultdict
from copy import deepcopy

from neurots.validator import validate_neuron_distribs
from neurots.validator import validate_neuron_params

_PREPROCESS_FUNCTIONS = defaultdict(set)


def register_preprocess(*growth_methods):
    """Register a preprocess function."""

    def inner(func):
        for i in growth_methods:
            _PREPROCESS_FUNCTIONS[i].add(func)
        return func

    return inner


def preprocess_inputs(params, distrs):
    """Validate and preprocess all inputs."""
    params = deepcopy(params)
    distrs = deepcopy(distrs)
    validate_neuron_params(params)
    validate_neuron_distribs(distrs)

    for grow_type in params["grow_types"]:
        growth_method = params[grow_type]["growth_method"]
        for preprocess_func in _PREPROCESS_FUNCTIONS[growth_method]:
            preprocess_func(params[grow_type], distrs[grow_type])

    return params, distrs
