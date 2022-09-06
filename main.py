import argparse
from powerdatagen import build_train_test_datasets


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate a randomly dataset from a single power grid.')
    parser.add_argument('--default_net_path', type=str, required=True,
                        help='Path to the power grid file that will serve to generate data.')
    parser.add_argument('--dataset_name', type=str, required=True,
                        help='Name of the dataset to be generated.')
    parser.add_argument('--n_train', type=int, default=1000,
                        help='Size of the train set to be generated.')
    parser.add_argument('--n_test', type=int, default=100,
                        help='Size of the test set to be generated.')

    # Total load
    parser.add_argument('--total_load_sampling_method', type=str, default='constant',
                        choices=['constant', 'uniform_factor', 'normal_factor', 'uniform_values', 'normal_values'],
                        help='Method for total load sampling')
    parser.add_argument('--total_load_params', default=None,
                        help='Parameters for total load sampling, depends on the method choice.')

    # Active load
    parser.add_argument('--active_load_sampling_method', type=str, default='homothetic',
                        choices=['homothetic', 'uniform_independent_factor', 'normal_independent_factor',
                                 'uniform_independent_values', 'normal_independent_values'],
                        help='Method for active load sampling.')
    parser.add_argument('--active_load_params', default=None,
                        help='Parameters for active load sampling, depends on the method choice.')

    # Reactive load
    parser.add_argument('--reactive_load_sampling_method', type=str, default='constant',
                        choices=['constant', 'constant_pq_ratio', 'uniform_homothetic_factor',
                                 'normal_homothetic_factor', 'uniform_independent_factor',
                                 'normal_independent_factor', 'uniform_independent_values',
                                 'normal_independent_values'],
                        help='Method for reactive load sampling.')
    parser.add_argument('--reactive_load_params', default=None,
                        help='Parameters for reactive load sampling, depends on the method choice.')

    # Active generation
    parser.add_argument('--active_gen_sampling_method', type=str, default='homothetic',
                        choices=['homothetic', 'uniform_independent_factor', 'normal_independent_factor',
                                 'uniform_independent_values', 'normal_independent_values'],
                        help='Method for active generation sampling.')
    parser.add_argument('--active_gen_params', default=None,
                        help='Parameters for active generation sampling, depends on the method choice.')

    # Voltage setpoints
    parser.add_argument('--voltage_setpoint_sampling_method', type=str, default='constant',
                        choices=['constant', 'uniform_homothetic_factor', 'normal_homothetic_factor',
                                 'uniform_independent_factor', 'normal_independent_factor',
                                 'uniform_independent_values', 'normal_independent_values'],
                        help='Method for the voltage setpoint sampling.')
    parser.add_argument('--voltage_setpoint_params', default=None,
                        help='Parameters for voltage setpoint sampling, depends on the method choice.')

    # Topology
    # TODO add arguments for topology sampling

    args = parser.parse_args()

    build_train_test_datasets(**vars(args))
