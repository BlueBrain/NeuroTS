"""Example for comparing a neuron to a population
   using their morphometrics"""
import neurom as nm
import numpy as np
import pylab as plt

# Set a list of features to be extracted
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

# Set a list of names for the previous features
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


def get_features(object1, object2, flist=feat_list, neurite_type=nm.BASAL_DENDRITE):
    """Computes features from module mod"""
    collect_all = []

    for feat in flist:
        feature_pop = nm.get(feat, object1, neurite_type=neurite_type)
        feature_neu = nm.get(feat, object2, neurite_type=neurite_type)

        collect_all.append([feature_pop, feature_neu])

    return collect_all


def get_features_median(object1, object2, flist=feat_list, neurite_type=nm.BASAL_DENDRITE):
    """Computes features from module mod"""
    collect_all = []

    for feat in flist:
        feature_pop = [np.median(nm.get(feat, obj, neurite_type=neurite_type)) for obj in object1]
        feature_neu = nm.get(feat, object2, neurite_type=neurite_type)

        collect_all.append([feature_pop, feature_neu])

    return collect_all


def mvs_score(data, percent=50):
    """Get the MED - MVS score equal to
    the absolute difference between the median
    of the population and the median of the neuron
    divided by the maximum visible spread.
    """
    median_diff = np.abs(np.median(data[0]) - np.median(data[1]))
    max_percentile = np.max(
        [
            np.percentile(data[0], 100 - percent / 2.0, axis=0),
            np.percentile(data[1], 100 - percent / 2.0, axis=0),
        ]
    )

    min_percentile = np.min(
        [
            np.percentile(data[0], percent / 2.0, axis=0),
            np.percentile(data[1], percent / 2.0, axis=0),
        ]
    )

    max_vis_spread = max_percentile - min_percentile

    return median_diff / max_vis_spread


def normalize(data):
    """Returns the data normalized by
    subtracting the mean of the population
    and dividing by the std of the population.
    """
    m = np.mean(data[0])
    st = np.std(data[0])

    return [(data[0] - m) / st, (data[1] - m) / st]


def score_test(data):
    """Computes the absolute differences
    between a population and a neuron and
    returns True if > 1 and False if <= 1
    """
    return np.abs(np.median(data[1]) - np.median(data[0])) > 1


def score_mvs_test(data, threshold=0.3):
    """Computes the absolute differences
    between a population and a neuron and
    returns True if > 1 and False if <= 1
    """
    return mvs_score(data) > threshold


def boxplots(data, fnames=feat_names, threshold=0.5):
    """Plots a list of boxplots for each feature in feature_list for object 1.
    Then presents the value of object 2 for each feature as an colored objected
    in the same boxplot.

    Parameters:
        data:\
            A list of pairs of flattened data for each feature.
        new_fig (Optional[bool]):\
            Default is False, which returns the default matplotlib axes 111\
            If a subplot needs to be specified, it should be provided in xxx format.
        subplot (Optional[bool]):\
            Default is False, which returns a matplotlib figure object. If True,\
            returns a matplotlib axis object, for use as a subplot.

    Returns:
        fig:\
            A figure which contains the list of boxplots.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)

    norm_data = [normalize(d) for d in data]

    ax.boxplot(np.array(norm_data)[:, 0], vert=False)

    for i, d in enumerate(norm_data):
        if score_mvs_test(data[i], threshold):
            col = "r"
            mark = "h"
        else:
            col = "g"
            mark = "s"

        ax.scatter(np.median(d[1]), len(norm_data) - i, s=100, color=col, marker=mark)

    ax.set_yticklabels(fnames)

    ax.set_xlabel("Normalized units (dimensionless)")
    ax.set_ylabel("")
    ax.set_title("Summarizing validation features")

    plt.tight_layout(True)

    return fig, ax


def dict_mvs_scores(data, feat_list):
    """Creates a dictionary with the mvs scores
    of a neuron compared to a population.
    """
    dictionary = {feat_list[i]: mvs_score(d) for i, d in enumerate(data)}

    return dictionary


def dict_mvs_scores_population(population1, population2, feat_list):
    """Creates a dictionary with the mvs scores
    of a neuron compared to a population.
    """
    dictionary = {f: [] for f in feat_list}

    for n2 in population2.neurons:
        data = get_features(population1, n2, feat_list)
        for i, d in enumerate(data):
            dictionary[feat_list[i]].append(mvs_score(d))

    return dictionary


def write_mvs_scores(dictionary, names, feat_list, output_file):
    """Outputs the dictionary of the feature scores
    for each neuron using its name as an identifier.
    """
    import csv

    F = open(output_file, "wb")
    Fcsv = csv.writer(F)
    Fcsv.writerow(["CellID"] + dictionary.keys())

    for i, n in enumerate(names):
        Fcsv.writerow([n] + list(np.array(dictionary.values())[:, i]))
    F.close()


def load_csv(filename):
    import csv

    F = open(filename)
    csv_reader = csv.reader(F)
    data = []
    for i in csv_reader:
        data.append(i)

    return np.array(np.array(data)[1:, 1:], dtype=np.float)
