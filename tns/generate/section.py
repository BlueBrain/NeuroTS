import numpy as np
from tns.morphmath.random_tree import get_random_point
from scipy import stats
from tns.morphmath.utils import norm
from numpy.linalg import norm as vectorial_norm

from collections import deque

MEMORY = 4

WEIGHTS = np.exp(-np.arange(MEMORY))


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
        self.latest_directions = deque(maxlen=MEMORY)

    def next_point(self, current_point):
        """Returns the next point depending
        on the growth method and the previous point.
        """
        direction = self.params["targeting"] * self.direction + \
                    self.params["randomness"] * get_random_point() + \
                    self.params["history"] * self.history()
        self.latest_directions.append(direction)
        return current_point + direction

    def check_stop(self):
        """Checks if any num_seg criteria is fullfiled.
        If it is it returns False and the growth stops.
        """
        return len(self.points3D) < self.stop_criteria["num_seg"]

    def history(self):
        '''Returns a combination of the sections history
        '''
        n_points = min(MEMORY, len(self.points3D)-1)

        hist = np.dot(WEIGHTS[:n_points][::-1], self.latest_directions)
        distance = vectorial_norm(hist)

        if distance > 0:
            hist /= distance
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

        if self.children == 0:
            return 'terminate'

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

        return 'bifurcate'


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
        '''A derived class of SectionGrower with a different stopping condition.
        Probabilities of bifurcating and stopping are proportional
        exp(-distance/scale)'''
        super(SectionGrowerTMD, self).__init__(parent,
                                            children,
                                            start_point,
                                            direction,
                                            randomness,
                                            targeting,
                                            process,
                                            stop_criteria)


    def check_stop(self):
        '''Probabilities of bifurcating and stopping are proportional
        exp(-distance/scale)'''

        if len(self.points3D) < 2:
            return True

        crit = self.stop_criteria["bif_term"]
        scale = self.params["scale_prob"]

        currd = norm(np.subtract(self.points3D[-1], crit["ref"]))

        if np.random.random() < np.exp(-(crit["bif"] - currd) / scale):
            self.children = 2.
            return False

        if np.random.random() < np.exp(-(crit["term"] - currd)  / scale):
            self.children = 0.
            return False

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
        '''Probabilities of bifurcating and stopping are proportional
        exp(-distance/scale)'''

        if len(self.points3D) < 2:
            return True

        crit = self.stop_criteria["bif_term"]
        scale = self.params["scale_prob"]

        if np.random.random() < np.exp(-(crit["bif"] - self.pathlength) / scale):
            self.children = 2.
            return False

        if np.random.random() < np.exp(-(crit["term"] - self.pathlength)  / scale):
            self.children = 0.
            return False

        return True

    def next(self):
        '''Creates one point and returns the next state.
           bifurcate, terminate or continue.
        '''
        curr_point = self.points3D[-1]
        point = self.next_point(curr_point)
        self.points3D.append(np.array(point))
        self.pathlength = self.pathlength + norm(np.subtract(curr_point, point))

        if self.check_stop():
            return 'continue'

        if self.children == 0:
            return 'terminate'

        return 'bifurcate'

    def generate(self):
        '''Creates a section with the selected parameters
           until at least one stop criterion is fulfilled.
        '''
        self.points3D.append(np.array(self.points3D[0]))

        while self.check_stop():
            curr_point = self.points3D[-1]
            point = self.next_point(curr_point)
            self.points3D.append(np.array(point))
            self.pathlength = self.pathlength + np.linalg.norm(np.subtract(curr_point, point))

        if self.children == 0:
            return 'terminate'

        return 'bifurcate'
