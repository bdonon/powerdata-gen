from .random import sample_normal_simplex, sample_uniform_simplex

# TODO checker qu'on ne travaille que sur les objets connectés...


def sample_active_load_reject(net, default_net, total_load, config, reject_max):
    """Samples loads, rejects and counts negative loads."""
    negative_load = True
    reject = -1
    while negative_load and reject < reject_max:
        reject += 1
        sample_active_load(net, default_net, total_load, config)
        negative_load = check_active_load(net)
    return reject


def check_active_load(net):
    """Returns True if a load is negative."""
    return (net.load.p_mw < 0.).any()


def sample_active_load(net, default_net, total_load, config):
    """Samples active loads while respecting the total load."""
    method = config["sampling_method"]
    params = config["params"]
    if method == 'homothetic':
        apply_homothetic_transform(net, default_net, total_load)
    elif method == 'uniform_independent_factor':
        sample_uniform_independent_factor(net, default_net, total_load, params)
    elif method == 'normal_independent_factor':
        sample_normal_independent_factor(net, default_net, total_load, params)
    elif method == 'uniform_independent_values':
        sample_uniform_independent_values(net, total_load, params)
    elif method == 'normal_independent_values':
        sample_normal_independent_values(net, total_load, params)


def apply_homothetic_transform(net, default_net, total_load):
    """Homothetically transforms active loads to respect total_load."""
    active = net.load.in_service
    factor = total_load / default_net.load.p_mw.loc[active].sum()
    net.load.p_mw.loc[active] = factor * default_net.load.p_mw.loc[active]


def sample_uniform_independent_factor(net, default_net, total_load, params):
    """Samples uniformly around the default situation, while respecting the total_load."""
    active = net.load.in_service
    n_load = active.sum()
    default_value = default_net.load.p_mw.loc[active] / default_net.load.p_mw.loc[active].sum()
    factor = sample_uniform_simplex(params[0], size=n_load, center_around_zero=True)
    net.load.p_mw.loc[active] = (factor + default_value) * total_load


def sample_normal_independent_factor(net, default_net, total_load, params):
    """Samples normally around the default situation, while respecting the total_load."""
    active = net.load.in_service
    n_load = active.sum()
    default_value = default_net.load.p_mw.loc[active] / default_net.load.p_mw.loc[active].sum()
    factor = sample_normal_simplex(params[0], size=n_load, center_around_zero=True)
    net.load.p_mw.loc[active] = (factor + default_value) * total_load


def sample_uniform_independent_values(net, total_load, params):
    """Samples independent loads uniformly, while respecting total_load."""
    active = net.load.in_service
    n_load = active.sum()
    factor = sample_uniform_simplex(params[0], size=n_load)
    net.load.p_mw.loc[active] = total_load * factor


def sample_normal_independent_values(net, total_load, params):
    """Samples independent loads normally, while respecting total_load."""
    active = net.load.in_service
    n_load = active.sum()
    factor = sample_normal_simplex(params[0], size=n_load)
    net.load.p_mw.loc[active] = total_load * factor
