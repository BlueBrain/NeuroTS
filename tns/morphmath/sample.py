'''Definition of distributions to sample from'''

import numpy as np

from scipy import stats


class Distr(object):
    '''Class of custom distributions
    '''

    def __init__(self, params):
        """Object of statistical distribution
        """
        self.type = next(iter(params.keys()))
        self.params = params[self.type]
        self.set_distribution()

    @staticmethod
    def norm(params):
        """Returns loc, scale
        as expected from scipy
        from mean, std data
        """
        return {"loc": params["mean"],
                "scale": params["std"]}

    @staticmethod
    def uniform(params):
        """Returns loc, scale
        as expected from scipy
        from min, max of a uniform
        """
        return {'loc': params['min'],
                'scale': params['max'] - params['min']}

    @staticmethod
    def expon(params):
        """Returns loc, scale
        as expected from scipy
        from mean, std data
        """
        return {"loc": params["loc"],
                "scale": 1. / params["lambda"]}

    def set_distribution(self):
        """Returns a statistical distribution
           according to input parameters
        """
        # If distribution is a statistical distribution
        if self.type != "data":
            fit = getattr(self, self.type)(self.params)
            self.distribution = getattr(stats, self.type)(**fit)
        # If distribution consists of data we reformat input
        else:
            w = np.array(self.params["weights"], dtype=np.float)
            b = self.params["bins"]
            self.distribution = {"bins": b, "weights": w / np.sum(w)}

    def draw(self):
        """Returns a sampled number"""
        if self.type == "data":
            return np.random.choice(self.distribution["bins"],
                                    p=self.distribution["weights"])

        return self.distribution.rvs()

    def draw_positive(self):
        """Returns a positive sampled number"""
        if self.type == "data":
            positives = np.where(self.distribution["bins"] > 0)
            return np.random.choice(self.distribution["bins"][positives],
                                    p=self.distribution["weights"][positives])

        val = self.distribution.rvs()
        while val <= 0:
            val = self.distribution.rvs()
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


def soma_size(distrib):
    """Returns a random soma radius
    as sampled from a distribution
    plus some constraints.
    """
    soma_d = Distr(distrib['soma']['size'])
    return soma_d.draw_positive()


def n_neurites(distrib):
    """Returns a number of neurites
    as sampled from a distribution
    plus some constraints.
    It ensures the number will be an INT.
    """
    neurites_d = Distr(distrib)
    numtrees = int(neurites_d.draw())
    return numtrees


def trunk_angles(distrib, N):
    """Returns a sequence of angles,
    depending on the number of trunks "N"
    and the input distribution.
    """
    trunks_d = Distr(distrib['trunk']['orientation_deviation'])
    angles = [trunks_d.draw() for _ in range(N - 1)]
    angles = angles + [sum(angles)]
    return angles


def azimuth_angles(distrib, N):
    """Returns a sequence of angles,
    depending on the number of trunks "N"
    and the input distribution.
    """
    trunks_d = Distr(d_transform(distrib['trunk']['azimuth'], np.cos))
    angles = [np.arccos(trunks_d.draw()) for _ in range(N)]
    return angles


def ph(phs):
    """Samples randomly a persistence diagram
    from the input distribution.
    """
    index = np.random.choice(len(phs))
    return phs[index]
