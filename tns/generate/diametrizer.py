''' Models to create diameters of synthesized cells '''
import numpy as np
from tns.morphio_utils import DICT_OF_TYPES, STR_TO_TYPES
from tns.morphio_utils import section_filter, root_section_filter


def sample(data):
    """Returns a value according to the input data"""
    return np.random.choice(data)


def section_lengths(section):
    """Computes all segment lengths within section"""
    return np.linalg.norm(section.points[1:] - section.points[:-1], axis=1)


def redefine_diameter_section(section, diam_ind, diam_new):
    """Hack to replace one diameter at index diam_ind with value diam_new"""
    section.diameters = np.array(section.diameters.tolist()[:diam_ind] +
                        [diam_new] + section.diameters.tolist()[diam_ind + 1:])
    if len(section.points) != len(section.diameters):
        raise Exception('Mismatch in dimensions of diameters.')


def bifurcator(initial_diam, num_children, rall_ratio, siblings_ratio):
    '''Returns the computed bifurcation diameter'''
    # pylint: disable=assignment-from-no-return
    reduction_factor = np.power(1. + (num_children - 1) * np.power(siblings_ratio,
                                                                   rall_ratio), 1. / rall_ratio)
    return initial_diam / reduction_factor


def merger(section, trunk, rall_ratio):
    '''Returns the computed bifurcation diameter'''
    # pylint: disable=assignment-from-no-return
    # diameters[0] is the duplicate point
    diameters_children = [ch.diameters[1] for ch in section.children]
    parent_d = np.power(np.sum([np.power(d, rall_ratio)
                                for d in diameters_children]), 1. / rall_ratio)

    diam_val = parent_d if parent_d <= trunk else np.max(diameters_children)
    redefine_diameter_section(section, len(section.diameters) - 1, diam_val)


def taper_section_diam_from_root(section, initial_diam, taper, min_diam=0.07, max_diam=100.):
    '''Corrects the diameters of a section'''
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


def taper_section_diam_from_tips(section, final_diam, taper, min_diam=0.07, max_diam=100.):
    '''Corrects the diameters of a section'''
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
    '''Corrects the diameters of a section by smoothing between initial and final diameters'''
    def sec_mean_taper(sec):
        """Returns the mean tapering of section"""
        min_diam = min(sec.diameters)
        lengths = [np.linalg.norm(i) for i in section.points[1:] - section.points[:-1]]
        di_li = np.sum([(sec.diameters[i] + sec.diameters[i + 1]) / 2. * lengths[i]
                        for i in range(len(sec.points) - 1)])
        return (di_li - min_diam * np.sum(lengths)) / np.sum(lengths)

    taper = sec_mean_taper(section)
    taper_section_diam_from_root(section, section.diameters[0], taper, min_diam=min_diam,
                                 max_diam=np.max(section.diameters))


def diametrize_from_root(neuron, model_all, neurite_type=None):
    '''Corrects the diameters of a morphio-neuron according to the model.
       Starts from the root and moves towards the tips.
    '''
    for r in root_section_filter(neuron, tree_type=neurite_type):

        model = model_all[DICT_OF_TYPES[r.type]]  # Selected by the root type.
        trunk_diam = sample(model['trunk'])
        min_diam = np.min(model['term'])
        status = {s.id: False for s in r.iter()}

        active = [r]

        while active:
            for section in list(active):

                if section.is_root:
                    taper = sample(model['trunk_taper'])
                    init_diam = trunk_diam
                else:
                    taper = sample(model['taper'])
                    init_diam = section.diameters[0]

                taper_section_diam_from_root(section, init_diam, taper=taper,
                                             min_diam=min_diam, max_diam=trunk_diam)
                status[section.id] = True  # Tapering of section complete.
                active.remove(section)

                children = np.array(section.children)

                if len(children) > 1:
                    d1 = bifurcator(section.diameters[-1], len(children),
                                    rall_ratio=model['Rall_ratio'],
                                    siblings_ratio=model['siblings_ratio'])

                    for i, ch in enumerate(children):
                        new_diam = d1 if i == 0 else d1 * model['siblings_ratio']
                        redefine_diameter_section(ch, 0, new_diam)
                        active.append(ch)

        for section in r.iter():
            if not section.is_root:  # if section is not root replace diameter with parent
                # Ensures duplicate points consistency. First point will be removed while writen.
                redefine_diameter_section(section, 0, section.parent.diameters[-1])


def diametrize_from_tips(neuron, model_all, neurite_type=None):
    '''Corrects the diameters of a morphio-neuron according to the model.
       Starts from the tips and moves towards the root.
    '''
    for r in root_section_filter(neuron, tree_type=neurite_type):

        model = model_all[DICT_OF_TYPES[r.type]]  # Selected by the root type.
        trunk_diam = sample(model['trunk'])
        min_diam = np.min(model['term'])
        tips = [s for s in r.iter() if not s.children]
        status = {s.id: False for s in r.iter()}

        for tip in tips:
            redefine_diameter_section(tip, len(tip.diameters) - 1, sample(model['term']))

        active = tips

        while active:
            for section in list(active):
                taper = sample(model['trunk_taper']) if section.is_root else sample(model['taper'])

                taper_section_diam_from_tips(section, section.diameters[-1], taper=taper,
                                             min_diam=min_diam, max_diam=trunk_diam)
                status[section.id] = True  # Tapering of section complete.
                active.remove(section)

                if not section.is_root:
                    par = section.parent
                    if np.alltrue([status[ch.id] for ch in par.children]):
                        # Assign a new diameter to the last point if section is not terminal
                        merger(par, trunk_diam, model['Rall_ratio'])
                        active.append(par)

        for section in r.iter():
            if not section.is_root:  # if section is not root replace diameter with parent
                # Ensures duplicate points consistency. First point will be removed while writen.
                redefine_diameter_section(section, 0, section.parent.diameters[-1])


def diametrize_constant_per_section(neuron, neurite_type=None):
    '''Corrects the diameters of a morphio-neuron to make them constant per section'''
    for sec in section_filter(neuron, neurite_type):
        mean_diam = np.mean(sec.diameters)
        sec.diameters = mean_diam * np.ones(len(sec.diameters))


def diametrize_constant_per_neurite(neuron, neurite_type=None):
    '''Corrects the diameters of a morphio-neuron to make them constant per neurite'''
    roots = root_section_filter(neuron, neurite_type)

    for root in roots:
        mean_diam = np.mean(np.hstack([sec.diameters for sec in root.iter()]))
        for sec in root.iter():
            sec.diameters = mean_diam * np.ones(len(sec.diameters))


def diametrize_smoothing(neuron, neurite_type=None):
    '''Corrects the diameters of a morphio-neuron, by smoothing them within each section'''
    for sec in section_filter(neuron, neurite_type):
        smooth_section_diam(sec)


def build(neuron, input_model=None, neurite_types=None, diam_method='M5'):
    '''Diametrize according to the selected method.
       Save file formats in the selected output_path'''
    methods = {'M1': diametrize_constant_per_neurite,
               'M2': diametrize_constant_per_section,
               'M3': diametrize_smoothing,
               'M4': diametrize_from_root,
               'M5': diametrize_from_tips}

    if neurite_types is None:
        neurite_types = ['apical', 'basal']

    for tree_type in neurite_types:
        if diam_method in ['M1', 'M2', 'M3']:
            methods[diam_method](neuron, STR_TO_TYPES[tree_type])
        else:
            methods[diam_method](neuron, input_model, STR_TO_TYPES[tree_type])
