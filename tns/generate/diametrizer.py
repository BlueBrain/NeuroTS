import numpy as np


def sample(data, size=None):
    """Returns a value according to the input data"""
    return np.random.choice(data, size=size)


def section_points(beg, end, secID=0):
    """Returns all the point IDs within
       a selected section.
    """
    return np.arange(beg[secID], end[secID] + 1)


def fill_sec_diameters(neuron, active_points, taper, max_diam):
    """Fills in the diameters of a section
       with an increasing tapering according
       to the biological model (taper, max_diam).
    """
    for i in reversed(active_points[:-1]):
        leng = np.linalg.norm(neuron.points[i+1, :2] - neuron.points[i, :2])

        diam_new = neuron.points[i+1, 3] + taper * leng

        if diam_new <= max_diam:
            neuron.points[i, 3] = diam_new
        else:
            neuron.points[i, 3] = neuron.points[i+1,3]


def fill_parent_diameters(neuron, chil, secID, model, status, connections):
    """Fills in the diameters of a section
       with an increasing tapering according
       to the biological model.
    """
    rall = sample(np.array(model['rall'])[np.array(model['rall']) > 0.0])
    trunk_diam = sample(model['trunk'])

    if np.alltrue(status[chil]):

        d1 = neuron.points[neuron.groups[chil[0]][0]][3]
        d2 = neuron.points[neuron.groups[chil[1]][0]][3]

        if rall is None:
            neuron.points[neuron.groups[secID + 1][0] - 1][3] = np.max([d1, d2])
        else:
            parent_d = np.power( np.power(d1, rall) + np.power(d2, rall), 1./ rall)

            if parent_d <= trunk_diam:
                neuron.points[neuron.groups[secID + 1][0] - 1][3] = parent_d
            else:
            #print secID, parent_d, d1, d2
                neuron.points[neuron.groups[secID + 1][0] - 1][3] = np.max([d1, d2])

        return True # Action completed, to remove from active sections

    else:
        return False # Action not completed, to keep in active sections


def correct_diameters(neuron, model):
    """Takes as input a neuron object,
       modifies the diameters and
       returns the new object
       Choose neurite type to diametrize
       Basals: 3
       Apicals: 4
       Axons: 2
    """
    # Groups and points need to be np.arrays
    # The following lines ensure this requirement is fulfilled.
    neuron.groups = np.array(neuron.groups)
    neuron.points = np.array(neuron.points)

    beg = neuron.groups[:, 0]
    ends = np.append(beg[1:], len(neuron.points)) -1

    connections = neuron.groups[:, 2]
    children = {i:np.where(connections == i)[0] for i in xrange(len(connections))}
    term = np.where(np.array([len(np.where(connections == i)[0]) for i in xrange(len(connections))]) == 0)[0]

    # Initialize all diameters to zero
    neuron.points[neuron.groups[0][1]:, 3] = 0.0

    # Set terminal diameters to term_diam
    for t in term:
        neuron.points[ends[t], 3] = sample(model[neuron.groups[t][1]]['term'])

    status = np.array([False for i in xrange(len(connections))])
    active = np.array([len(np.where(connections == i)[0]) for i in xrange(len(connections))]) == 0

    while len(np.where(active)[0]) > 1:
        to_process = list(np.where(active)[0])

        for a in to_process:
            chil = children[a]
            tree_type = neuron.groups[a][1]

            if tree_type in [2,3,4]:
                # Assign a new diameter to the last point if section is not soma
                if len(chil) > 0:
                # Assign a new diameter to the last point if section is not terminal
                    state = fill_parent_diameters(neuron, chil, a, model[tree_type], status, connections)
                    if connections[a] != -1:
                        maxD = sample(model[tree_type]['trunk'])
                        tapering = sample(np.array(model[tree_type]['taper'])[np.array(model[tree_type]['taper']) > 0.0])
                    elif connections[a] == -1:
                        maxD = sample(model[tree_type]['trunk'])
                        tapering = sample(np.array(model[tree_type]['trunk_taper'])[np.array(model[tree_type]['trunk_taper']) > 0.0])
                elif len(chil)==0:
                # Assign a new diameter to the last point if section is terminal
                    state = True
                    maxD = sample(model[tree_type]['term_max_diam'])
                    tapering = sample(np.array(model[tree_type]['term_taper'])[np.array(model[tree_type]['term_taper']) > 0.0])

                # Fill in the section with new diameters, only when all children are processed.
                if state:
                    # Find all points in section
                    active_points = section_points(beg, ends, a)

                    # Taper within a section
                    fill_sec_diameters(neuron, active_points, tapering, maxD)

                    # Deactivate current section
                    active[a] = False
                    # Activate parent section
                    active[connections[a]] = True
                    # Set status to filled
                    status[a] = True
