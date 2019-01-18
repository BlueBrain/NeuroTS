import numpy as np

from collections import deque
from morphio import SectionType

dict_of_types = {SectionType.apical_dendrite: 4,
                 SectionType.basal_dendrite: 3,
                 SectionType.axon: 2}


def sample(data):
    """Returns a value according to the input data"""
    return np.random.choice(data)


def bifurcator(initial_diam, num_children, rall_ratio, siblings_ratio):
    '''Returns the computed bifurcation diameter'''
    reduction_factor = np.power(1. + (num_children - 1) * np.power(siblings_ratio, rall_ratio), 1. / rall_ratio)
    return initial_diam / reduction_factor


def merger(sect, model_all, status, rall_ratio):
    '''Returns the computed bifurcation diameter'''
    if alltrue(status[[ch.id for ch in sect.children]]):
        diameters_children = []
        for ch in sect.children:
            diameters_children.append(ch.diameters[0])

        parent_d = np.power(np.sum([np.power(d, rall_ratio) for d in diameters_children]), 1. / rall_ratio)

        if parent_d <= np.max(model['trunk']):
            sect.diameters[-1] = parent_d
        else:
            sect.diameters[-1] = np.max(diameters_children)
        return True  # Action completed, to remove from active sections
    else:
        return False  # Action not completed, to keep in active sections


def taper_section_diam(section, initial_diam, taper, min_diam=0.07):
    '''Corrects the diameters of a section'''
    taps = taper / len(section.diameters)
    section.diameters = np.array([initial_diam * ( 1 - i * taps) 
                                  if initial_diam * ( 1 - i * taps) > min_diam
                                  else min_diam for i in range(len(section.diameters))],
                                  dtype=np.float32)


def smooth_section_diam(section, min_diam=0.07):
    '''Corrects the diameters of a section by smoothing between initial and final diameters'''
    initial_diam = section.diameters[0]
    taps = (np.max(section.diameters) - np.min(section.diameters)) / len(section.diameters)
    section.diameters = np.array([initial_diam * ( 1 - i * taps) 
                                  if initial_diam * ( 1 - i * taps) > min_diam
                                  else min_diam for i in range(len(section.diameters))],
                                  dtype=np.float32)

def diametrize_from_root(neuron, model_all):
    '''Corrects the diameters of a morphio-neuron according to the model.
       Starts from the root and moves towards the tips.
    '''
    roots = neuron.root_sections

    for r in roots:
        model = model_all[dict_of_types[r.type]]
        siblings_ratio = model['siblings_ratio']
        for s in r.iter():
            try:
                # When not first section of the tree
                par = s.parent
                children = np.array(par.children)
                childrenID = np.where(children == s)[0][0]
                d1 = bifurcator(par.diameters[-1], len(children),
                                rall_ratio=model['Rall_ratio'],
                                siblings_ratio=siblings_ratio)
                if childrenID:
                    new_diam = d1 * siblings_ratio
                else:
                    new_diam = d1
            except:
                # This applies only to first tree section
                new_diam = sample(model['trunk'])

            taper_section_diam(s, new_diam, taper=sample(model['taper']),
                               min_diam=np.min(model['term']))


def diametrize_from_tips(neuron, model_all):
    '''Corrects the diameters of a morphio-neuron according to the model.
       Starts from the tips and moves towards the root.
    '''
    tips = [s for s in neuron.iter() if len(s.children) == 0]

    for t in tips:
        model = model_all[t.type]
        t.diameters[-1] = sample(model['term'])

    active = deque(tips)
    visited = set()

    while active:
        section = active.pop()
        model = model_all[section.type]

        if section.children:
            # Assign a new diameter to the last point if section is not terminal
            state = merger(section, model_all, status, model['Rall_ratio'])
        else:
            # Assign a new diameter to the last point if section is terminal
            state = True

        # Fill in the section with new diameters, only when all children are processed.
        if state:
            # Taper within a section
            taper = - sample(model['taper'])
            init_diam = section.diameters[-1] + taper
            taper_section_diam(s, init_diam, taper=taper,
                               min_diam=np.min(model['term']))


def diametrize_constant(neuron):
    '''Corrects the diameters of a morphio-neuron according to the model'''
    roots = neuron.root_sections

    for r in roots:
        for s in r.iter():
            mean_diam = np.mean(s.diameters)
            s.diameters = mean_diam * np.ones(len(s.diameters))


def diametrize_constant_all(neuron):
    '''Corrects the diameters of a morphio-neuron according to the model'''
    roots = neuron.root_sections
    diams = []

    for r in roots:
        for s in r.iter():
            diams = diams + s.diameters.tolist()

    mean_diam = np.mean(diams)

    for r in roots:
        for s in r.iter():
            s.diameters = mean_diam * np.ones(len(s.diameters))


def diametrize_smoothing(neuron, model_all):
    '''Corrects the diameters of a morphio-neuron according to the model'''

    for r in neuron.root_sections:
        for s in r.iter():
            smooth_section_diam(s)
