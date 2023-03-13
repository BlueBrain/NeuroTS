"""Definition of distributions to sample from."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np


class Distr:
    """Class of custom distributions.

    Args:
        params (dict): The parameters of the distribution.
        random_generator (numpy.random.Generator): The random number generator to use.
    """

    def __init__(self, params, random_generator=np.random):
        """Object of statistical distribution."""
        self.type, distr_params = next(iter(params.items()))
        self._rng = random_generator
        self.loc = 0.0
        self.scale = 1.0
        self.set_distribution(distr_params)

    @staticmethod
    def norm(params):
        """Return loc, scale as expected from scipy from mean, std data."""
        return "standard_normal", params["mean"], params["std"]

    @staticmethod
    def uniform(params):
        """Return loc, scale as expected from scipy from min, max of a uniform."""
        return "uniform", params["min"], params["max"] - params["min"]

    @staticmethod
    def expon(params):
        """Return loc, scale as expected from scipy from mean, std data."""
        return "standard_exponential", params["loc"], 1.0 / params["lambda"]

    def set_distribution(self, params):
        """Return a statistical distribution according to input parameters."""
        # If distribution is a statistical distribution
        if self.type != "data":
            name, self.loc, self.scale = getattr(self, self.type)(params)
            self.distribution = getattr(self._rng, name)
        # If distribution consists of data we reformat input
        else:
            w = np.array(params["weights"], dtype=float)
            b = np.array(params["bins"])
            self.distribution = {"bins": b, "weights": w / np.sum(w)}

    def draw(self):
        """Return a sampled number."""
        if self.type == "data":
            return self._rng.choice(self.distribution["bins"], p=self.distribution["weights"])

        return self.loc + self.scale * self.distribution()

    def draw_positive(self):
        """Return a positive sampled number."""
        if self.type == "data":
            positives = np.where(self.distribution["bins"] > 0)
            return self._rng.choice(
                self.distribution["bins"][positives],
                p=self.distribution["weights"][positives],
            )

        if self.scale == 0:
            if self.loc >= 0:
                return self.loc
            else:
                raise ValueError(
                    "The 'loc' of the distribution must be >= 0 when 'scale' == 0 (loc == "
                    f"{self.scale})"
                )

        val = self.loc + self.scale * self.distribution()
        while val <= 0:
            val = self.loc + self.scale * self.distribution()
        return val


def d_transform(distr, funct, **kwargs):
    """Transform a distribution according to a selected function."""
    transf = {}
    for k in distr.keys():
        transf[k] = {}
        for j in distr[k].keys():
            transf[k][j] = funct(distr[k][j], **kwargs)

    return transf


def soma_size(distrib, random_generator=np.random):
    """Return a random soma radius as sampled from a distribution plus some constraints."""
    soma_d = Distr(distrib["soma"]["size"], random_generator)
    return soma_d.draw_positive()


def n_neurites(distrib, random_generator=np.random):
    """Return a number of neurites as sampled from a distribution plus some constraints.

    It ensures the number will be an INT.
    """
    neurites_d = Distr(distrib, random_generator)
    numtrees = int(neurites_d.draw())
    return numtrees


def trunk_angles(distrib, N, random_generator=np.random):
    """Return N relative angles, depending on the input distribution."""
    trunks_d = Distr(distrib["trunk"]["orientation_deviation"], random_generator)
    angles = [trunks_d.draw() for _ in range(N - 1)]
    angles = angles + [sum(angles)]
    return angles


def trunk_absolute_angles(distrib, N, random_generator=np.random):
    """Return N absolute angles, depending on the input distribution."""
    trunks_d = Distr(distrib["trunk"]["absolute_elevation_deviation"], random_generator)
    return [trunks_d.draw() for _ in range(N)]


def azimuth_angles(distrib, N, random_generator=np.random):
    """Return N azimuth angles, depending on the input distribution."""
    trunks_d = Distr(d_transform(distrib["trunk"]["azimuth"], np.cos), random_generator)
    tmp = np.array([trunks_d.draw() for _ in range(N)])
    angles = np.arccos(tmp)
    return angles


def ph(phs, random_generator=np.random):
    """Samples randomly a persistence diagram from the input distribution."""
    index = random_generator.choice(len(phs))
    return phs[index]


def sample_spherical_unit_vectors(rng):
    """Sample a point uniformly on the sphere.

    Args:
        rng: random number generator
    """
    x = rng.normal(0, 1, 3)
    return x / np.linalg.norm(x)
