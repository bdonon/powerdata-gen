import numpy as np


def sample_topology(net, config):
    """Samples the power grid topology"""
    method = config["sampling_method"]
    params = config["params"]
    if method == 'constant':
        pass
    if method == 'random_disconnection':
        sample_random_disconnection(net, params)

def sample_random_disconnection(net, params):
    """Randomly disconnects generators, loads and lines."""
    random_disconnect_object(net.gen, params['gen'])
    random_disconnect_object(net.load, params['load'])
    random_disconnect_object(net.line, params['line'])

def random_disconnect_object(object, params):
    """Randomly disconnect objects."""
    max_disconnect = len(params)
    n_disconnect = np.random.choice(max_disconnect, p=params)
    n_obj = len(object)
    disconnected_gens = np.random.choice(n_obj, size=n_disconnect, replace=False)
    object.in_service.iloc[disconnected_gens] = False
