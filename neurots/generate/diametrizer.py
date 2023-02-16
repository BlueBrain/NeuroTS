"""Models to create diameters of synthesized cells."""

# Copyright (C) 2021  Blue Brain Project, EPFL
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

import inspect

import numpy as np
from morphio import SectionType

from neurots.utils import NeuroTSError


def section_filter(neuron, tree_type=None):
    """Filter all sections according to type."""
    if tree_type is None:
        return list(neuron.iter())
    return [i for i in neuron.iter() if i.type == tree_type]


def root_section_filter(neuron, tree_type=None):
    """Filter root sections according to type."""
    if tree_type is None:
        return list(neuron.root_sections)
    return [i for i in neuron.root_sections if i.type == tree_type]


def sample(data, random_generator=np.random):
    """Returns a value according to the input data.

    Args:
        data (list): The data to sample from.
        random_generator (numpy.random.Generator): The random number generator to use.
    """
    return random_generator.choice(data)


def section_lengths(section):
    """Computes all segment lengths within section.

    Args:
        section (morphio.Section): The section whose length is computed.

    Returns:
        float: The total length of the section.
    """
    return np.linalg.norm(section.points[1:] - section.points[:-1], axis=1)


def redefine_diameter_section(section, diam_ind, diam_new):
    """Hack to replace one diameter at index diam_ind with value diam_new.

    Args:
        section (morphio.mut.Section): The section whose diameter is updated.
        diam_ind (int): The index to replace.
        diam_new (float): The new diameter value.
    """
    section.diameters = np.array(
        section.diameters.tolist()[:diam_ind]
        + [diam_new]
        + section.diameters.tolist()[(diam_ind + 1) :]
    )
    if len(section.points) != len(section.diameters):
        raise NeuroTSError("Mismatch in dimensions of diameters.")


def bifurcator(initial_diam, num_children, rall_ratio, siblings_ratio):
    """Returns the computed bifurcation diameter.

    Args:
        initial_diam (float): The initial diameter value.
        num_children (int): The number of children.
        rall_ratio (float): The rall ratio.
        siblings_ratio (float): The sibling ratio.
    """
    # pylint: disable=assignment-from-no-return
    reduction_factor = np.power(
        1.0 + (num_children - 1) * np.power(siblings_ratio, rall_ratio),
        1.0 / rall_ratio,
    )
    return initial_diam / reduction_factor


def merger(section, trunk_diam, rall_ratio):
    """Returns the computed bifurcation diameter.

    Args:
        section (morphio.mut.Section): The section whose diameter is updated.
        trunk_diam (float): The trunk diameter.
        rall_ratio (float): The rall ratio.
    """
    # pylint: disable=assignment-from-no-return
    # diameters[0] is the duplicate point
    diameters_children = [ch.diameters[1] for ch in section.children]
    parent_d = np.power(
        np.sum([np.power(d, rall_ratio) for d in diameters_children]), 1.0 / rall_ratio
    )

    diam_val = parent_d if parent_d <= trunk_diam else np.max(diameters_children)
    redefine_diameter_section(section, len(section.diameters) - 1, diam_val)


def taper_section_diam_from_root(section, initial_diam, taper, min_diam=0.07, max_diam=100.0):
    """Corrects the diameters of a section.

    Args:
        section (morphio.mut.Section): The section whose diameters are updated.
        initial_diam (float): The initial diameter value.
        taper (float): The taper value.
        min_diam (float): The min diameter value.
        max_diam (float): The max diameter value.
    """
    diams = [initial_diam]

    if section.is_root:
        range_ = range(1, len(section.diameters))
    else:
        range_ = range(0, len(section.diameters) - 1)

    # lengths of each segments will be used for scaling of tapering
    lengths = [0] + section_lengths(section).tolist()
    taps = taper / np.sum(lengths)

    for i in range_:
        # Diameters decrease from root towards the tip
        new_diam = diams[-1] - taps * lengths[i]

        if new_diam >= max_diam:
            diams.append(max_diam)
        elif new_diam <= min_diam:
            diams.append(min_diam)
        else:
            diams.append(new_diam)

    section.diameters = np.array(diams, dtype=np.float32)


def taper_section_diam_from_tips(section, final_diam, taper, min_diam=0.07, max_diam=100.0):
    """Corrects the diameters of a section.

    Args:
        section (morphio.mut.Section): The section whose diameters are updated.
        final_diam (float): The final diameter value.
        taper (float): The taper value.
        min_diam (float): The min diameter value.
        max_diam (float): The max diameter value.
    """
    diams = [final_diam]
    # lengths of each segments will be used for scaling of tapering
    lengths = section_lengths(section)
    taps = taper / np.sum(lengths)

    for i in range(len(section.diameters) - 1):
        # Diameters increase from tip towards the root
        new_diam = diams[-1] + taps * lengths[len(section.diameters) - 2 - i]

        if new_diam >= max_diam:
            diams.append(max_diam)
        elif new_diam <= min_diam:
            diams.append(min_diam)
        else:
            diams.append(new_diam)

    diams.reverse()
    section.diameters = np.array(diams, dtype=np.float32)


def smooth_section_diam(section, min_diam=0.07):
    """Corrects the diameters of a section by smoothing between initial and final diameters.

    Args:
        section (morphio.mut.Section): The section whose diameters are updated.
        min_diam (float): The min diameter value.
    """

    def sec_mean_taper(sec):
        """Returns the mean tapering of section."""
        min_diam = min(sec.diameters)
        lengths = [np.linalg.norm(i) for i in section.points[1:] - section.points[:-1]]
        di_li = np.sum(
            [
                (sec.diameters[i] + sec.diameters[i + 1]) / 2.0 * lengths[i]
                for i in range(len(sec.points) - 1)
            ]
        )
        return (di_li - min_diam * np.sum(lengths)) / np.sum(lengths)

    taper = sec_mean_taper(section)
    taper_section_diam_from_root(
        section,
        section.diameters[0],
        taper,
        min_diam=min_diam,
        max_diam=np.max(section.diameters),
    )


def diametrize_from_root(
    neuron,
    neurite_type=None,
    *,
    model_params,
    random_generator=np.random,
):  # pylint: disable=too-many-locals
    """Corrects the diameters of a morphio-neuron according to the model.

    Starts from the root and moves towards the tips.

    Args:
        neuron (morphio.mut.Morphology): The morphology that will be diametrized.
        neurite_type (morphio.SectionType): Only the neurites of this type are diametrized.
        model_params (dict): The model parameters.
        random_generator (numpy.random.Generator): The random number generator to use.
    """
    for r in root_section_filter(neuron, tree_type=neurite_type):
        model = model_params[r.type.name]  # Selected by the root type.
        trunk_diam = sample(model["trunk"], random_generator)
        min_diam = np.min(model["term"])
        status = {s.id: False for s in r.iter()}

        active = [r]

        while active:
            for section in list(active):
                if section.is_root:
                    taper = sample(model["trunk_taper"], random_generator)
                    init_diam = trunk_diam
                else:
                    taper = sample(model["taper"], random_generator)
                    init_diam = section.diameters[0]

                taper_section_diam_from_root(
                    section,
                    init_diam,
                    taper=taper,
                    min_diam=min_diam,
                    max_diam=trunk_diam,
                )
                status[section.id] = True  # Tapering of section complete.
                active.remove(section)

                children = np.array(section.children)

                if len(children) > 1:
                    d1 = bifurcator(
                        section.diameters[-1],
                        len(children),
                        rall_ratio=model["Rall_ratio"],
                        siblings_ratio=model["siblings_ratio"],
                    )

                    for i, ch in enumerate(children):
                        new_diam = d1 if i == 0 else d1 * model["siblings_ratio"]
                        redefine_diameter_section(ch, 0, new_diam)
                        active.append(ch)

        for section in r.iter():
            if not section.is_root:  # if section is not root replace diameter with parent
                # Ensures duplicate points consistency. First point will be removed while written.
                redefine_diameter_section(section, 0, section.parent.diameters[-1])


def diametrize_from_tips(neuron, neurite_type=None, *, model_params, random_generator=np.random):
    """Corrects the diameters of a morphio-neuron according to the model.

    Starts from the tips and moves towards the root.

    Args:
        neuron (morphio.mut.Morphology): The morphology that will be diametrized.
        neurite_type (morphio.SectionType): Only the neurites of this type are diametrized.
        model_params (dict): The model parameters.
        random_generator (numpy.random.Generator): The random number generator to use.
    """
    for r in root_section_filter(neuron, tree_type=neurite_type):
        model = model_params[r.type.name]  # Selected by the root type.
        trunk_diam = sample(model["trunk"], random_generator)
        min_diam = np.min(model["term"])
        tips = [s for s in r.iter() if not s.children]
        status = {s.id: False for s in r.iter()}

        for tip in tips:
            redefine_diameter_section(
                tip, len(tip.diameters) - 1, sample(model["term"], random_generator)
            )

        active = tips

        while active:
            for section in list(active):
                taper = (
                    sample(model["trunk_taper"], random_generator)
                    if section.is_root
                    else sample(model["taper"], random_generator)
                )

                taper_section_diam_from_tips(
                    section,
                    section.diameters[-1],
                    taper=taper,
                    min_diam=min_diam,
                    max_diam=trunk_diam,
                )
                status[section.id] = True  # Tapering of section complete.
                active.remove(section)

                if not section.is_root:
                    par = section.parent
                    if np.alltrue([status[ch.id] for ch in par.children]):
                        # Assign a new diameter to the last point if section is not terminal
                        merger(par, trunk_diam, model["Rall_ratio"])
                        active.append(par)

        for section in r.iter():
            if not section.is_root:  # if section is not root replace diameter with parent
                # Ensures duplicate points consistency. First point will be removed while written.
                redefine_diameter_section(section, 0, section.parent.diameters[-1])


def diametrize_constant_per_section(neuron, neurite_type=None):
    """Corrects the diameters of a morphio-neuron to make them constant per section.

    Args:
        neuron (morphio.mut.Morphology): The morphology that will be diametrized.
        neurite_type (morphio.SectionType): Only the neurites of this type are diametrized.
    """
    for sec in section_filter(neuron, neurite_type):
        mean_diam = np.mean(sec.diameters)
        sec.diameters = mean_diam * np.ones(len(sec.diameters))


def diametrize_constant_per_neurite(neuron, neurite_type=None):
    """Corrects the diameters of a morphio-neuron to make them constant per neurite.

    Args:
        neuron (morphio.mut.Morphology): The morphology that will be diametrized.
        neurite_type (morphio.SectionType): Only the neurites of this type are diametrized.
    """
    roots = root_section_filter(neuron, neurite_type)

    for root in roots:
        mean_diam = np.mean(np.hstack([sec.diameters for sec in root.iter()]))
        for sec in root.iter():
            sec.diameters = mean_diam * np.ones(len(sec.diameters))


def diametrize_smoothing(neuron, neurite_type=None):
    """Corrects the diameters of a morphio-neuron, by smoothing them within each section.

    Args:
        neuron (morphio.mut.Morphology): The morphology that will be diametrized.
        neurite_type (morphio.SectionType): Only the neurites of this type are diametrized.
    """
    for sec in section_filter(neuron, neurite_type):
        smooth_section_diam(sec)


diam_methods = {
    "M1": diametrize_constant_per_neurite,
    "M2": diametrize_constant_per_section,
    "M3": diametrize_smoothing,
    "M4": diametrize_from_root,
    "M5": diametrize_from_tips,
}


def build(
    neuron,
    input_model=None,
    neurite_types=None,
    diam_method=None,
    diam_params=None,
    random_generator=np.random,
):
    """Diametrize according to the selected method.

    Args:
        neuron (morphio.mut.Morphology): The morphology that will be diametrized.
        input_model (dict): The model parameters.
        neurite_types (list[str]): Only the neurites of these types are diametrized.
        diam_method (str or callable): The name of the diametrization method.
        diam_params (dict): The parameters passed to the diametrization method.
        random_generator (numpy.random.Generator): The random number generator to use.

    If ``diam_method`` is a string matching the models in ``diam_methods`` it will use an internal
    diametrizer. If a function is provided, it will use this function to diametrize the cells. This
    function should have the following arguments:

    * **neuron** (*morphio.mut.Morphology*): The morphology that will be diametrized.
    * **tree_type** (*str*): Only the neurites of this type are diametrized.
    * **model_params** (*dict*): The model parameters (optional).
    * **diam_params** (*dict*): The parameters passed to the diametrization method (optional).
    * **random_generator** (*numpy.random.Generator*): The random number generator to use
        (optional).

    and should only update the neuron object.
    """
    if neurite_types is None:
        neurite_types = [SectionType.apical_dendrite, SectionType.basal_dendrite]

    if isinstance(diam_method, str):
        try:
            diam_method = diam_methods[diam_method]
        except KeyError as exc:
            raise KeyError(
                "The name of the diametrization method is unknown: "
                f"'{diam_method}' is not in {list(diam_methods.keys())}"
            ) from exc

    elif not hasattr(diam_method, "__call__"):
        raise ValueError(f"Diameter method not understood, we got {diam_method}")

    for tree_type in neurite_types:
        if isinstance(tree_type, str):
            tree_type = getattr(SectionType, tree_type)
        param_signature = list(inspect.signature(diam_method).parameters.keys())
        optional_kw = {}
        if "model_params" in param_signature:
            optional_kw["model_params"] = input_model
        if "diam_params" in param_signature:
            optional_kw["diam_params"] = diam_params
        if "random_generator" in param_signature:
            optional_kw["random_generator"] = random_generator
        diam_method(neuron, tree_type, **optional_kw)
