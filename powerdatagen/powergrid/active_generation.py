# -*- coding: utf-8 -*-
"""Samples active generation."""

import numpy as np
import pandapower as pp
from omegaconf import DictConfig
from pandapower import pandapowerNet

from powerdatagen.utils import SamplingException, sample_normal_simplex, sample_uniform_simplex


def sample_active_generation(net: pandapowerNet, default_net: pandapowerNet, total_load: float,
                             cfg: DictConfig) -> None:
    """Samples active gen while respecting the total load."""
    function_dict = {
        "homothetic": apply_homothetic_transform, "uniform_independent_factor": sample_uniform_independent_factor,
        "normal_independent_factor": sample_normal_independent_factor,
        "uniform_independent_values": sample_uniform_independent_values,
        "normal_independent_values": sample_normal_independent_values, "dc_opf": sample_dc_opf,
        "dc_opf_disconnect": sample_dc_opf_disconnect}

    if cfg.method in function_dict:
        function_dict[cfg.method](net, default_net, total_load, **cfg.params)
    else:
        raise ValueError(
            "{} is not a valid active generation sampling method".format(cfg.method) + ", choose from {}".format(
                list(function_dict.keys())))


def apply_homothetic_transform(net: pandapowerNet, default_net: pandapowerNet, total_load: float,
                               gen_to_load_ratio: float = 1.02) -> None:
    """Homothetically transforms active loads to respect total_load, while adjusting approximately for Joule losses."""
    active_gen = net.gen.in_service
    active_sgen = net.sgen.in_service
    net.gen.p_mw = total_load * gen_to_load_ratio * default_net.gen.p_mw.loc[active_gen] / default_net.gen.p_mw.loc[
        active_gen].sum()
    net.sgen.p_mw = total_load * gen_to_load_ratio * default_net.sgen.p_mw.loc[active_sgen] / default_net.sgen.p_mw.loc[
        active_sgen].sum()


def sample_uniform_independent_factor(net: pandapowerNet, default_net: pandapowerNet, total_load: float,
                                      gen_to_load_ratio: float = 1.02, beta: float = 1.) -> None:
    """Samples uniformly around the default active generation, while respecting the total_load and Joule losses."""
    active_gen = net.gen.in_service
    active_sgen = net.sgen.in_service
    n_gen = active_gen.sum()
    n_sgen = active_sgen.sum()
    default_total_gen = default_net.gen.p_mw.loc[active_gen].sum() + default_net.sgen.p_mw.loc[active_sgen].sum()
    total_gen = total_load * gen_to_load_ratio
    gen_default_value = (default_net.gen.p_mw.loc[active_gen]) / default_total_gen
    sgen_default_value = (default_net.sgen.p_mw.loc[active_sgen]) / default_total_gen
    factor = sample_uniform_simplex(beta=beta, size=n_gen + n_sgen, center_around_zero=True)
    net.gen.p_mw.loc[active_gen] = (factor[:n_gen] + gen_default_value) * total_gen
    net.sgen.p_mw.loc[active_sgen] = (factor[n_gen:] + sgen_default_value) * total_gen


def sample_normal_independent_factor(net: pandapowerNet, default_net: pandapowerNet, total_load: float,
                                     gen_to_load_ratio: float = 1.02, std: float = 0.) -> None:
    """Samples normally around the default active generation, while respecting the total_load and Joule losses."""
    active_gen = net.gen.in_service * (net.gen.p_mw != 0.)
    inactive_gen = ~active_gen
    active_sgen = net.sgen.in_service * (net.sgen.p_mw != 0.)
    inactive_sgen = ~active_sgen
    n_gen = active_gen.sum()
    n_sgen = active_sgen.sum()
    default_total_gen = default_net.gen.p_mw.loc[active_gen].sum() + default_net.sgen.p_mw.loc[active_sgen].sum()
    total_gen = total_load * gen_to_load_ratio
    gen_default_value = (default_net.gen.p_mw.loc[active_gen]) / default_total_gen
    sgen_default_value = (default_net.sgen.p_mw.loc[active_sgen]) / default_total_gen
    factor = sample_normal_simplex(std=std, size=n_gen + n_sgen, center_around_zero=True)
    net.gen.p_mw.loc[active_gen] = (factor[:n_gen] + gen_default_value) * total_gen
    net.gen.p_mw.loc[inactive_gen] = 0.
    net.sgen.p_mw.loc[active_sgen] = (factor[n_gen:] + sgen_default_value) * total_gen
    net.sgen.p_mw.loc[inactive_sgen] = 0.


def sample_uniform_independent_values(net: pandapowerNet, _, total_load: float, gen_to_load_ratio: float = 1.02,
                                      beta: float = 1.) -> None:
    """Samples independent active generation uniformly, while respecting total_load."""
    active_gen = net.gen.in_service
    active_sgen = net.sgen.in_service
    n_gen = active_gen.sum()
    n_sgen = active_sgen.sum()
    total_gen = total_load * gen_to_load_ratio
    factor = sample_uniform_simplex(beta=beta, size=n_gen + n_sgen)
    net.gen.p_mw.loc[active_gen] = factor[:n_gen] * total_gen
    net.sgen.p_mw.loc[active_sgen] = factor[n_gen:] * total_gen


def sample_normal_independent_values(net: pandapowerNet, _, total_load: float, gen_to_load_ratio: float = 1.02,
                                     std: float = 0.) -> None:
    """Samples independent active generation normally, while respecting total_load."""
    active_gen = net.gen.in_service
    active_sgen = net.sgen.in_service
    n_gen = active_gen.sum()
    n_sgen = active_sgen.sum()
    total_gen = total_load * gen_to_load_ratio
    factor = sample_normal_simplex(std=std, size=n_gen + n_sgen)
    net.gen.p_mw.loc[active_gen] = factor[:n_gen] * total_gen
    net.sgen.p_mw.loc[active_sgen] = factor[n_gen:] * total_gen


def sample_dc_opf(net: pandapowerNet, *_, min_cp0: float = 0., max_cp0: float = 0., min_cp1: float = 0.,
                  max_cp1: float = 0., min_cp2: float = 0., max_cp2: float = 0.) -> None:
    """Samples random costs function coefficients for generators and solves the DC-OPF for active power dispatch."""

    # Sample random cost coefficients
    net.poly_cost.cp0_eur = np.random.uniform(min_cp0, max_cp0, size=[len(net.poly_cost)])
    net.poly_cost.cp1_eur_per_mw = np.random.uniform(min_cp1, max_cp1, size=[len(net.poly_cost)])
    net.poly_cost.cp2_eur_per_mw2 = np.random.uniform(min_cp2, max_cp2, size=[len(net.poly_cost)])

    # DC OPF
    try:
        pp.rundcopp(net)
    except pp.OPFNotConverged:
        raise SamplingException

    # Store OPF results into generators
    net.gen.p_mw = net.res_gen.p_mw
    net.sgen.p_mw = net.res_sgen.p_mw


def sample_dc_opf_disconnect(net: pandapowerNet, *_, max_loading_percent: float = 85., min_cp0: float = 0.,
                             max_cp0: float = 0., min_cp1: float = 0., max_cp1: float = 0., min_cp2: float = 0.,
                             max_cp2: float = 0.) -> None:
    """Samples random linear costs for generators and solves the DC-OPF for active power dispatch."""

    # Set min_p_mw to 0.
    old_gen_min_p_mw = net.gen.min_p_mw.values
    net.gen.min_p_mw = 0.
    old_sgen_min_p_mw = net.sgen.min_p_mw.values
    net.sgen.min_p_mw = 0.

    # Sample random cost coefficients.
    net.poly_cost.cp0_eur = np.random.uniform(min_cp0, max_cp0, size=[len(net.poly_cost)])
    net.poly_cost.cp1_eur_per_mw = np.random.uniform(min_cp1, max_cp1, size=[len(net.poly_cost)])
    net.poly_cost.cp2_eur_per_mw2 = np.random.uniform(min_cp2, max_cp2, size=[len(net.poly_cost)])

    # Change branch maximum loading percent for the DC-OPF.
    net.line.max_loading_percent = max_loading_percent
    net.trafo.max_loading_percent = max_loading_percent

    # 1st OPF to decide which generators to disconnect.
    try:
        pp.rundcpp(net)
        pp.rundcopp(net)
    except pp.OPFNotConverged:
        raise SamplingException

    # Disconnect generators below their initial min_p_mw.
    gen_disconnect = net.res_gen.p_mw < old_gen_min_p_mw
    net.gen.in_service.loc[gen_disconnect] = False
    net.gen.p_mw.loc[gen_disconnect] = 0.
    sgen_disconnect = net.res_sgen.p_mw < old_sgen_min_p_mw
    net.sgen.in_service.loc[sgen_disconnect] = False
    net.sgen.p_mw.loc[sgen_disconnect] = 0.

    # Reset min_p_mw for connected generators.
    net.gen.min_p_mw = old_gen_min_p_mw
    net.sgen.min_p_mw = old_sgen_min_p_mw

    # 2nd OPF without disconnected generators.
    try:
        pp.rundcpp(net)
        pp.rundcopp(net)
    except pp.OPFNotConverged:
        raise SamplingException

    # Store OPF results into generators.
    net.gen.p_mw = net.res_gen.p_mw
    net.sgen.p_mw = net.res_sgen.p_mw

    # Reset branch maximum loading percent.
    net.line.max_loading_percent = 100.
    net.trafo.max_loading_percent = 100.
