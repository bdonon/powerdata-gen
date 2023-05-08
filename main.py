# -*- coding: utf-8 -*-
"""Samples power grid datasets based on provided configuration."""

import logging
import os
import shutil

import hydra
from omegaconf import DictConfig

from powerdata_gen import build_datasets

os.environ["HYDRA_FULL_ERROR"] = "1"

log = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: DictConfig) -> None:
    """Builds train, val and test datasets."""
    save_path = hydra.core.hydra_config.HydraConfig.get().runtime.output_dir
    shutil.copyfile(cfg.default_net_path, os.path.join(save_path, 'default_net.json'))
    build_datasets(cfg.default_net_path, save_path, log, cfg.n_train, cfg.n_val, cfg.n_test, cfg.sampling,
                   cfg.powerflow, cfg.filtering, cfg.seed)


if __name__ == '__main__':
    main()
