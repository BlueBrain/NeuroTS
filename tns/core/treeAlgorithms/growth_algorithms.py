    def generate_ph_repulsion(self, ph_angles, method):
        """Generates a tree structure according to the persistent diagram ph_angles.
        The synthesized structure is saved in the neuron object.
        """
        bif, term, angles, bt_all = handle_distributions.init_ph_angles(ph_angles)
        #print bt_all

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
                    dir1 = Sec.direction
                    phi, theta = rotation.spherical_from_vector(Sec.direction)
                    dir2 = rotation.vector_from_spherical(phi - np.pi/2., theta - np.pi * np.random.random())
                    #dir1, dir2 = rd.get_bif_bio_oriented(Sec.direction, angles=ang)
                    process1 = Sec.process
                    process2 = Sec.process

                else:
                    dir1, dir2 = rd.get_bif_soma_repulsion(Sec.direction, angles=ang,
                                                           soma=self.point, curr_point=start_point)
                    #dir1, dir2 = rd.get_bif_symmetric(Sec.direction, angles=ang)
                    process1 = 'tuft'
                    process2 = 'tuft'

                stop["bif_term"]["term"] = round_num(Sec.stop_criteria["bif_term"]["term"])

                self.add_section(self.neuron, act, dir1, start_point,
                                 stop, process=process1)
                active.append(len(self.neuron.sections) - 1)

                stop["bif_term"]["term"] = round_num(bt_all[Sec.stop_criteria["bif_term"]["bif"]])

                self.add_section(self.neuron, act, dir2, start_point,
                                 stop, process=process1)
                active.append(len(self.neuron.sections) - 1)

            elif state == 'terminate':
                term.remove(Sec.stop_criteria["bif_term"]["term"])



    def generate_galton_watson(self, ph_angles, method):
        """Generates a tree structure according to the persistent diagram ph_angles.
        The synthesized structure is saved in the neuron object.
        """
        from basic import neurite_types

        bif, term, angles, bt_all = handle_distributions.init_ph_angles(ph_angles)

        bif = [round_num(i) for i in self.neuron.input_distributions[neurite_types[self.type]]['bif_density']['data']]
        term = [round_num(i) for i in self.neuron.input_distributions[neurite_types[self.type]]['term_density']['data']]

        angles.pop(0)

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.first_section(neuron, len(ph_angles), stop)

        active = [len(neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = neuron.sections[act]
            self.save_section_group_in_neuron(neuron, Sec)

            Sec.stop_criteria["bif_term"]["bif"] = round_num(bif[0]) if len(bif)>0 else np.inf
            Sec.stop_criteria["bif_term"]["term"] = round_num(term[0]) if len(term)>0 else np.inf              

            state = Sec.generate()
            self.save_section_points_in_neuron(neuron, Sec)

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])
                ang = angles[np.random.choice(angles.keys())]
                dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)
                start_point = np.array(Sec.points3D[-1])

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
        from basic import neurite_types

        bif, term, angles, bt_all = handle_distributions.init_ph_angles(ph_angles)

        bif = [round_num(i) for i in neuron.input_distributions[neurite_types[self.type]]['bif_density']['data']]
        term = [round_num(i) for i in neuron.input_distributions[neurite_types[self.type]]['term_density']['data']]

        angles.pop(0)

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.first_section(neuron, len(ph_angles), stop, process='major')

        active = [len(neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = neuron.sections[act]
            self.save_section_group_in_neuron(neuron, Sec)

            Sec.stop_criteria["bif_term"]["bif"] = round_num(bif[0]) if len(bif)>0 else np.inf
            Sec.stop_criteria["bif_term"]["term"] = round_num(term[0]) if len(term)>0 else np.inf              

            state = Sec.generate()
            self.save_section_points_in_neuron(neuron, Sec)

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])
                ang = angles[np.random.choice(angles.keys())]
                dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)
                start_point = np.array(Sec.points3D[-1])
                dist = np.linalg.norm(np.subtract(Sec.points3D[-1], self.point))

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
        bif, term, angles, bt_all = handle_distributions.init_ph_angles(ph_angles)

        # remove the undefined None angles
        angles.pop(0)
        #print bt_all
        #print angles

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.first_section(neuron, len(ph_angles), stop)

        active = [len(neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = neuron.sections[act]
            self.save_section_group_in_neuron(neuron, Sec)

            Sec.stop_criteria["bif_term"]["bif"] = round_num(np.random.choice(bif)) if bif else np.inf

            if Sec.stop_criteria["bif_term"]["term"] not in term:
                Sec.stop_criteria["bif_term"]["term"] = round_num(np.random.choice(term)) if term else np.inf

            state = Sec.generate()
            self.save_section_points_in_neuron(neuron, Sec)

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])
                ang = angles.values()[np.random.choice(xrange(len(angles.values()[:-1])))] #TODO: randomize this one
                dir1, dir2 = getattr(rd, 'get_bif_' + method)(Sec.direction, angles=ang)
                start_point = np.array(Sec.points3D[-1])

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
        bif, term, angles, bt_all = handle_distributions.init_ph_angles(ph_angles)
        #print bt_all

        angles.pop(0)

        stop = {"bif_term": {"ref": self.point[:3],
                             "bif": bif[0],
                             "term": term[-1]}}

        self.first_section(neuron, len(ph_angles), stop, process='major')

        active = [len(neuron.sections) - 1]

        while active:

            active.sort(reverse=True)

            act = active.pop()

            Sec = neuron.sections[act]
            self.save_section_group_in_neuron(neuron, Sec)

            Sec.stop_criteria["bif_term"]["bif"] = round_num(np.random.choice(bif)) if bif else np.inf

            if Sec.stop_criteria["bif_term"]["term"] not in term:
                Sec.stop_criteria["bif_term"]["term"] = round_num(np.random.choice(term)) if term else np.inf

            state = Sec.generate()
            self.save_section_points_in_neuron(neuron, Sec)

            if state == 'bifurcate':

                bif.remove(Sec.stop_criteria["bif_term"]["bif"])
                ang = angles.values()[np.random.choice(xrange(len(angles.values())))]
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
