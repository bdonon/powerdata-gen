import numpy as np


def sample_total_load(default_net, config):
    """Samples a value for the total load based on the default_net total load."""
    method = config["sampling_method"]
    params = config["params"]
    default_total_load = default_net.load.p_mw.sum()
    if method == 'constant':
        return default_total_load
    elif method == 'uniform_factor':
        return default_total_load * np.random.uniform(params[0], params[1])
    elif method == 'normal_factor':
        return default_total_load * np.random.normal(params[0], params[1])
    elif method == 'uniform_values':
        return np.random.uniform(params[0], params[1])
    elif method == 'normal_values':
        return np.random.normal(params[0], params[1])
