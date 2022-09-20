from .random import sample_normal_simplex, sample_uniform_simplex


def sample_active_generation(net, default_net, total_load, config):
    """Samples active gen while respecting the total load."""
    method = config["sampling_method"]
    params = config["params"]
    if method == 'homothetic':
        apply_homothetic_transform(net, default_net, total_load)
    elif method == 'uniform_independent_factor':
        sample_uniform_independent_factor(net, default_net, total_load, params)
    elif method == 'normal_independent_factor':
        sample_normal_independent_factor(net, default_net, total_load, params)
    elif method == 'uniform_independent_values':
        sample_uniform_independent_values(net, default_net, total_load, params)
    elif method == 'normal_independent_values':
        sample_normal_independent_values(net, default_net, total_load, params)


def apply_homothetic_transform(net, default_net, total_load):
    """Homothetically transforms active loads to respect total_load, while adjusting approximately for Joule losses."""
    active_gen = net.gen.in_service
    active_sgen = net.sgen.in_service
    #n_gen = active_gen.sum()
    #n_sgen = active_sgen.sum()
    #factor = total_load / default_net.load.p_mw.sum()
    net.gen.p_mw = total_load * 1.02 * default_net.gen.p_mw.loc[active_gen] / default_net.gen.p_mw.loc[active_gen].sum()
    net.sgen.p_mw = total_load * 1.02 * default_net.sgen.p_mw.loc[active_sgen] / default_net.sgen.p_mw.loc[active_sgen].sum()


def sample_uniform_independent_factor(net, default_net, total_load, params):
    """Samples uniformly around the default situation, while respecting the total_load and Joule losses."""
    active_gen = net.gen.in_service
    active_sgen = net.sgen.in_service
    n_gen = active_gen.sum()
    n_sgen = active_sgen.sum()
    # default_total_load = default_net.load.p_mw.sum()
    default_total_gen = default_net.gen.p_mw.loc[active_gen].sum() + default_net.sgen.p_mw.loc[active_sgen].sum()
    total_gen = total_load * 1.02  # default_total_gen / default_total_load
    gen_default_value = (default_net.gen.p_mw.loc[active_gen]) / default_total_gen
    sgen_default_value = (default_net.sgen.p_mw.loc[active_sgen]) / default_total_gen
    factor = sample_uniform_simplex(params[0], size=n_gen+n_sgen, center_around_zero=True)
    net.gen.p_mw.loc[active_gen] = (factor[:n_gen] + gen_default_value) * total_gen
    net.sgen.p_mw.loc[active_sgen] = (factor[n_gen:] + sgen_default_value) * total_gen


def sample_normal_independent_factor(net, default_net, total_load, params):
    """Samples normally around the default situation, while respecting the total_load and Joule losses."""
    active_gen = net.gen.in_service
    active_sgen = net.sgen.in_service
    n_gen = active_gen.sum()
    n_sgen = active_sgen.sum()
    #default_total_load = default_net.load.p_mw.sum()
    default_total_gen = default_net.gen.p_mw.loc[active_gen].sum() + default_net.sgen.p_mw.loc[active_sgen].sum()
    total_gen = total_load * 1.02 #default_total_gen / default_total_load
    gen_default_value = (default_net.gen.p_mw.loc[active_gen]) / default_total_gen
    sgen_default_value = (default_net.sgen.p_mw.loc[active_sgen]) / default_total_gen
    factor = sample_normal_simplex(params[0], size=n_gen + n_sgen, center_around_zero=True)
    net.gen.p_mw.loc[active_gen] = (factor[:n_gen] + gen_default_value) * total_gen
    net.sgen.p_mw.loc[active_sgen] = (factor[n_gen:] + sgen_default_value) * total_gen


def sample_uniform_independent_values(net, default_net, total_load, params):
    """Samples independent gens uniformly, while respecting total_load."""
    active_gen = net.gen.in_service
    active_sgen = net.sgen.in_service
    n_gen = active_gen.sum()
    n_sgen = active_sgen.sum()
    #default_total_load = default_net.load.p_mw.sum()
    #default_total_gen = default_net.gen.p_mw.sum() + default_net.sgen.p_mw.sum()
    total_gen = total_load * 1.02 # default_total_gen / default_total_load
    factor = sample_uniform_simplex(params[0], size=n_gen + n_sgen)
    net.gen.p_mw.loc[active_gen] = factor[:n_gen] * total_gen
    net.sgen.p_mw.loc[active_sgen] = factor[n_gen:] * total_gen


def sample_normal_independent_values(net, default_net, total_load, params):
    """Samples independent gens normally, while respecting total_load."""
    active_gen = net.gen.in_service
    active_sgen = net.sgen.in_service
    n_gen = active_gen.sum()
    n_sgen = active_sgen.sum()
    #default_total_load = default_net.load.p_mw.sum()
    #default_total_gen = default_net.gen.p_mw.sum() + default_net.sgen.p_mw.sum()
    total_gen = total_load * 1.02 #default_total_gen / default_total_load
    factor = sample_uniform_simplex(params[0], size=n_gen + n_sgen)
    net.gen.p_mw.loc[active_gen] = factor[:n_gen] * total_gen
    net.sgen.p_mw.loc[active_sgen] = factor[n_gen:] * total_gen

