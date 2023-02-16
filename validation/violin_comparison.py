"""Example for comparing two populations using
   the violin plots from their morphometrics"""
import neurom as nm
import numpy as np
import pandas
import pylab as plt
import seaborn

feat_list = [
    "number_of_neurites",
    "number_of_sections_per_neurite",
    "number_of_leaves",
    "number_of_bifurcations",
    "section_lengths",
    "section_tortuosity",
    "section_radial_distances",
    "section_path_distances",
    "section_branch_orders",
    "remote_bifurcation_angles",
]


feat_names = [
    "Number of neurites",
    "Number of sections",
    "Number of terminations",
    "Number of bifurcations",
    "Section lengths",
    "Section tortuosity",
    "Section radial distances",
    "Section path distances",
    "Section branch orders",
    "Remote bif angles",
]


def get_features_medians(object1, object2, flist=feat_list, neurite_type=nm.BASAL_DENDRITE):
    """Computes features from module mod"""
    collect_all = []

    for feat in flist:
        feature_pop = [np.median(nm.get(feat, obj, neurite_type=neurite_type)) for obj in object1]
        feature_neu = [np.median(nm.get(feat, obj, neurite_type=neurite_type)) for obj in object2]

        collect_all.append([feature_pop, feature_neu])

    return collect_all


def get_features_all(object1, object2, flist=feat_list, neurite_type=nm.BASAL_DENDRITE):
    """Computes features from module mod"""
    collect_all = []

    for feat in flist:
        feature_pop = []
        for obj in object1:
            feature_pop = feature_pop + nm.get(feat, obj, neurite_type=neurite_type).tolist()
        feature_neu = []
        for obj in object2:
            feature_neu = feature_neu + nm.get(feat, obj, neurite_type=neurite_type).tolist()

        collect_all.append([feature_pop, feature_neu])

    return collect_all


def transform2DataFrame(data, pop_names, flist=feat_names):
    """Returns a DataFrame in the appropriate
    format from a set of features"""
    values = []
    names = []
    feat = []
    # Loop through each feature
    for i, d1 in enumerate(data):
        m = np.mean(d1[0])
        st = np.std(d1[0])
        # Loop through populations
        for j, d2 in enumerate(d1):
            values = values + [(d3 - m) / st for d3 in d2]
            names = names + len(d2) * [pop_names[j]]
            feat = feat + len(d2) * [flist[i]]

    frame = pandas.DataFrame({"Data": names, "Values": values, "Morphological features": feat})

    return frame


def plot_violins(data, x="Morphological features", y="Values", hues="Data", **kwargs):
    """Plots the split violins of all features"""
    axs = seaborn.violinplot(x=x, y=y, hue=hues, data=data, palette="muted", split=True, **kwargs)
    plt.xticks(rotation=20)
    plt.tight_layout(True)
    return axs
