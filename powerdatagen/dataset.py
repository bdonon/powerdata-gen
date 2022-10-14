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


def build_dataset(default_net, n_files, path, sampling_config, reject_max):
    """"""

    os.mkdir(path)


    n_characters = np.ceil(np.log10(n_files)).astype(int)

    n_converged, n_diverged = 0, 0
    active_load_reject, active_gen_reject = 0, 0
    active_load_accept, active_gen_accept = 0, 0

    pbar = tqdm.tqdm(range(n_files))
    for i in pbar:
        not_converged, reject = True, True
        while not_converged or reject:
            net, n_reject = sample_power_grid(default_net, sampling_config, reject_max)
            active_load_reject += n_reject['load']
            active_gen_reject += n_reject['gen']
            reject = False
            if n_reject['load'] >= reject_max:
                reject = True
            else:
                active_load_accept += 1
            if n_reject['gen'] >= reject_max:
                reject = True
            else:
                active_gen_accept += 1
            # Todo : clean sample rejection
            if top.unsupplied_buses(net):
                reject = True
                print('Unsupplied buses !')

            try:
                pp.runpp(net)
                # Get rid of snapshots with unsupplied buses
                not_converged = False
                n_converged += 1

            except:
                not_converged = True
                n_diverged += 1

        file_name = 'sample_' + str(i).rjust(n_characters, '0') + '.json'
        file_path = os.path.join(path, file_name)
        pp.to_json(net, file_path)


        divergence_ratio = n_diverged / (n_diverged + n_converged)
        active_load_reject_ratio = active_load_reject / (active_load_reject + active_load_accept)
        active_gen_reject_ratio = active_gen_reject / (active_gen_reject + active_gen_accept)
        pbar.set_description("Div. ratio = {:.2e}, Load reject ratio = {:.2e}, Gen reject ratio = {:.2e}".format(
            divergence_ratio, active_load_reject_ratio, active_gen_reject_ratio))

    generation_log = {
        'Divergence ratio': divergence_ratio,
        'Active load reject': active_load_reject_ratio,
        'Active generation reject': active_gen_reject_ratio
    }
    with open(os.path.join(path, "generation.log"), "w") as file:
        file.write(str(generation_log))

    #with open(os.path.join(path, 'generation_output.json'), 'w') as f:
    #    json.dump(generation_output, f)

    #generation.out