'''Definition of distributions to sample from'''

import numpy as np


class Distr:
    '''Class of custom distributions
    '''

    def __init__(self, params, random_generator=np.random):
        """Object of statistical distribution
        """
        self.type, distr_params = next(iter(params.items()))
        self._rng = random_generator
        self.loc = 0.0
        self.scale = 1.0
        self.set_distribution(distr_params)

    @staticmethod
    def norm(params):
        """Returns loc, scale
        as expected from scipy
        from mean, std data
        """
        return "standard_normal", params["mean"], params["std"]

    @staticmethod
    def uniform(params):
        """Returns loc, scale
        as expected from scipy
        from min, max of a uniform
        """
        return "uniform", params['min'], params['max'] - params['min']

    @staticmethod
    def expon(params):
        """Returns loc, scale
        as expected from scipy
        from mean, std data
        """
        return "standard_exponential", params["loc"], 1. / params["lambda"]

    def set_distribution(self, params):
        """Returns a statistical distribution
           according to input parameters
        """
        # If distribution is a statistical distribution
        if self.type != "data":
            name, self.loc, self.scale = getattr(self, self.type)(params)
            self.distribution = getattr(self._rng, name)
        # If distribution consists of data we reformat input
        else:
            w = np.array(params["weights"], dtype=np.float)
            b = np.array(params["bins"])
            self.distribution = {"bins": b, "weights": w / np.sum(w)}

    def draw(self):
        """Returns a sampled number"""
        if self.type == "data":
            return self._rng.choice(self.distribution["bins"],
                                                p=self.distribution["weights"])

        return self.loc + self.scale * self.distribution()

    def draw_positive(self):
        """Returns a positive sampled number"""
        if self.type == "data":
            positives = np.where(self.distribution["bins"] > 0)
            return self._rng.choice(self.distribution["bins"][positives],
                                                p=self.distribution["weights"][positives])

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


def d_transform(distr, funct):
    """Transform a distribuion
    according to a selected function
    """
    transf = {}
    for k in distr.keys():
        transf[k] = {}
        for j in distr[k].keys():
            transf[k][j] = funct(distr[k][j])

    return transf


def soma_size(distrib, random_generator=np.random):
    """Returns a random soma radius
    as sampled from a distribution
    plus some constraints.
    """
    soma_d = Distr(distrib['soma']['size'], random_generator)
    return soma_d.draw_positive()


def n_neurites(distrib, random_generator=np.random):
    """Returns a number of neurites
    as sampled from a distribution
    plus some constraints.
    It ensures the number will be an INT.
    """
    neurites_d = Distr(distrib, random_generator)
    numtrees = int(neurites_d.draw())
    return numtrees


def trunk_angles(distrib, N, random_generator=np.random):
    """Returns a sequence of relative angles,
    depending on the number of trunks "N"
    and the input distribution.
    """
    trunks_d = Distr(distrib['trunk']['orientation_deviation'], random_generator)
    angles = [trunks_d.draw() for _ in range(N - 1)]
    angles = angles + [sum(angles)]
    return angles


def trunk_absolute_angles(distrib, N, random_generator=np.random):
    """Returns a sequence of absolute angles,
    depending on the number of trunks "N"
    and the input distribution.
    """
    elevation = distrib.get('trunk', {}).get('absolute_elevation_deviation', None)
    if elevation is None:
        raise KeyError(
            "No elevation distribution found in parameters['trunk']"
            "['absolute_elevation_deviation']."
        )
    trunks_d_theta = Distr(elevation, random_generator)
    return [trunks_d_theta.draw() for _ in range(N)]


def azimuth_angles(distrib, N, random_generator=np.random):
    """Returns a sequence of angles,
    depending on the number of trunks "N"
    and the input distribution.
    """
    trunks_d = Distr(d_transform(distrib['trunk']['azimuth'], np.cos), random_generator)
    angles = [np.arccos(trunks_d.draw()) for _ in range(N)]
    return angles


def ph(phs, random_generator=np.random):
    """Samples randomly a persistence diagram
    from the input distribution.
    """
    index = random_generator.choice(len(phs))
    return phs[index]
