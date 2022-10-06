"""Functions used for preprocessing."""
from neurots.generate.algorithms import tmdgrower
from neurots.preprocess.utils import register_preprocess


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
