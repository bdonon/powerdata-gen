import argparse
import shutil
import json
import os

from powerdatagen import build_train_test_datasets


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate a randomly dataset from a single power grid.')
    parser.add_argument('--config_file', type=str, required=True, help='Config json file.')

    args = parser.parse_args()
    with open(args.config_file) as f:
        config = json.load(f)

    default_net_path = config.get("default_net_path")
    dataset_name = config.get("dataset_name", "data/no_name")
    n_train = config.get("n_train", 1000)
    n_test = config.get("n_test", 100)
    sampling_config = config.get("sampling")
    reject_max = config.get("reject_max", 10)
    seed = config.get("seed", None)

    os.mkdir(dataset_name)
    config_dir = os.path.join(dataset_name, 'config')
    os.mkdir(config_dir)
    shutil.copyfile(default_net_path, os.path.join(config_dir, 'default_net.json'))
    with open(os.path.join(config_dir, 'parameters.json'), 'w') as f:
        json.dump(config, f)

    build_train_test_datasets(default_net_path, dataset_name, n_train, n_test, sampling_config, reject_max, seed)
