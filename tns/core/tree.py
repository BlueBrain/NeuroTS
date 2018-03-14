'''
TNS class : Tree
'''
import numpy as np
from tns.morphmath import random_tree as rd
import section
import copy
from tns.morphmath import rotation

def round_num(num, decimal_places=4):
    """Rounds a number to the selected num of decimal places
    This allows consistency throughout the method and avoids
    numerical artifacts"""
    return np.round(num, decimal_places)

all_types = {2:'axon',
             3:'basal',
             4:'apical'}


class TreeGrower(object):
    """Tree class"""
    def __init__(self,
                 initial_direction,
                 initial_point,
                 parameters):
        """TNS Tree Object

        Parameters:
            neuron: Obj neuron where groups and points are stored
            initial_direction: 3D vector or random
            initial_point:  the root of the tree
            radius: assuming that the radius is constant for now.
            tree_type: an integer indicating the type of the tree (choose from 2, 3, 4, 5)
        """
        if len(initial_direction) == 3:
            self.direction = initial_direction
        elif initial_direction == "random":
            self.direction = rd.get_random_point()

        self.point = list(initial_point)
        self.radius = parameters["radius"]
        self.type = parameters["tree_type"] # 2: axon, 3: basal, 4: apical, 5: other
        self.randomness = parameters["randomness"]
        self.targeting = parameters["targeting"]
        self.apical_dist = parameters["apical_distance"]


    def initialization(self, ph_angles):
        """Decomposes the information needed for the growth
        from ph_angles
        """
        bif = [round_num(i) for i in np.unique(np.array(ph_angles)[:, 1])[1:]] # bif[0] = 0 trivial.
        term = [round_num(i) for i in np.array(ph_angles)[:, 0]]
        angles = {round_num(p[1]): [p[2], p[3], p[4], p[5]] for p in ph_angles}
        bt_all = {round_num(p[1]): p[0] for p in ph_angles}

        return bif, term, angles, bt_all


    def initial_section(self, neuron, ph_angles, stop, process=None):
        """Creates the first section of the tree in the neuron
        extracting all the required information.
        """
        parent = 0 # The first point of the tree is always connected to the soma.
        n_sec = len(ph_angles)
        lpoint = list(self.point)

        neuron.sections.append(section.SectionGrower(neuron,
                                                     parent=parent,
                                                     start_point=np.array(lpoint + [self.radius]),
                                                     direction=self.direction,
                                                     randomness=self.randomness,
                                                     targeting=self.targeting,
                                                     children=0 if n_sec > 1 else 1,
                                                     process=process,
                                                     stop_criteria=copy.deepcopy(stop)))


    def add_section(self, neuron, act, dir1, start_point,
                     stop, process=None):
        """Generates a section from the parent section "act"
        from all the required information. The section is
        added to the neuron.sections and activated.
        """
        neuron.sections.append(section.SectionGrower(neuron,
                                                     parent=act,
                                                     start_point=start_point,
                                                     direction=dir1,
                                                     randomness=self.randomness,
                                                     targeting=self.targeting,
                                                     children=0,
                                                     process=process,
                                                     stop_criteria=copy.deepcopy(stop)))


    def generate_trunk(self, neuron, input_distributions, sec_len=50, n_sec=1):
        """Generates a tree structure according to the input distributions.
        The synthesized structure is saved in the neuron object.
        """
        parent = 0 # The first point of the tree is always connected to the soma

        for n in xrange(n_sec):

             # Test value: TODO: sample from distribution

            neuron.groups.append(np.array([len(neuron.points), self.type, parent]))

            S = section.SectionGrower(neuron,
                                      parent=parent,
                                      start_point=np.array(self.point + [self.radius]),
                                      direction=self.direction,
                                      randomness=self.randomness,
                                      targeting=self.targeting,
                                      children=0,
                                      process=None,
                                      stop_criteria={"num_seg":sec_len})

            S.generate_nseg()


    def generate_binary(self, neuron, input_distributions, generations=4):
        """Generates a tree structure according to the input distributions.
        The synthesized structure is saved in the neuron object.
        """
        parent = 0 # The first point of the tree is always connected to the soma.
        nsec = np.power(2, generations) - 1
        sec_len = 50

        for n in xrange(n_sec):

            neuron.groups.append(np.array([len(neuron.points), self.type, parent]))

            S = section.SectionGrower(neuron,
                                      parent=parent,
                                      start_point=np.array(self.point + [self.radius]),
                                      direction=self.direction,
                                      randomness=self.randomness,
                                      targeting=self.targeting,
                                      children=0,
                                      process=None,
                                      stop_criteria={"num_seg":sec_len})

            S.generate_nseg()


    def generate_ph_angles(self, neuron, ph_angles, method):
        """Generates a tree structure according to the persistent diagram ph_angles.
        The synthesized structure is saved in the neuron object.
        """
        bif, term, angles, bt_all = self.initialization(ph_angles)
        #print bt_all

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.initial_section(neuron, ph_angles, stop)

        active = [len(neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = neuron.sections[act]

            neuron.groups.append(np.array([len(neuron.points), self.type, Sec.parent]))

            Sec.stop_criteria["bif_term"]["bif"] = round_num(bif[0]) if bif else np.inf

            if Sec.stop_criteria["bif_term"]["term"] not in term:
                Sec.stop_criteria["bif_term"]["term"] = round_num(term[0]) if term else np.inf

            state = Sec.generate()

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])

                ang = angles[Sec.stop_criteria["bif_term"]["bif"]]

                dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)

                start_point = np.array(list(Sec.points[-1]) + [self.radius])

                stop["bif_term"]["term"] = round_num(Sec.stop_criteria["bif_term"]["term"])

                self.add_section(neuron, act, dir1, start_point,
                                 stop, process=Sec.process)

                active.append(len(neuron.sections) - 1)

                stop["bif_term"]["term"] = round_num(bt_all[Sec.stop_criteria["bif_term"]["bif"]])

                self.add_section(neuron, act, dir2, start_point,
                                 stop, process=Sec.process)

                active.append(len(neuron.sections) - 1)

            elif state == 'terminate':
                term.remove(Sec.stop_criteria["bif_term"]["term"])


    def generate_ph_apical(self, neuron, ph_angles, method):
        """Generates a tree structure according to the persistent diagram ph_angles.
        The synthesized structure is saved in the neuron object.
        """
        bif, term, angles, bt_all = self.initialization(ph_angles)
        #print bif, term, angles, bt_all
        #print bt_all

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.initial_section(neuron, ph_angles, stop, process='major')

        active = [len(neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = neuron.sections[act]

            neuron.groups.append(np.array([len(neuron.points), self.type, Sec.parent]))

            Sec.stop_criteria["bif_term"]["bif"] = round_num(bif[0]) if bif else np.inf

            if Sec.stop_criteria["bif_term"]["term"] not in term:
                Sec.stop_criteria["bif_term"]["term"] = round_num(term[0]) if term else np.inf

            state = Sec.generate()

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])

                ang = angles[Sec.stop_criteria["bif_term"]["bif"]]

                start_point = np.array(list(Sec.points[-1]) + [self.radius])

                dist = np.linalg.norm(np.subtract(Sec.points[-1], self.point))

                if Sec.process == 'major' and dist <= self.apical_dist:
                    dir1, dir2 = rd.get_bif_directional(Sec.direction, angles=ang)
                    process1 = 'major'
                    process2 = 'oblique'

                elif Sec.process == 'oblique' or Sec.process == 'tuft':
                    dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)
                    #dir1, dir2 = rd.get_bif_bio_oriented(Sec.direction, angles=ang)
                    process1 = Sec.process
                    process2 = Sec.process

                else:
                    dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)
                    #dir1, dir2 = rd.get_bif_symmetric(Sec.direction, angles=ang)
                    process1 = 'tuft'
                    process2 = 'tuft'

                stop["bif_term"]["term"] = round_num(Sec.stop_criteria["bif_term"]["term"])

                self.add_section(neuron, act, dir1, start_point,
                                 stop, process=process1)

                active.append(len(neuron.sections) - 1)

                stop["bif_term"]["term"] = round_num(bt_all[Sec.stop_criteria["bif_term"]["bif"]])

                self.add_section(neuron, act, dir2, start_point,
                                 stop, process=process1)

                active.append(len(neuron.sections) - 1)

            elif state == 'terminate':
                term.remove(Sec.stop_criteria["bif_term"]["term"])


    def generate_ph_repulsion(self, neuron, ph_angles, method):
        """Generates a tree structure according to the persistent diagram ph_angles.
        The synthesized structure is saved in the neuron object.
        """
        bif, term, angles, bt_all = self.initialization(ph_angles)
        #print bt_all

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.initial_section(neuron, ph_angles, stop, process='major')

        active = [len(neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = neuron.sections[act]

            neuron.groups.append(np.array([len(neuron.points), self.type, Sec.parent]))

            Sec.stop_criteria["bif_term"]["bif"] = round_num(bif[0]) if bif else np.inf

            if Sec.stop_criteria["bif_term"]["term"] not in term:
                Sec.stop_criteria["bif_term"]["term"] = round_num(term[0]) if term else np.inf

            state = Sec.generate()

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])

                ang = angles[Sec.stop_criteria["bif_term"]["bif"]]

                start_point = np.array(list(Sec.points[-1]) + [self.radius])

                dist = np.linalg.norm(np.subtract(Sec.points[-1], self.point))

                if Sec.process == 'major' and dist <= self.apical_dist:
                    dir1, dir2 = rd.get_bif_directional(Sec.direction, angles=ang)
                    process1 = 'major'
                    process2 = 'oblique'

                elif Sec.process == 'oblique' or Sec.process == 'tuft':
                    dir1 = Sec.direction
                    phi, theta = rotation.spherical_from_vector(Sec.direction)
                    dir2 = rotation.vector_from_spherical(phi - np.pi/2., theta - np.pi * np.random.random())
                    #dir1, dir2 = rd.get_bif_bio_oriented(Sec.direction, angles=ang)
                    process1 = Sec.process
                    process2 = Sec.process

                else:
                    dir1, dir2 = rd.get_bif_soma_repulsion(Sec.direction, angles=ang,
                                                           soma=self.point, curr_point=start_point[:-1])
                    #dir1, dir2 = rd.get_bif_symmetric(Sec.direction, angles=ang)
                    process1 = 'tuft'
                    process2 = 'tuft'

                stop["bif_term"]["term"] = round_num(Sec.stop_criteria["bif_term"]["term"])

                self.add_section(neuron, act, dir1, start_point,
                                 stop, process=process1)

                active.append(len(neuron.sections) - 1)

                stop["bif_term"]["term"] = round_num(bt_all[Sec.stop_criteria["bif_term"]["bif"]])

                self.add_section(neuron, act, dir2, start_point,
                                 stop, process=process1)

                active.append(len(neuron.sections) - 1)

            elif state == 'terminate':
                term.remove(Sec.stop_criteria["bif_term"]["term"])



    def generate_galton_watson(self, neuron, ph_angles, method):
        """Generates a tree structure according to the persistent diagram ph_angles.
        The synthesized structure is saved in the neuron object.
        """
        bif, term, angles, bt_all = self.initialization(ph_angles)

        bif = [round_num(i) for i in neuron.input_distributions[all_types[self.type]]['bif_density']['data']]
        term = [round_num(i) for i in neuron.input_distributions[all_types[self.type]]['term_density']['data']]

        angles.pop(0)

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.initial_section(neuron, ph_angles, stop)

        active = [len(neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = neuron.sections[act]

            neuron.groups.append(np.array([len(neuron.points), self.type, Sec.parent]))

            Sec.stop_criteria["bif_term"]["bif"] = round_num(bif[0]) if len(bif)>0 else np.inf
            Sec.stop_criteria["bif_term"]["term"] = round_num(term[0]) if len(term)>0 else np.inf              

            state = Sec.generate()

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])

                ang = angles[np.random.choice(angles.keys())]
                
                dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)

                start_point = np.array(list(Sec.points[-1]) + [self.radius])

                self.add_section(neuron, act, dir1, start_point,
                                 stop, process=Sec.process)

                active.append(len(neuron.sections) - 1)

                self.add_section(neuron, act, dir2, start_point,
                                 stop, process=Sec.process)

                active.append(len(neuron.sections) - 1)

            elif state == 'terminate':
                term.remove(Sec.stop_criteria["bif_term"]["term"])



    def generate_galton_watson_apical(self, neuron, ph_angles, method):
        """Generates a tree structure according to the persistent diagram ph_angles.
        The synthesized structure is saved in the neuron object.
        """
        bif, term, angles, bt_all = self.initialization(ph_angles)

        bif = [round_num(i) for i in neuron.input_distributions[all_types[self.type]]['bif_density']['data']]
        term = [round_num(i) for i in neuron.input_distributions[all_types[self.type]]['term_density']['data']]

        angles.pop(0)

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.initial_section(neuron, ph_angles, stop, process='major')

        active = [len(neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = neuron.sections[act]

            neuron.groups.append(np.array([len(neuron.points), self.type, Sec.parent]))

            Sec.stop_criteria["bif_term"]["bif"] = round_num(bif[0]) if len(bif)>0 else np.inf
            Sec.stop_criteria["bif_term"]["term"] = round_num(term[0]) if len(term)>0 else np.inf              

            state = Sec.generate()

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])

                ang = angles[np.random.choice(angles.keys())]
                
                dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)

                start_point = np.array(list(Sec.points[-1]) + [self.radius])

                dist = np.linalg.norm(np.subtract(Sec.points[-1], self.point))

                if Sec.process == 'major' and dist <= self.apical_dist:
                    dir1, dir2 = rd.get_bif_directional(Sec.direction, angles=ang)
                    process1 = 'major'
                    process2 = 'oblique'

                elif Sec.process == 'oblique' or Sec.process == 'tuft':
                    dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)
                    process1 = Sec.process
                    process2 = Sec.process

                else:
                    dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)
                    process1 = 'tuft'
                    process2 = 'tuft'

                self.add_section(neuron, act, dir1, start_point,
                                 stop, process=Sec.process)

                active.append(len(neuron.sections) - 1)

                self.add_section(neuron, act, dir2, start_point,
                                 stop, process=Sec.process)

                active.append(len(neuron.sections) - 1)

            elif state == 'terminate':
                term.remove(Sec.stop_criteria["bif_term"]["term"])



    def generate_random_angles(self, neuron, ph_angles, method):
        """Generates a tree structure according to the bifurcation/termination probabilities.
        The synthesized structure is saved in the neuron object.
        """
        bif, term, angles, bt_all = self.initialization(ph_angles)

        # remove the undefined None angles
        angles.pop(0)
        #print bt_all
        #print angles

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.initial_section(neuron, ph_angles, stop)

        active = [len(neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = neuron.sections[act]

            neuron.groups.append(np.array([len(neuron.points), self.type, Sec.parent]))

            Sec.stop_criteria["bif_term"]["bif"] = round_num(np.random.choice(bif)) if bif else np.inf

            if Sec.stop_criteria["bif_term"]["term"] not in term:
                Sec.stop_criteria["bif_term"]["term"] = round_num(np.random.choice(term)) if term else np.inf

            state = Sec.generate()

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])
                
                ang = angles.values()[np.random.choice(xrange(len(angles.values()[:-1])))] #TODO: randomize this one

                dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)

                start_point = np.array(list(Sec.points[-1]) + [self.radius])

                stop["bif_term"]["term"] = round_num(np.random.choice(term)) if term else np.inf

                self.add_section(neuron, act, dir1, start_point,
                                 stop, process=Sec.process)

                active.append(len(neuron.sections) - 1)

                stop["bif_term"]["term"] = round_num(np.random.choice(bif)) if bif else np.inf

                self.add_section(neuron, act, dir2, start_point,
                                 stop, process=Sec.process)

                active.append(len(neuron.sections) - 1)

            elif state == 'terminate':
                term.remove(Sec.stop_criteria["bif_term"]["term"])


    def generate_random_apical(self, neuron, ph_angles, method):
        """Generates a tree structure according to the persistent diagram ph_angles.
        The synthesized structure is saved in the neuron object.
        """
        bif, term, angles, bt_all = self.initialization(ph_angles)
        #print bt_all

        angles.pop(0)

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.initial_section(neuron, ph_angles, stop, process='major')

        active = [len(neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = neuron.sections[act]

            neuron.groups.append(np.array([len(neuron.points), self.type, Sec.parent]))

            Sec.stop_criteria["bif_term"]["bif"] = round_num(np.random.choice(bif)) if bif else np.inf

            if Sec.stop_criteria["bif_term"]["term"] not in term:
                Sec.stop_criteria["bif_term"]["term"] = round_num(np.random.choice(term)) if term else np.inf

            state = Sec.generate()

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])

                ang = angles.values()[np.random.choice(xrange(len(angles.values())))]

                start_point = np.array(list(Sec.points[-1]) + [self.radius])

                dist = np.linalg.norm(np.subtract(Sec.points[-1], self.point))

                if Sec.process == 'major' and dist <= self.apical_dist:
                    dir1, dir2 = rd.get_bif_directional(Sec.direction, angles=ang)
                    process1 = 'major'
                    process2 = 'oblique'

                elif Sec.process == 'oblique' or Sec.process == 'tuft':
                    dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)
                    #dir1, dir2 = rd.get_bif_bio_oriented(Sec.direction, angles=ang)
                    process1 = Sec.process
                    process2 = Sec.process

                else:
                    dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)
                    #dir1, dir2 = rd.get_bif_symmetric(Sec.direction, angles=ang)
                    process1 = 'tuft'
                    process2 = 'tuft'

                stop["bif_term"]["term"] = round_num(np.random.choice(term)) if term else np.inf

                self.add_section(neuron, act, dir1, start_point,
                                 stop, process=process1)

                active.append(len(neuron.sections) - 1)

                stop["bif_term"]["term"] = round_num(np.random.choice(bif)) if bif else np.inf

                self.add_section(neuron, act, dir2, start_point,
                                 stop, process=process1)

                active.append(len(neuron.sections) - 1)

            elif state == 'terminate':
                term.remove(Sec.stop_criteria["bif_term"]["term"])
