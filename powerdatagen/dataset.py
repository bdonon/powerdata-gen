# -*- coding: utf-8 -*-
"""Samples power grid datasets."""

import logging
import os

import numpy as np
import pandapower as pp
import pandapower.topology as top
import tqdm
from omegaconf import DictConfig
from pandapower import pandapowerNet

from powerdatagen.powergrid.core import sample_power_grid
from powerdatagen.utils import SamplingException


def build_datasets(net_path: pandapowerNet, save_path: str, log: logging.Logger, n_train: int, n_val: int, n_test: int,
                   sampling_cfg: DictConfig, powerflow_cfg: DictConfig, filtering_cfg: DictConfig, seed=None) -> None:
    """Builds train, val and test sets."""
    if seed is not None:
        np.random.seed(seed)
    default_net = pp.from_json(net_path)
    log.info("Building the train set...")
    build_one_dataset(default_net, os.path.join(save_path, 'train'), log, n_train, sampling_cfg, powerflow_cfg,
                      filtering_cfg)
    log.info("Building the validation set...")
    build_one_dataset(default_net, os.path.join(save_path, 'val'), log, n_val, sampling_cfg, powerflow_cfg,
                      filtering_cfg)
    log.info("Building the test set...")
    build_one_dataset(default_net, os.path.join(save_path, 'test'), log, n_test, sampling_cfg, powerflow_cfg,
                      filtering_cfg)


def build_one_dataset(default_net: pandapowerNet, path: str, log: logging.Logger, n_files: int,
                      sampling_cfg: DictConfig, powerflow_cfg: DictConfig, filtering_cfg: DictConfig) -> None:
    """Builds a single dataset."""

    net = None
    os.mkdir(path)
    divergence_path = os.path.join(path, "divergence")
    os.mkdir(divergence_path)
    reject_path = os.path.join(path, "rejection")
    os.mkdir(reject_path)

    n_characters = np.ceil(np.log10(n_files)).astype(int)
    pbar = tqdm.tqdm(range(n_files))

    sample_count, sampling_error_count, divergence_count, filtering_count = 0, 0, 0, 0
    filtering_info = {}
    for i in pbar:
        success = False
        while not success:
            sample_count += 1

            # Sampling a power grid.
            try:
                net = sample_power_grid(default_net, sampling_cfg)
            except SamplingException:
                sampling_error_count += 1
                continue

            # Running a Power Flow
            try:
                pp.runpp(net, **powerflow_cfg)
            except pp.powerflow.LoadflowNotConverged:
                divergence_count += 1
                file_name = 'divergence_sample_' + str(divergence_count).rjust(n_characters, '0') + '.json'
                file_path = os.path.join(divergence_path, file_name)
                pp.to_json(net, file_path)
                continue

            # Checking the sanity of the sample.
            reject, info = filter_sample(net, **filtering_cfg)
            if reject:
                filtering_count += 1
                filtering_info = {k: filtering_info.get(k, 0) + info.get(k, 0) for k in filtering_info | info}
                file_name = 'rejection_sample_' + str(filtering_count).rjust(n_characters, '0') + '.json'
                file_path = os.path.join(reject_path, file_name)
                pp.to_json(net, file_path)
                continue

            success = True

        file_name = 'sample_' + str(i).rjust(n_characters, '0') + '.json'
        file_path = os.path.join(path, file_name)
        pp.to_json(net, file_path)

        pbar.set_description(
            "Sample count = {}, Sampling issues = {}, Divergences = {}, Rejections = {} ".format(sample_count,
                                                                                                 sampling_error_count,
                                                                                                 divergence_count,
                                                                                                 filtering_count))

    log.info("Sample count : {}".format(sample_count))
    log.info("Sampling issues : {}".format(sampling_error_count))
    log.info("Divergences : {}".format(divergence_count))
    log.info("Rejections : {}".format(filtering_count))
    for k, v in filtering_info.items():
        log.info("    {} : {}".format(k, v))


def filter_sample(net: pandapowerNet, max_loading_percent: float = None, max_count_voltage_violation: int = None,
                  allow_disconnected_bus: bool = False, allow_negative_load: bool = False,
                  allow_out_of_range_gen: bool = False) -> tuple[bool, dict]:
    """Returns a boolean that says if the considered power grid sample should be filtered out."""

    reject = False
    info = dict()

    info["overflow"] = 0
    if max_loading_percent is not None:
        loading_percent = max(net.res_trafo.loading_percent.max(), net.res_line.loading_percent.max())
        if loading_percent > max_loading_percent:
            reject = True
            info["overflow"] = 1

    info["disconnected_bus"] = 0
    if not allow_disconnected_bus:
        if top.unsupplied_buses(net):
            reject = True
            info["disconnected_bus"] = 1

    info["negative_load"] = 0
    if not allow_negative_load:
        if (net.load.p_mw < 0. - 1e-4).any():
            reject = True
            info["negative_load"] = 1

    info["out_of_range_gen"] = 0
    if not allow_out_of_range_gen:
        active_gen = net.gen[net.gen.in_service == True]
        below_min = (active_gen.p_mw < active_gen.min_p_mw - 1e-4).any()
        above_max = (active_gen.p_mw > active_gen.max_p_mw + 1e-4).any()
        if below_min or above_max:
            reject = True
            info["out_of_range_gen"] = 1

    if max_count_voltage_violation is not None:
        count_above = np.sum(net.res_bus.vm_pu.values > net.bus.max_vm_pu)
        count_below = np.sum(net.res_bus.vm_pu.values < net.bus.min_vm_pu)
        if count_above + count_below > max_count_voltage_violation:
            reject = True
            info["too_many_voltage_violations"] = 1

    return reject, info
