# -*- coding: utf-8 -*-
"""Samples active loads."""

from omegaconf import DictConfig
from pandapower import pandapowerNet

from powerdata_gen.utils import sample_normal_simplex, sample_uniform_simplex


def sample_active_load(net: pandapowerNet, default_net: pandapowerNet, total_load: float, cfg: DictConfig) -> None:
    """Samples active loads while respecting the total load."""

    function_dict = {
        "homothetic": apply_homothetic_transform, "uniform_independent_factor": sample_uniform_independent_factor,
        "normal_independent_factor": sample_normal_independent_factor,
        "uniform_independent_values": sample_uniform_independent_values,
        "normal_independent_values": sample_normal_independent_values}

    if cfg.method in function_dict:
        function_dict[cfg.method](net, default_net, total_load, **cfg.params)
    else:
        raise ValueError("{} is not a valid active load sampling method".format(cfg.method) + ", choose from {}".format(
            list(function_dict.keys())))


def apply_homothetic_transform(net: pandapowerNet, default_net: pandapowerNet, total_load: float) -> None:
    """Updates `net` by homothetically transforming active loads to respect total_load."""
    active = net.load.in_service
    factor = total_load / default_net.load.p_mw.loc[active].sum()
    net.load.p_mw.loc[active] = factor * default_net.load.p_mw.loc[active]


def sample_uniform_independent_factor(net: pandapowerNet, default_net: pandapowerNet, total_load: float,
                                      beta: float = 1.) -> None:
    """Updates `net` by sampling uniformly around the default situation, while respecting the total_load."""
    active = net.load.in_service
    n_load = active.sum()
    default_value = default_net.load.p_mw.loc[active] / default_net.load.p_mw.loc[active].sum()
    factor = sample_uniform_simplex(beta, size=n_load, center_around_zero=True)
    net.load.p_mw.loc[active] = (factor + default_value) * total_load


def sample_normal_independent_factor(net: pandapowerNet, default_net: pandapowerNet, total_load: float,
                                     std: float = 0.) -> None:
    """Updates `net` by sampling normally around the default situation, while respecting the total_load."""
    active = net.load.in_service
    n_load = active.sum()
    default_value = default_net.load.p_mw.loc[active] / default_net.load.p_mw.loc[active].sum()
    factor = sample_normal_simplex(std, size=n_load, center_around_zero=True)
    net.load.p_mw.loc[active] = (factor + default_value) * total_load


def sample_uniform_independent_values(net: pandapowerNet, _, total_load: float,
                                      beta: float = 0.) -> None:
    """Updates `net` by sampling independent loads uniformly, while respecting total_load."""
    active = net.load.in_service
    n_load = active.sum()
    factor = sample_uniform_simplex(beta, size=n_load)
    net.load.p_mw.loc[active] = total_load * factor


def sample_normal_independent_values(net: pandapowerNet, _, total_load: float,
                                     std: float = 0.) -> None:
    """Updates `net` by sampling independent loads normally, while respecting total_load."""
    active = net.load.in_service
    n_load = active.sum()
    factor = sample_normal_simplex(std, size=n_load)
    net.load.p_mw.loc[active] = total_load * factor
