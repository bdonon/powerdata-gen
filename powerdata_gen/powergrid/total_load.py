# -*- coding: utf-8 -*-
"""Samples total active load."""

import numpy as np
from omegaconf import DictConfig
from pandapower import pandapowerNet


def sample_total_load(net: pandapowerNet, cfg: DictConfig) -> float:
    """Samples a new value for the total load."""

    function_dict = {
        "constant": sample_constant, "uniform_factor": sample_uniform_factor, "normal_factor": sample_normal_factor,
        "uniform_values": sample_uniform_values, "normal_values": sample_normal_values}

    if cfg.method in function_dict:
        return function_dict[cfg.method](net, **cfg.params)
    else:
        raise ValueError("{} is not a valid total load sampling method".format(cfg.method) + ", choose from {}".format(
            list(function_dict.keys())))


def sample_constant(net: pandapowerNet) -> float:
    """Returns the initial total load."""
    return (net.load.p_mw * net.load.in_service).sum()


def sample_uniform_factor(net: pandapowerNet, min_val: float = 1., max_val: float = 1.) -> float:
    """Returns the initial total load multiplied by a factor sampled uniformly."""
    default_total_load = (net.load.p_mw * net.load.in_service).sum()
    return default_total_load * np.random.uniform(min_val, max_val)


def sample_normal_factor(net: pandapowerNet, mean: float = 1., std: float = 0.) -> float:
    """Returns the initial total load multiplied by a factor sampled from a Normal distribution."""
    default_total_load = (net.load.p_mw * net.load.in_service).sum()
    return default_total_load * np.random.normal(mean, std)


def sample_uniform_values(_, min_val: float = 1., max_val: float = 1.) -> float:
    """Returns a uniformly sampled total load."""
    return np.random.uniform(min_val, max_val)


def sample_normal_values(_, mean: float = 1., std: float = 0.) -> float:
    """Ret a total load from a Normal distribution."""
    return np.random.normal(mean, std)
