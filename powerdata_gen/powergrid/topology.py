# -*- coding: utf-8 -*-
"""Samples power grid topology."""

import numpy as np
from omegaconf import DictConfig
from pandapower import pandapowerNet


def sample_topology(net: pandapowerNet, cfg: DictConfig) -> None:
    """Samples the power grid topology"""

    function_dict = {
        "constant": apply_constant, "random_disconnection": sample_random_disconnection}

    if cfg.method in function_dict:
        function_dict[cfg.method](net, **cfg.params)
    else:
        raise ValueError("{} is not a valid topology sampling method".format(cfg.method) + ", choose from {}".format(
            list(function_dict.keys())))


def apply_constant(*_) -> None:
    """Does nothing."""
    pass


def sample_random_disconnection(net: pandapowerNet, gen: DictConfig = None, load: DictConfig = None,
                                line: DictConfig = None) -> None:
    """Randomly disconnects generators, loads and lines."""
    if gen is not None:
        random_disconnect_devices(net.gen, **gen)
    if load is not None:
        random_disconnect_devices(net.load, **load)
    if line is not None:
        random_disconnect_devices(net.line, **line)


def random_disconnect_devices(devices: pandapowerNet, probs: DictConfig, black_list: list = None) -> None:
    """Randomly disconnect devices."""
    values = [int(v) for v in probs.keys()]
    p = [p for p in probs.values()]
    n_disconnect = np.random.choice(values, p=p)
    n_obj = len(devices)
    if black_list is None:
        black_list = []
    white_list = [i for i in range(n_obj) if i not in black_list]
    disconnected_objects = np.random.choice(white_list, size=n_disconnect, replace=False)
    devices.in_service.iloc[disconnected_objects] = False
