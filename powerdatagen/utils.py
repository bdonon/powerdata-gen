# -*- coding: utf-8 -*-
"""Exception and samplers."""

import numpy as np


class SamplingException(Exception):
    """General exception for sampling issues."""
    pass


def sample_normal_simplex(std: float = 0., size: int = 2, center_around_zero: bool = False) -> np.ndarray:
    """Samples from a Normal distribution over the hyper-plane where values sum to 1.

    std = 0 implies that all values are equal to 1 / size.
    If `center_around_zero` is set to True, an offset is applied so that values sum to zero.
    """
    a = np.random.normal(0, std / size, size=size)
    r = a - np.mean(a) * np.ones(size) + 1 / size
    if center_around_zero:
        return r - 1 / size
    else:
        return r


def sample_uniform_simplex(beta: float = 1., size: int = 2, center_around_zero: bool = False) -> np.ndarray:
    """Samples uniformly from a `size`-dimensional simplex.

    beta = 0 implies that all values are equal to 1 / size,
    while beta = 1 implies a uniform sampling over `size`-dimensional simplex.
    If `center_around_zero` is set to True, an offset is applied so that values
    sum to zero.
    """
    assert (beta <= 1) and (beta >= 0)
    a = np.concatenate([[0.], np.random.uniform(0., 1., size=size - 1), [1.]])
    a = np.sort(a)[1:] - np.sort(a)[:-1]
    r = (1 - beta) / size + beta * a
    if center_around_zero:
        return r - 1 / size
    else:
        return r
