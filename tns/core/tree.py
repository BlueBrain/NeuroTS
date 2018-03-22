'''
TNS class : Tree
'''
import numpy as np
from tns.morphmath import random_tree as rd
import section
import copy
from tns.morphmath import rotation
from tns.basic import round_num
from tns.process_input import handle_distributions


class TreeGrower(object):
    """Tree class"""
    def __init__(self,
                 neuron,
                 initial_direction,
                 initial_point,
                 parameters):
        """TNS Tree Object

        Parameters:
            neuron: Obj neuron where groups and points are stored
            initial_direction: 3D vector
            initial_point: 3D vector that defines the starting point of the tree
            parameters including: tree_type, radius, randomness, targeting, apical_distance
            tree_type: an integer indicating the type (choose from 2, 3, 4, 5)
        """
        self.neuron = neuron
        self.direction = initial_direction
        self.point = list(initial_point)
        self.radius = parameters["radius"]
        self.type = parameters["tree_type"] # 2: axon, 3: basal, 4: apical, 5: other
        self.randomness = parameters["randomness"]
        self.targeting = parameters["targeting"]
        self.apical_dist = parameters["apical_distance"]


    def save_section_points_in_neuron(self, section):
        '''Saves the 3D points of a section into the input neuron
        to avoid having access to the neuron from the section level.
        '''
        self.neuron.add_points_without_radius(section.points3D, self.radius)


    def save_section_group_in_neuron(self, section):
        '''Saves the group that represents a section into the input neuron
        to avoid having access to the neuron from the section level.
        The group information required are (SegmentID, Type, ParentID)
        SegmentID is defined by the len(neuron.points)
        Type is defined by self.type (2: axon, 3: basal, 4: apical, 5: other)
        ParentID is defined by the section.parent
        '''
        self.neuron.add_group([len(self.neuron.points), self.type, section.parent])


    def first_section(self, num_sec, stop, process=None):
        """Creates the first section of the tree in the neuron
        extracting all the required information.
        num_sec: the expected number of sections to be grown.
        """
        parent = 0 # The first point of the tree is always connected to the soma.
        lpoint = list(self.point)

        self.neuron.sections.append(section.SectionGrower(parent=parent,
                                                     start_point=np.array(lpoint),
                                                     direction=self.direction,
                                                     randomness=self.randomness,
                                                     targeting=self.targeting,
                                                     children=0 if num_sec > 1 else 1,
                                                     process=process,
                                                     stop_criteria=copy.deepcopy(stop)))


    def add_section(self, parent, dir1, start_point, stop, process=None):
        """Generates a section from the parent section "act"
        from all the required information. The section is
        added to the neuron.sections and activated.
        """
        self.neuron.sections.append(section.SectionGrower(parent=parent,
                                                          start_point=start_point,
                                                          direction=dir1,
                                                          randomness=self.randomness,
                                                          targeting=self.targeting,
                                                          children=0,
                                                          process=process,
                                                          stop_criteria=copy.deepcopy(stop)))


    def generate_trunk(self, input_distributions, sec_len=50):
        """Generates a single section tree structure that is saved in the neuron object.
        """
        # The first point of the tree is always connected to the soma, therefore parent = 0
        parent = 0
        self.neuron.add_group([len(self.neuron.points), self.type, parent])
        self.add_section(parent, self.direction, self.point, {"num_seg":sec_len})
        Sec.generate_nseg()
        self.save_section_points_in_neuron(Sec)


    def generate_binary(self, input_distributions, generations=4):
        """Generates a tree structure according to the input distributions.
        The synthesized structure is saved in the neuron object.
        """
        parent = 0 # The first point of the tree is always connected to the soma.
        nsec = np.power(2, generations) - 1
        sec_len = 50

        for n in xrange(nsec):
            self.neuron.add_group([len(self.neuron.points), self.type, parent])
            self.add_section(parent, self.direction, self.point, {"num_seg":sec_len})
            Sec.generate_nseg()
            self.save_section_points_in_neuron(Sec)
            parent = n/2


    def generate_ph_angles(self, ph_angles, method):
        """Generates a tree structure according to the persistent diagram ph_angles.
        The synthesized structure is saved in the neuron object.
        """
        bif, term, angles, bt_all = handle_distributions.init_ph_angles(ph_angles)

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.first_section(num_sec=len(ph_angles), stop=stop)

        active = [len(self.neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = self.neuron.sections[act]
            self.save_section_group_in_neuron(Sec)

            Sec.stop_criteria["bif_term"]["bif"] = round_num(bif[0]) if bif else np.inf

            if Sec.stop_criteria["bif_term"]["term"] not in term:
                Sec.stop_criteria["bif_term"]["term"] = round_num(term[0]) if term else np.inf

            state = Sec.generate()
            self.save_section_points_in_neuron(Sec)

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])
                ang = angles[Sec.stop_criteria["bif_term"]["bif"]]
                dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)
                start_point = np.array(Sec.points3D[-1])

                stop["bif_term"]["term"] = round_num(Sec.stop_criteria["bif_term"]["term"])

                self.add_section(act, dir1, start_point, stop, process=Sec.process)
                active.append(len(self.neuron.sections) - 1)

                stop["bif_term"]["term"] = round_num(bt_all[Sec.stop_criteria["bif_term"]["bif"]])

                self.add_section(act, dir2, start_point, stop, process=Sec.process)
                active.append(len(self.neuron.sections) - 1)

            elif state == 'terminate':
                term.remove(Sec.stop_criteria["bif_term"]["term"])


    def generate_ph_apical(self, ph_angles, method):
        """Generates a tree structure according to the persistent diagram ph_angles.
        The synthesized structure is saved in the neuron object.
        """
        bif, term, angles, bt_all = handle_distributions.init_ph_angles(ph_angles)

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.first_section(num_sec=len(ph_angles), stop=stop, process='major')

        active = [len(self.neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = self.neuron.sections[act]
            self.save_section_group_in_neuron(Sec)

            Sec.stop_criteria["bif_term"]["bif"] = round_num(bif[0]) if bif else np.inf

            if Sec.stop_criteria["bif_term"]["term"] not in term:
                Sec.stop_criteria["bif_term"]["term"] = round_num(term[0]) if term else np.inf

            state = Sec.generate()
            self.save_section_points_in_neuron(Sec)

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])
                ang = angles[Sec.stop_criteria["bif_term"]["bif"]]
                start_point = np.array(Sec.points3D[-1])
                dist = np.linalg.norm(np.subtract(Sec.points3D[-1], self.point))

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

                self.add_section(act, dir1, start_point, stop, process=process1)
                active.append(len(self.neuron.sections) - 1)

                stop["bif_term"]["term"] = round_num(bt_all[Sec.stop_criteria["bif_term"]["bif"]])

                self.add_section(act, dir2, start_point, stop, process=process1)
                active.append(len(self.neuron.sections) - 1)

            elif state == 'terminate':
                term.remove(Sec.stop_criteria["bif_term"]["term"])
