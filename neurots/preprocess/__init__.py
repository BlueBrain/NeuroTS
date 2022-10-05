"""Functions used for preprocessing."""
from collections import defaultdict

from neurots.generate.algorithms import tmdgrower
from neurots.validator import validate_neuron_distribs
from neurots.validator import validate_neuron_params

_preprocess_functions = defaultdict(set)


def register_preprocess(*growth_methods):
    """Register a preprocess function."""

    def inner(func):
        for i in growth_methods:
            _preprocess_functions[i].add(func)
        return func

    return inner


@register_preprocess("trunk")
def check_num_seg(params, distrs):
    """Check that params contains a 'num_seg' entry."""
    if "num_seg" not in params:
        raise KeyError(
            "The parameters must contain a 'num_seg' entry when the "
            "'growth_method' entry in parameters is 'trunk'."
        )


@register_preprocess("tmd", "tmd_apical", "tmd_gradient")
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
    tmdgrower.TMDAlgo.check_min_bar_length(params, distrs)


def preprocess_inputs(params, distrs):
    """Validate and preprocess all inputs."""
    validate_neuron_params(params)
    validate_neuron_distribs(distrs)

    for grow_type in params["grow_types"]:
        growth_method = params[grow_type]["growth_method"]
        for preprocess_func in _preprocess_functions[growth_method]:
            preprocess_func(params[grow_type], distrs[grow_type])
