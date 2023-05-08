# -*- coding: utf-8 -*-
"""Samples reactive loads."""

import numpy as np
from omegaconf import DictConfig
from pandapower import pandapowerNet


def sample_reactive_load(net: pandapowerNet, default_net: pandapowerNet, cfg: DictConfig) -> None:
    """Samples reactive loads based on those found in default_net."""

    function_dict = {
        "constant": sample_constant, "constant_pq_ratio": sample_constant_pq_ratio,
        "uniform_homothetic_factor": sample_uniform_homothetic_factor,
        "normal_homothetic_factor": sample_normal_homothetic_factor,
        "uniform_independent_factor": sample_uniform_independent_factor,
        "normal_independent_factor": sample_normal_independent_factor,
        "uniform_independent_values": sample_uniform_independent_values,
        "normal_independent_values": sample_normal_independent_values,
        "uniform_power_factor": sample_uniform_power_factor}

    if cfg.method in function_dict:
        function_dict[cfg.method](net, default_net, **cfg.params)
    else:
        raise ValueError(
            "{} is not a valid reactive load sampling method".format(cfg.method) + ", choose from {}".format(
                list(function_dict.keys())))


def sample_constant(*_) -> None:
    """Does nothing."""
    pass


def sample_constant_pq_ratio(net: pandapowerNet, default_net: pandapowerNet) -> None:
    """Modifies the active loads, to have the same P/Q ratio as in the default_net."""
    pq_ratio = default_net.load.p_mw / default_net.load.q_mvar
    net.load.q_mvar = net.load.p_mw / pq_ratio


def sample_uniform_homothetic_factor(net: pandapowerNet, default_net: pandapowerNet, min_val: float = 1.,
                                     max_val: float = 1.) -> None:
    """Applies a homothetic transform to default reactive loads, sampled uniformly from U([min_val, max_val])."""
    factor = np.random.uniform(min_val, max_val)
    net.load.q_mvar = factor * default_net.load.q_mvar


def sample_normal_homothetic_factor(net: pandapowerNet, default_net: pandapowerNet, mean: float = 1.,
                                    std: float = 0.) -> None:
    """Applies a homothetic transform to default reactive loads, sampled normally from N(mean; std)."""
    factor = np.random.normal(mean, std)
    net.load.q_mvar = factor * default_net.load.q_mvar


def sample_uniform_independent_factor(net: pandapowerNet, default_net: pandapowerNet, min_val: float = 1.,
                                      max_val: float = 1.) -> None:
    """Multiplies reactive loads by independent factors sampled uniformly from U([min_val, max_val])."""
    n_load = len(net.load)
    factor = np.random.uniform(min_val, max_val, size=n_load)
    net.load.q_mvar = factor * default_net.load.q_mvar


def sample_normal_independent_factor(net: pandapowerNet, default_net: pandapowerNet, mean: float = 1.,
                                     std: float = 0.) -> None:
    """Multiplies reactive loads by independent factors sampled normally from N(mean, std)."""
    n_load = len(net.load)
    factor = np.random.normal(mean, std, size=n_load)
    net.load.q_mvar = factor * default_net.load.q_mvar


def sample_uniform_independent_values(net: pandapowerNet, _, min_val: float = 1., max_val: float = 1.) -> None:
    """Samples reactive loads uniformly from U([min_val, max_val])."""
    n_load = len(net.load)
    values = np.random.uniform(min_val, max_val, size=n_load)
    net.load.q_mvar = values


def sample_normal_independent_values(net: pandapowerNet, _, mean: float = 1., std: float = 0.) -> None:
    """Samples reactive loads normally from N(mean, std)."""
    n_load = len(net.load)
    values = np.random.normal(mean, std, size=n_load)
    net.load.q_mvar = values


def sample_uniform_power_factor(net: pandapowerNet, _, pf_min: float = 0.8, pf_max: float = 1.,
                                flip_prob: float = 0.1) -> None:
    """Samples a uniform power factor, and randomly flips sign.

    Follows the strategy exposed in Deep Reinforcement Learning for Electric Transmission Voltage Control
    by Brandon L. Thayer and Thomas J. Overbye.

    The power factor is drawn uniformly from [pf_min, pf_max].
    The sign has a flip_prob probability of being flipped.
    Q = sign x P x tan(arccos(power_factor))
    """
    n_load = len(net.load)
    pf = np.random.uniform(pf_min, pf_max, [n_load])
    p = net.load.p_mw.values
    sign = np.random.choice(a=[-1, 1], p=[flip_prob, 1. - flip_prob], size=[n_load])
    net.load.q_mvar = sign * p * np.tan(np.arccos(pf))
