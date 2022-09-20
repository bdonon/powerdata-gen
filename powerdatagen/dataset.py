import pandapower as pp
import numpy as np
import tqdm
import json
import os

from .power_grid import sample_power_grid


def build_train_test_datasets(default_net_path, dataset_name, n_train, n_test, sampling_config):
    """Build both train and test sets."""
    default_net = pp.from_json(default_net_path)
    os.mkdir(dataset_name)
    print("Building the train set...")
    build_dataset(default_net, n_train, os.path.join(dataset_name, 'train'), sampling_config)
    print("Building the test set...")
    build_dataset(default_net, n_test, os.path.join(dataset_name, 'test'), sampling_config)


def build_dataset(default_net, n_files, path, sampling_config):
    """"""

    os.mkdir(path)
    config_dir = os.path.join(path, 'config')
    os.mkdir(config_dir)
    pp.to_json(default_net, os.path.join(config_dir, 'default_net.json'))
    with open(os.path.join(config_dir, 'parameters.json'), 'w') as f:
        json.dump(sampling_config, f)

    n_characters = np.ceil(np.log10(n_files)).astype(int)

    for i in tqdm.tqdm(range(n_files)):
        not_converged = True
        while not_converged:
            net = sample_power_grid(default_net, sampling_config)
            try:
                pp.runpp(net)
                file_name = 'sample_' + str(i).rjust(n_characters, '0') + '.json'
                file_path = os.path.join(path, file_name)
                pp.to_json(net, file_path)
                not_converged = False
            except pp.LoadflowNotConverged:
                pass
