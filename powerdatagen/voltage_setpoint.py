import numpy as np


def sample_voltage_setpoint(net, default_net, method, params):
    """Samples voltage setpoints based on those found in default_net."""
    if method == 'constant':
        pass
    elif method == 'uniform_homothetic_factor':
        sample_uniform_homothetic_factor(net, default_net, params)
    elif method == 'normal_homothetic_factor':
        sample_normal_homothetic_factor(net, default_net, params)
    elif method == 'uniform_independent_factor':
        sample_uniform_independent_factor(net, default_net, params)
    elif method == 'normal_independent_factor':
        sample_normal_independent_factor(net, default_net, params)
    elif method == 'uniform_independent_values':
        sample_uniform_independent_values(net, params)
    elif method == 'normal_independent_values':
        sample_normal_independent_values(net, params)


def sample_uniform_homothetic_factor(net, default_net, params):
    """Applies a homothetic transform to default values, sampled uniformly from U([params[0], params[1]])."""
    factor = np.random.uniform(params[0], params[1])
    net.gen.vm_pu = factor * default_net.gen.vm_pu
    net.ext_grid.vm_pu = factor * default_net.ext_grid.vm_pu


def sample_normal_homothetic_factor(net, default_net, params):
    """Applies a common homothetic factor to all default values, sampled normally from N(params[0], params[1])."""
    factor = np.random.normal(params[0], params[1])
    net.gen.vm_pu = factor * default_net.gen.vm_pu
    net.ext_grid.vm_pu = factor * default_net.ext_grid.vm_pu


def sample_uniform_independent_factor(net, default_net, params):
    """Applies independent multiplicative factors, sampled uniformly from U([params[0], params[1]])."""
    n_gen, n_ext_grid = len(net.gen), len(net.ext_grid)
    factor = np.random.uniform(params[0], params[1], size=n_gen + n_ext_grid)
    net.gen.vm_pu = factor[:n_gen] * default_net.gen.vm_pu
    net.ext_grid.vm_pu = factor[n_gen:] * default_net.ext_grid.vm_pu


def sample_normal_independent_factor(net, default_net, params):
    """Applies independent multiplicative factors, sampled normally from N(params[0], params[1])."""
    n_gen, n_ext_grid = len(net.gen), len(net.ext_grid)
    factor = np.random.normal(params[0], params[1], size=n_gen + n_ext_grid)
    net.gen.vm_pu = factor[:n_gen] * default_net.gen.vm_pu
    net.ext_grid.vm_pu = factor[n_gen:] * default_net.ext_grid.vm_pu


def sample_uniform_independent_values(net, params):
    """Samples values uniformly from U([params[0], params[1]]), expressed in p.u.."""
    n_gen, n_ext_grid = len(net.gen), len(net.ext_grid)
    values = np.random.uniform(params[0], params[1], size=n_gen + n_ext_grid)
    net.gen.vm_pu = values[:n_gen]
    net.ext_grid.vm_pu = values[n_gen:]


def sample_normal_independent_values(net, params):
    """Samples values normally from N(params[0], params[1]), expressed in p.u.."""
    n_gen, n_ext_grid = len(net.gen), len(net.ext_grid)
    values = np.random.normal(params[0], params[1], size=n_gen + n_ext_grid)
    net.gen.vm_pu = values[:n_gen]
    net.ext_grid.vm_pu = values[n_gen:]
