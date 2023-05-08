# -*- coding: utf-8 -*-
"""Samples voltage set points."""

import numpy as np
from omegaconf import DictConfig
from pandapower import pandapowerNet


def sample_voltage_setpoint(net: pandapowerNet, default_net: pandapowerNet, cfg: DictConfig) -> None:
    """Samples voltage set points based on those found in default_net."""
    function_dict = {
        "constant": apply_constant, "uniform_homothetic_factor": sample_uniform_homothetic_factor,
        "normal_homothetic_factor": sample_normal_homothetic_factor,
        "uniform_independent_factor": sample_uniform_independent_factor,
        "normal_independent_factor": sample_normal_independent_factor,
        "uniform_independent_values": sample_uniform_independent_values,
        "normal_independent_values": sample_normal_independent_values}

    if (cfg.method in function_dict) and ('params' in cfg):
        function_dict[cfg.method](net, default_net, **cfg.params)
    elif (cfg.method in function_dict) and ('params' not in cfg):
        function_dict[cfg.method](net, default_net)
    else:
        raise ValueError(
            "{} is not a valid voltage setpoint sampling method".format(cfg.method) + ", choose from {}".format(
                list(function_dict.keys())))


def apply_constant(*_) -> None:
    """Does nothing."""
    pass


def sample_uniform_homothetic_factor(net: pandapowerNet, default_net: pandapowerNet, min_val: float = 0.,
                                     max_val: float = 1.) -> None:
    """Homothetically multiplies default voltage set points by a factor sampled from U([min_val, max_val])."""
    factor = np.random.uniform(min_val, max_val)
    net.gen.vm_pu = factor * default_net.gen.vm_pu
    net.ext_grid.vm_pu = factor * default_net.ext_grid.vm_pu


def sample_normal_homothetic_factor(net: pandapowerNet, default_net: pandapowerNet, mean: float = 1.,
                                    std: float = 0.) -> None:
    """Homothetically multiplies default voltage set points by a factor sampled from N(mean; std)."""
    factor = np.random.normal(mean, std)
    net.gen.vm_pu = factor * default_net.gen.vm_pu
    net.ext_grid.vm_pu = factor * default_net.ext_grid.vm_pu


def sample_uniform_independent_factor(net: pandapowerNet, default_net: pandapowerNet, min_val: float = 0.,
                                      max_val: float = 1.) -> None:
    """Independently multiplies default voltage set points by factors sampled uniformly from U([min_val, max_val])."""
    n_gen, n_ext_grid = len(net.gen), len(net.ext_grid)
    factor = np.random.uniform(min_val, max_val, size=n_gen + n_ext_grid)
    net.gen.vm_pu = factor[:n_gen] * default_net.gen.vm_pu
    net.ext_grid.vm_pu = factor[n_gen:] * default_net.ext_grid.vm_pu


def sample_normal_independent_factor(net: pandapowerNet, default_net: pandapowerNet, mean: float = 1.,
                                     std: float = 0.) -> None:
    """Independently multiplies default voltage set points by factors sampled normally from N(mean; std)."""
    n_gen, n_ext_grid = len(net.gen), len(net.ext_grid)
    factor = np.random.normal(mean, std, size=n_gen + n_ext_grid)
    net.gen.vm_pu = factor[:n_gen] * default_net.gen.vm_pu
    net.ext_grid.vm_pu = factor[n_gen:] * default_net.ext_grid.vm_pu


def sample_uniform_independent_values(net: pandapowerNet, _, min_val: float = 0.9, max_val: float = 1.1) -> None:
    """Samples voltage set points uniformly from U([min_val, max_val]), expressed in p.u.."""
    n_gen, n_ext_grid = len(net.gen), len(net.ext_grid)
    values = np.random.uniform(min_val, max_val, size=n_gen + n_ext_grid)
    net.gen.vm_pu = values[:n_gen]
    net.ext_grid.vm_pu = values[n_gen:]


def sample_normal_independent_values(net: pandapowerNet, _, mean: float = 1., std: float = 0.1) -> None:
    """Samples voltage set points normally from N(mean; std), expressed in p.u.."""
    n_gen, n_ext_grid = len(net.gen), len(net.ext_grid)
    values = np.random.normal(mean, std, size=n_gen + n_ext_grid)
    net.gen.vm_pu = values[:n_gen]
    net.ext_grid.vm_pu = values[n_gen:]
