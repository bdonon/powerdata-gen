# -*- coding: utf-8 -*-
"""Samples a power grid."""

import copy

from omegaconf import DictConfig
from pandapower import pandapowerNet

from .active_generation import sample_active_generation
from .active_load import sample_active_load
from .reactive_load import sample_reactive_load
from .topology import sample_topology
from .total_load import sample_total_load
from .voltage_setpoint import sample_voltage_setpoint


def sample_power_grid(default_net: pandapowerNet, sampling_cfg: DictConfig) -> pandapowerNet:
    """Samples a single power grid instance."""

    net = copy.deepcopy(default_net)
    sample_topology(net, sampling_cfg.topology)
    total_load = sample_total_load(net, sampling_cfg.total_load)
    sample_active_load(net, default_net, total_load, sampling_cfg.active_load)
    sample_reactive_load(net, default_net, sampling_cfg.reactive_load)
    sample_active_generation(net, default_net, total_load, sampling_cfg.active_gen)
    sample_voltage_setpoint(net, default_net, sampling_cfg.voltage_setpoint)
    return net
