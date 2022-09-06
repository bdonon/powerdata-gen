import numpy as np


def sample_normal_simplex(param, size=2, center_around_zero=False):
    """TODO"""
    a = np.random.normal(0, param/size, size=size)
    r = a - np.mean(a)*np.ones(size) + 1/size
    if center_around_zero:
        return r - 1/size
    else:
        return r


def sample_uniform_simplex(param, size=2, center_around_zero=False):
    """Samples uniformly from a n_dim dimensional simplex TODO add details.
    param = 0 implies that loads are all equal to 1 / size, while param = 1 samples from the unit simplex"""
    # TODO assert that param is between 0 and 1.
    a = np.concatenate([[0.], np.random.uniform(0., 1., size=size - 1), [1.]])
    a = np.sort(a)[1:] - np.sort(a)[:-1]
    r = (1 - param) / size + param * a
    if center_around_zero:
        return r - 1/size
    else:
        return r
