'''
TNS section grower class.
'''

from collections import deque
import numpy as np
from numpy.linalg import norm as vectorial_norm  # vectorial_norm used for array of vectors
from tns.morphmath.utils import get_random_point, norm  # norm used for single vectors

MEMORY = 5

# Memory decreases with distance from current point
WEIGHTS = np.exp(np.arange(1, MEMORY + 1) - MEMORY)


class SectionGrower(object):
    '''Class for the section growth
    '''
    # pylint: disable-msg=too-many-arguments
    def __init__(self, parent, children, first_point, direction, parameters,
                 process, stop_criteria, step_size_distribution, pathlength, context=None):
        '''A section is a list of points in 4D space (x, y, x, r)
        that are sequentially connected to each other. This process
        generates a tubular morphology that resembles a random walk.
        '''
        self.parent = parent
        assert not np.isclose(vectorial_norm(direction), 0.0), 'Nan direction not recognized'
        self.direction = direction / vectorial_norm(direction)
        self.children = children
        self.points = [np.array(first_point[:3])]

        self.params = parameters

        self.stop_criteria = stop_criteria
        self.process = process
        self.latest_directions = deque(maxlen=MEMORY)
        self.context = context
        self.step_size_distribution = step_size_distribution
        self.pathlength = 0 if parent is None else pathlength

    @property
    def last_point(self):
        '''Returns the last point of the section'''
        return self.points[-1]

    def update_pathlength(self, length):
        '''Increases the path distance'''
        self.pathlength += length

    def next_point(self, current_point):
        """Returns the next point depending
        on the growth method and the previous point.
        """
        direction = self.params.targeting * self.direction + \
            self.params.randomness * get_random_point() + \
            self.params.history * self.history()

        direction = direction / vectorial_norm(direction)
        seg_length = self.step_size_distribution.draw_positive()
        next_point = current_point + seg_length * direction
        self.update_pathlength(seg_length)
        return next_point, direction

    def first_point(self):
        """Generates the first point of the section, depending
        on the growth method and the previous point. This gives
        flexibility to implement a specific computation for the
        first point, and ensures the section has at least one point.
        Warning! The growth process cannot terminate before this point,
        as a first point will always be added to an active section.
        """
        direction = self.params.targeting * self.direction + \
            self.params.history * self.history()

        direction = direction / vectorial_norm(direction)
        seg_length = self.step_size_distribution.draw_positive()
        point = self.last_point + seg_length * direction
        self.update_pathlength(seg_length)

        self.latest_directions.append(direction)
        self.points.append(point)
        self.post_next_point()

    def check_stop(self):
        """Checks if any num_seg criteria is fullfiled.
        If it is it returns False and the growth stops.
        """
        return len(self.points) < self.stop_criteria["num_seg"]

    def history(self):
        '''Returns a combination of the sections history
        '''
        n_points = len(self.latest_directions)

        if n_points == 0:
            return np.zeros(3)

        hist = np.dot(WEIGHTS[MEMORY - n_points:], self.latest_directions)
        distance = vectorial_norm(hist)

        if not np.isclose(distance, 0.0):
            hist /= distance

        return hist

    def next(self):
        '''Creates one point and returns the next state.
           bifurcate, terminate or continue.
        '''
        curr_point = self.last_point
        point, direction = self.next_point(curr_point)
        self.latest_directions.append(direction)
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
        crit = getattr(self.stop_criteria["TMD"], which)
        lamda = self.params.scale_prob
        assert lamda > 0
        x = crit - value
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
        return norm(np.subtract(self.last_point, self.stop_criteria["TMD"].ref))


class SectionGrowerPath(SectionGrowerExponentialProba):
    '''Class for the TMD path based section growth
    '''
    def get_val(self):
        '''Returns path distance'''
        return self.pathlength
