import numpy as np


class Distr(object):

    def __init__(self, params):
        """Object of statistical distribution
        """
        self.type = params.keys()[0]
        self.params = params[self.type]

    def norm(self, params):
        """Returns loc, scale
        as expected from scipy
        from mean, std data
        """
        return {"loc": params["mean"],
                "scale": params["std"]}

    def uniform(self, params):
        """Returns loc, scale
        as expected from scipy
        from min, max of a uniform
        """
        return {'loc': params['min'],
         'scale': params['max'] - params['min']}

    def expon(self, params):
        """Returns loc, scale
        as expected from scipy
        from mean, std data
        """
        return {"loc": params["loc"],
                "scale": 1./params["lambda"]}

    def sample(self):
        """Returns a value according to
        the statistical distribution
        """
        from scipy import stats

        if self.type == "data":
            w = np.array(self.params["weights"], dtype=np.float)
            b = self.params["bins"]
            return np.random.choice(b, p=w / np.sum(w))

        fit = getattr(self, self.type)(self.params)

        D = getattr(stats, self.type)(**fit)

        return D.rvs()


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
    soma_d = Distr(distrib['soma_size'])
    return soma_d.sample()


def n_neurites(distrib):
    """Returns a number of neurites
    as sampled from a distribution
    plus some constraints.
    It ensures the number will be an INT.
    """
    neurites_d = Distr(distrib)

    numtrees = int(neurites_d.sample())

    return numtrees


def trunk_angles(distrib, N):
    """Returns a sequence of angles,
    depending on the number of trunks "N"
    and the input distribution.
    """
    trunks_d = Distr(distrib['trunk_orientation_deviation'])
    angles = [ trunks_d.sample() for i in xrange(N - 1) ]
    angles = angles + [sum(angles)]
    return angles


def azimuth_angles(distrib, N):
    """Returns a sequence of angles,
    depending on the number of trunks "N"
    and the input distribution.
    """
    trunks_d = Distr(d_transform(distrib['trunk_azimuth'], np.cos))
    angles = [ np.arccos(trunks_d.sample()) for i in xrange(N) ]
    return angles


def ph(phs):
    """Samples randomly a persistence diagram
    from the input distribution.
    """
    index = np.random.choice(len(phs))
    return phs[index]


def ph_prob(prob_function, distance):
    """Returns a True / False to modify
    the current state (growing). The change
    ia assumed with an exponential probability.
    If True the current behavior will change.
    """ 
    prob_current = 1. - prob_function.cdf(distance)

    return np.random.choice([True, False],
                            p=[prob_current, 1.0 - prob_current])
