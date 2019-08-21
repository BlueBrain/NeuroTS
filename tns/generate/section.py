'''
TNS section grower class.
'''

from collections import deque
import numpy as np
from numpy.linalg import norm as vectorial_norm  # vectorial_norm used for array of vectors
from tns.morphmath.utils import get_random_point, norm  # norm used for single vectors

MEMORY = 5

LAMDA = 1.0

# Memory decreases with distance from current point
WEIGHTS = np.exp(np.arange(1, MEMORY + 1) - MEMORY)


class SectionGrower(object):
    '''Class for the section growth
    '''

    def __init__(self, parent, children, first_point, direction,
                 randomness, targeting, process, stop_criteria, context=None):
        '''A section is a list of points in 4D space (x, y, x, r)
        that are sequentially connected to each other. This process
        generates a tubular morphology that resembles a random walk.
        '''
        self.parent = parent
        assert not np.isclose(vectorial_norm(direction), 0.0), 'Nan direction not recognized'
        self.direction = direction / vectorial_norm(direction)
        self.children = children
        self.points = [np.array(first_point[:3])]
        self.params = {"randomness": randomness,
                       "targeting": targeting,
                       "scale_prob": LAMDA,
                       "history": 1.0 - randomness - targeting}
        self.stop_criteria = stop_criteria
        self.process = process
        self.latest_directions = deque(maxlen=MEMORY)
        self.latest_directions_normed = deque(maxlen=MEMORY)
        self.context = context

    def next_point(self, current_point):
        """Returns the next point depending
        on the growth method and the previous point.
        """
        direction = self.params["targeting"] * self.direction + \
            self.params["randomness"] * get_random_point() + \
            self.params["history"] * self.history()

        next_point = current_point + direction
        return next_point, direction

    def check_stop(self):
        """Checks if any num_seg criteria is fullfiled.
        If it is it returns False and the growth stops.
        """
        return len(self.points) < self.stop_criteria["num_seg"]

    def history(self):
        '''Returns a combination of the sections history
        '''
        n_points = len(self.latest_directions_normed)

        if n_points == 0:
            return np.zeros(3)

        hist = np.dot(WEIGHTS[MEMORY - n_points:], self.latest_directions_normed)
        distance = vectorial_norm(hist)

        if not np.isclose(distance, 0.0):
            hist /= distance

        return hist

    def next(self):
        '''Creates one point and returns the next state.
           bifurcate, terminate or continue.
        '''
        curr_point = self.points[-1]
        point, direction = self.next_point(curr_point)
        self.latest_directions.append(direction)
        self.latest_directions_normed.append(direction / vectorial_norm(direction))
        self.points.append(point)
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
       The parameter lamda defines the slope of the exponential.

    The parameter that follows the exponential must be defined in the derived class'''

    def _check(self, value, which):
        crit = self.stop_criteria["TMD"]
        lamda = self.params["scale_prob"]
        assert lamda > 0
        x = crit[which] - value
        if x < 0:
            # no need to exponentiate, the comparison below automatically resolves to `True`
            return True
        # Check if close enough to exp( distance * lamda)
        return np.random.random() < np.exp(-x * lamda)

    def check_stop(self):
        '''Probabilities of bifurcating and stopping are proportional
        exp(-distance * lamda)'''

        if len(self.points) < 2:
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
        return norm(np.subtract(self.points[-1], self.stop_criteria["TMD"]["ref"]))


class SectionGrowerPath(SectionGrowerExponentialProba):
    '''Class for the TMD path based section growth
    '''

    def __init__(self, parent, children, first_point, direction,
                 randomness, targeting, process, stop_criteria, context=None):
        '''A section is a list of points in 4D space (x, y, x, r)
        that are sequentially connected to each other. This process
        generates a tubular morphology that resembles a random walk.
        '''
        super(SectionGrowerPath, self).__init__(parent, children, first_point, direction,
                                                randomness, targeting, process, stop_criteria,
                                                context)

        self.pathlength = 0 if parent is None else self.stop_criteria["TMD"]['ref']

    def get_val(self):
        '''Returns path distance'''
        return self.pathlength

    def post_next_point(self):
        '''Increases the path distance'''
        self.pathlength += norm(self.latest_directions[-1])
