import numpy as np
from tns.morphmath import random_tree as rd
from tns.morphmath.sample import ph_prob
from scipy import stats

class SectionGrower(object):
    '''Class for the section
    '''

    def __init__(self,
                 parent,
                 children,
                 start_point,
                 direction,
                 randomness,
                 targeting,
                 process,
                 stop_criteria):
        '''A section is a list of points in 4D space (x, y, x, r)
        that are sequentially connected to each other. This process
        generates a tubular morphology that resembles a random walk.
        '''
        self.parent = parent
        self.direction = direction
        self.children = children
        self.points3D = [np.array(start_point[:3])]
        self.params = {"randomness": randomness,
                       "targeting": targeting,
                       "scale_prob": 1.0,
                       "history": 1.0 - randomness - targeting}
        self.stop_criteria = stop_criteria
        self.process = process

    def next_point(self, current_point):
        """Returns the next point depending
        on the growth method and the previous point.
        """
        random_point = rd.get_random_point()

        hist_point = self.history()

        targeting = self.params["targeting"]
        randomness = self.params["randomness"]
        hist = self.params["history"]

        new_point = list([current_point[0] +
                          targeting * self.direction[0] +
                          randomness * random_point[0] +
                          hist * hist_point[0],
                          current_point[1] +
                          targeting * self.direction[1] +
                          randomness * random_point[1] +
                          hist * hist_point[1],
                          current_point[2] +
                          targeting * self.direction[2] +
                          randomness * random_point[2] +
                          hist * hist_point[2]])

        return new_point

    def check_stop(self):
        """Checks if any num_seg criteria is fullfiled.
        If it is it returns False and the growth stops.
        """
        return len(self.points3D) < self.stop_criteria["num_seg"]

    def history(self, memory=5):
        '''Returns a combination of the sections history
        '''
        hist = np.array([0., 0., 0.])

        for i in xrange(1, min(memory, len(self.points3D))):
            hist = np.add(hist, np.exp(1. - i) * (self.points3D[-i] - self.points3D[-i - 1]))

        if np.linalg.norm(hist) != 0.0:
            return hist / np.linalg.norm(hist)
        else:
            return hist

    def next(self):
        '''Creates one point and returns the next state.
           bifurcate, terminate or continue.
        '''
        curr_point = self.points3D[-1]
        point = self.next_point(curr_point)
        self.points3D.append(np.array(point))

        if self.check_stop():
            return 'continue'
        elif self.children == 0:
            return 'terminate'
        else:
            return 'bifurcate'

    def generate(self):
        '''Creates a section with the selected parameters
           until at least one stop criterion is fulfilled.
        '''

        while self.check_stop():

            curr_point = self.points3D[-1]
            point = self.next_point(curr_point)
            self.points3D.append(np.array(point))

        if self.children == 0:
            return 'terminate'
        else:
            return 'bifurcate'

    def get_current_direction(self):
        return self.history(memory=10)


class SectionGrowerTMD(SectionGrower):
    '''Class for the section
    '''
    def __init__(self,
                 parent,
                 children,
                 start_point,
                 direction,
                 randomness,
                 targeting,
                 process,
                 stop_criteria):
        '''A section is a list of points in 4D space (x, y, x, r)
        that are sequentially connected to each other. This process
        generates a tubular morphology that resembles a random walk.
        '''
        super(SectionGrowerTMD, self).__init__(parent,
                                            children,
                                            start_point,
                                            direction,
                                            randomness,
                                            targeting,
                                            process,
                                            stop_criteria)

        self.prob_function = stats.expon(loc=0, scale=self.params["scale_prob"])

    def check_stop(self):
        """Checks if any of bif_term criteria is fullfiled.
        If False the growth stops.
        """
        crit = self.stop_criteria["bif_term"]

        currd = np.linalg.norm(np.subtract(self.points3D[-1], crit["ref"]))
        # Ensure that the section has at least two points
        if len(self.points3D) < 2:
            return True

        if ph_prob(self.prob_function, crit["bif"] - currd):
            self.children = 2.
            return False
        elif ph_prob(self.prob_function, crit["term"] - currd):
            self.children = 0.
            return False
        else:
            return True


class SectionGrowerPath(SectionGrower):
    '''Class for the section
    '''
    def __init__(self,
                 parent,
                 children,
                 start_point,
                 direction,
                 randomness,
                 targeting,
                 process,
                 stop_criteria):
        '''A section is a list of points in 4D space (x, y, x, r)
        that are sequentially connected to each other. This process
        generates a tubular morphology that resembles a random walk.
        '''
        super(SectionGrowerPath, self).__init__(parent,
                                                children,
                                                start_point,
                                                direction,
                                                randomness,
                                                targeting,
                                                process,
                                                stop_criteria)

        self.prob_function = stats.expon(loc=0, scale=self.params["scale_prob"])
        self.pathlength = 0 if parent is None else self.stop_criteria['bif_term']['ref']

    def check_stop(self):
        """Checks if any of bif_term criteria is fullfiled.
        If False the growth stops.
        """
        crit = self.stop_criteria["bif_term"]

        if len(self.points3D) < 2:
            return True
        if ph_prob(self.prob_function, crit["bif"] - self.pathlength):
            self.children = 2.
            return False
        elif ph_prob(self.prob_function, crit["term"] - self.pathlength):
            self.children = 0.
            return False
        else:
            return True

    def next(self):
        '''Creates one point and returns the next state.
           bifurcate, terminate or continue.
        '''
        curr_point = self.points3D[-1]
        point = self.next_point(curr_point)
        self.points3D.append(np.array(point))
        self.pathlength = self.pathlength + np.linalg.norm(np.subtract(curr_point, point))

        if self.check_stop():
            return 'continue'
        elif self.children == 0:
            return 'terminate'
        else:
            return 'bifurcate'

    def generate(self):
        '''Creates a section with the selected parameters
           until at least one stop criterion is fulfilled.
        '''

        while self.check_stop():
            curr_point = self.points3D[-1]
            point = self.next_point(curr_point)
            self.points3D.append(np.array(point))
            self.pathlength = self.pathlength + np.linalg.norm(np.subtract(curr_point, point))

        if self.children == 0:
            return 'terminate'
        else:
            return 'bifurcate'

