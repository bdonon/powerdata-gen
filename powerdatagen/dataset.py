import pandapower as pp
import pandapower.topology as top
import numpy as np
import tqdm
import json
import os

from .power_grid import sample_power_grid


def build_train_test_datasets(default_net_path, dataset_name, n_train, n_test, sampling_config, reject_max, seed):
    """Build both train and test sets."""
    if seed is not None:
        np.random.seed(seed)
    default_net = pp.from_json(default_net_path)
    print("Building the train set...")
    build_dataset(default_net, n_train, os.path.join(dataset_name, 'train'), sampling_config, reject_max)
    print("Building the test set...")
    build_dataset(default_net, n_test, os.path.join(dataset_name, 'test'), sampling_config, reject_max)


def check_active_gen(net):
    """Returns True if a generator generates a p_mw out of its min-max range."""
    active_gen = net.gen[net.gen.in_service==True]
    return np.array([(active_gen.p_mw < active_gen.min_p_mw).any(), (active_gen.p_mw > active_gen.max_p_mw).any()]).any()


def check_active_load(net):
    """Returns True if a load is negative."""
    return (net.load.p_mw < 0.).any()


def check_branch_overflow(net):
    return np.array([(net.res_line.loading_percent > 100).any(), (net.res_trafo.loading_percent > 100).any()]).any()


def check_disconnected_bus(net):
    return top.unsupplied_buses(net)


def reject_function(net):
    if check_active_gen(net) or check_active_load(net) or check_branch_overflow(net) or check_disconnected_bus(net):
        return True
    else:
        return False


def build_dataset(default_net, n_files, path, sampling_config, reject_max):
    """"""
    os.mkdir(path)
    n_characters = np.ceil(np.log10(n_files)).astype(int)
    n_divergence, n_rejection = 0, 0
    pbar = tqdm.tqdm(range(n_files))
    for i in pbar:
        not_converged, reject = True, True
        while not_converged or reject:
            net = sample_power_grid(default_net, sampling_config)
            try:
                pp.runpp(net)
                not_converged = False
            except:
                not_converged = True
                n_divergence += 1
            reject = reject_function(net)
            if reject:
                n_rejection += 1

        file_name = 'sample_' + str(i).rjust(n_characters, '0') + '.json'
        file_path = os.path.join(path, file_name)
        pp.to_json(net, file_path)

        pbar.set_description("Divergences = {}, Rejections = {} ".format(
            n_divergence, n_rejection))

    generation_log = {
        'Divergences': n_divergence,
        'Rejections': n_rejection
    }
    with open(os.path.join(path, "generation.log"), "w") as file:
        file.write(str(generation_log))

    #with open(os.path.join(path, 'generation_output.json'), 'w') as f:
    #    json.dump(generation_output, f)

    #generation.out