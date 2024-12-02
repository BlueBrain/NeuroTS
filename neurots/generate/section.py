"""NeuroTS class: Section grower."""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

from collections import deque
from functools import partial

import numpy as np
from numpy.linalg import norm as vectorial_norm  # vectorial_norm used for array of vectors

from neurots.morphmath.utils import get_random_point  # norm used for single vectors
from neurots.morphmath.utils import norm
from neurots.utils import accept_reject

MEMORY = 5
DISTANCE_MIN = 1e-8

# Memory decreases with distance from current point
WEIGHTS = np.exp(np.arange(1, MEMORY + 1) - MEMORY)

# default parameters for accept/reject
DEFAULT_MAX_TRIES = 50
DEFAULT_RANDOMNESS_INCREASE = 1.2


class SectionGrower:
    """Class for the section growth.

    A section is a list of points in 4D space (x, y, x, r) that are sequentially connected to each
    other. This process generates a tubular morphology that resembles a random walk.

    Args:
        parent (morphio.Section): The parent of the section.
        children (int): The number of children.
        first_point (list[float]): The first point of the section.
        direction (list[float]): The first point of the section.
        parameters (SectionParameters): The parameters used to grow the section.
        process (str): The process type.
        stop_criteria (dict): The stop criteria used for this section.
        step_size_distribution (Distr): The step size distribution.
        pathlength (float): The path length of the section.
        context (Any): The context used for the section.
        random_generator (numpy.random.Generator): The random number generator to use.
    """

    # pylint: disable-msg=too-many-arguments
    def __init__(
        self,
        parent,
        children,
        first_point,
        direction,
        parameters,
        process,
        stop_criteria,
        step_size_distribution,
        pathlength,
        context=None,
        random_generator=np.random,
    ):
        self.parent = parent
        self.id = None
        assert not np.isclose(vectorial_norm(direction), 0.0), "Nan direction not recognized"
        self.direction = direction / vectorial_norm(direction)
        self.children = children
        self.points = [np.array(first_point[:3])]

        self.params = parameters

        self.stop_criteria = stop_criteria
        self.process = process
        self.latest_directions = deque(maxlen=MEMORY)
        self.context = context
        self._rng = random_generator
        self.step_size_distribution = step_size_distribution
        self.pathlength = 0 if parent is None else pathlength

    @property
    def last_point(self):
        """Returns the last point of the section."""
        return self.points[-1]

    def update_pathlength(self, length):
        """Increases the path distance."""
        self.pathlength += length

    def _propose(self, extra_randomness=0, add_random_component=True):
        """Propose the direction for a next section point.

        Args:
            extra_randomness (float): artificially increase the randomness to allow for context
            add_random_component (bool): add a random component to the direction
        """
        direction = self.params.targeting * self.direction + self.params.history * self.history()
        if add_random_component or extra_randomness > 0.0:
            random_component = self.params.randomness * get_random_point(random_generator=self._rng)
            if extra_randomness > 0:  # pragma: no cover
                random_component *= extra_randomness
            direction += random_component
        return direction / vectorial_norm(direction)

    def next_point(self, add_random_component=True, extra_randomness=0):
        """Returns the next point depending on the growth method and the previous point.

        If a context is present, an accept-reject mechanism will be used to alter the next point.

        Args:
            add_random_component (bool): add a random component to the direction
            extra_randomness (float): only used without constraints
        """
        if self.context is not None and self.context.get("constraints", []):  # pragma: no cover

            def prob(*args, **kwargs):
                p = 1.0
                for constraint in self.context["constraints"]:
                    p = min(p, constraint["section_prob"](*args, **kwargs))
                return p

            max_tries = -1
            randomness_increase = -1
            for constraint in self.context["constraints"]:
                max_tries = max(
                    max_tries,
                    constraint.get("params_section", {}).get("max_tries", DEFAULT_MAX_TRIES),
                )
                randomness_increase = max(
                    randomness_increase,
                    constraint.get("params_section", {}).get(
                        "randomness_increase", DEFAULT_RANDOMNESS_INCREASE
                    ),
                )
            if max_tries < 0:
                max_tries = DEFAULT_MAX_TRIES
            if randomness_increase < 0:
                randomness_increase = DEFAULT_RANDOMNESS_INCREASE

            direction = accept_reject(
                partial(
                    self._propose,
                    add_random_component=add_random_component,
                ),
                prob,
                self._rng,
                max_tries=max_tries,
                randomness_increase=randomness_increase,
                current_point=self.last_point,
            )
        else:
            direction = self._propose(
                add_random_component=add_random_component, extra_randomness=extra_randomness
            )

        seg_length = self.step_size_distribution.draw_positive()
        next_point = self.last_point + seg_length * direction
        self.update_pathlength(seg_length)

        self.latest_directions.append(direction)
        self.points.append(next_point)
        self.post_next_point()

    def first_point(self):
        """Generates the first point of the section from the growth method and the previous point.

        This gives flexibility to implement a specific computation for the first point, and ensures
        the section has at least one point.

        .. warning::
            The growth process cannot terminate before this point, as a first point will always be
            added to an active section.
        """
        self.next_point(add_random_component=False)

    def check_stop(self):
        """Checks if any num_seg criteria is fulfilled.

        If it is, it returns False and the growth stops.
        """
        return len(self.points) < self.stop_criteria["num_seg"]

    def history(self):
        """Returns a combination of the sections history."""
        n_points = len(self.latest_directions)

        if n_points == 0:
            return np.zeros(3)

        history = np.dot(WEIGHTS[MEMORY - n_points :], self.latest_directions)

        distance = vectorial_norm(history)
        if distance > DISTANCE_MIN:
            history /= distance

        return history

    def next(self):
        """Creates one point and returns the next state: bifurcate, terminate or continue."""
        self.next_point()

        if self.check_stop():
            return "continue"

        if self.children == 0:
            return "terminate"

        return "bifurcate"

    def post_next_point(self):
        """A method to perform actions after `self.next_point()` has been called."""


class SectionGrowerExponentialProba(SectionGrower):
    """Abstract class for exponentially decreasing bifurcation and termination probabilities.

    The parameter lambda defines the slope of the exponential.
    The parameter that follows the exponential must be defined in the derived class.
    """

    def _check(self, value, which):
        crit = getattr(self.stop_criteria["TMD"], which)
        scale_prob = self.params.scale_prob
        assert scale_prob > 0
        x = crit - value
        if x < 0:
            # no need to exponentiate, the comparison below automatically resolves to `True`
            return True
        # Check if close enough to exp( distance * scale_prob)
        return self._rng.random() < np.exp(-x * scale_prob)

    def check_stop(self):
        """Probabilities of bifurcating and stopping are proportional `exp(-distance * lambda)`."""
        if len(self.points) < 2:
            return True

        val = self.get_val()

        if self._check(val, "bif"):
            self.children = 2.0
            return False

        if self._check(val, "term"):
            self.children = 0.0
            return False

        return True

    def get_val(self):
        """Placeholder for any function."""
        raise NotImplementedError("Attempt to use abstract class")


class SectionGrowerTMD(SectionGrowerExponentialProba):
    """Class for the TMD section growth."""

    def get_val(self):
        """Returns radial distance."""
        return norm(np.subtract(self.last_point, self.stop_criteria["TMD"].ref))


class SectionGrowerPath(SectionGrowerExponentialProba):
    """Class for the TMD path based section growth."""

    def get_val(self):
        """Returns path distance."""
        return self.pathlength
