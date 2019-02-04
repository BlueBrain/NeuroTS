'''
TNS section grower class.
'''

from collections import deque

import numpy as np
from numpy.linalg import norm as vectorial_norm

from tns.morphmath.random_tree import get_random_point
from tns.morphmath.utils import norm

MEMORY = 5

# Memory decreases with distance from current point
WEIGHTS = np.exp(np.arange(1, MEMORY + 1) - MEMORY)


class SectionGrower(object):
    '''Class for the section growth
    '''

    def __init__(self, parent, children, start_point, direction,
                 randomness, targeting, process, stop_criteria):
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

        self.latest_directions.append(direction / vectorial_norm(direction))
        next_point = current_point + direction
        return next_point

    def check_stop(self):
        """Checks if any num_seg criteria is fullfiled.
        If it is it returns False and the growth stops.
        """
        return len(self.points3D) < self.stop_criteria["num_seg"]

    def history(self):
        '''Returns a combination of the sections history
        '''
        n_points = min(MEMORY, len(self.points3D) - 1)

        if n_points == 0:
            return np.zeros(3)

        hist = np.dot(WEIGHTS[MEMORY - n_points:], self.latest_directions)
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
        self.post_next_point()

        if self.check_stop():
            return 'continue'

        if self.children == 0:
            return 'terminate'

        return 'bifurcate'

    def post_next_point(self):
        '''A function that can be overriden in derived class
        to perform actions after self.next_point has been called'''


class SectionGrowerExponentialProba(SectionGrower):
    '''Abstract class where the bifurcation and termination probability
    follow a exponentially decreasing probability

    The parameter that follows the exponential must be defined in the derived class'''

    def _check(self, value, which):
        crit = self.stop_criteria["bif_term"]
        scale = self.params["scale_prob"]
        assert scale > 0
        x = crit[which] - value
        if x < 0:
            # no need to exponentiate, the comparison below automatically resolves to `True`
            return True
        else:
            return np.random.random() < np.exp(-x)

    def check_stop(self):
        '''Probabilities of bifurcating and stopping are proportional
        exp(-distance/scale)'''

        if len(self.points3D) < 2:
            return True

        val = self.get_val()

        if self._check(val, "bif"):
            self.children = 2.
            return False

        if self._check(val, "term"):
            self.children = 0.
            return False

        return True

    def get_val(self):
        '''Placeholder for any function'''
        raise NotImplementedError('Attempt to use abstract class')


class SectionGrowerTMD(SectionGrowerExponentialProba):
    '''Class for the TMD section growth
    '''
    def get_val(self):
        '''Returns radial distance'''
        return norm(np.subtract(self.points3D[-1], self.stop_criteria["bif_term"]["ref"]))


class SectionGrowerPath(SectionGrowerExponentialProba):
    '''Class for the TMD path based section growth
    '''

    def __init__(self, parent, children, start_point, direction,
                 randomness, targeting, process, stop_criteria):
        '''A section is a list of points in 4D space (x, y, x, r)
        that are sequentially connected to each other. This process
        generates a tubular morphology that resembles a random walk.
        '''
        super(SectionGrowerPath, self).__init__(parent, children, start_point, direction,
                                                randomness, targeting, process, stop_criteria)

        self.pathlength = 0 if parent is None else self.stop_criteria['bif_term']['ref']

    def get_val(self):
        '''Returns path distance'''
        return self.pathlength

    def post_next_point(self):
        '''Increases the path distance'''
        self.pathlength += norm(self.latest_directions[-1])
