from .random import sample_normal_simplex, sample_uniform_simplex

# TODO checker qu'on ne travaille que sur les objets connectés...


def sample_active_load(net, default_net, total_load, method, params):
    """Samples active loads while respecting the total load."""
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
    factor = total_load / default_net.load.p_mw.sum()
    net.load.p_mw = factor * default_net.load.p_mw


def sample_uniform_independent_factor(net, default_net, total_load, params):
    """Samples uniformly around the default situation, while respecting the total_load."""
    n_load = len(net.load)
    default_value = default_net.load.p_mw / default_net.load.p_mw.sum()
    factor = sample_uniform_simplex(params[0], size=n_load, center_around_zero=True)
    net.load.p_mw = (factor + default_value) * total_load


def sample_normal_independent_factor(net, default_net, total_load, params):
    """Samples normally around the default situation, while respecting the total_load."""
    n_load = len(net.load)
    default_value = default_net.load.p_mw / default_net.load.p_mw.sum()
    factor = sample_normal_simplex(params[0], size=n_load, center_around_zero=True)
    net.load.p_mw = (factor + default_value) * total_load


def sample_uniform_independent_values(net, total_load, params):
    """Samples independent loads uniformly, while respecting total_load."""
    n_load = len(net.load)
    factor = sample_uniform_simplex(params[0], size=n_load)
    net.load.p_mw = total_load * factor


def sample_normal_independent_values(net, total_load, params):
    """Samples independent loads normally, while respecting total_load."""
    n_load = len(net.load)
    factor = sample_normal_simplex(params[0], size=n_load)
    net.load.p_mw = total_load * factor
