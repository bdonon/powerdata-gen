import numpy as np


def sample_topology(net, config):
    """Samples the power grid topology"""
    method = config["sampling_method"]
    params = config["params"]
    black_lists = config["black_lists"]
    if method == 'constant':
        pass
    if method == 'random_disconnection':
        sample_random_disconnection(net, params, black_lists)


def sample_random_disconnection(net, params, black_lists):
    """Randomly disconnects generators, loads and lines."""
    random_disconnect_object(net.gen, params['gen'], black_lists.get('gen', []))
    random_disconnect_object(net.load, params['load'], black_lists.get('load', []))
    random_disconnect_object(net.line, params['line'], black_lists.get('line', []))


def random_disconnect_object(object, params, black_list):
    """Randomly disconnect objects."""
    max_disconnect = len(params)
    n_disconnect = np.random.choice(max_disconnect, p=params)
    n_obj = len(object)
    white_list = [i for i in range(n_obj) if i not in black_list]
    disconnected_objects = np.random.choice(white_list, size=n_disconnect, replace=False)
    object.in_service.iloc[disconnected_objects] = False
