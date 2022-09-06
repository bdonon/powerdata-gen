import copy

from .total_load import sample_total_load
from .active_load import sample_active_load
from .reactive_load import sample_reactive_load
from .active_generation import sample_active_generation
from .voltage_setpoint import sample_voltage_setpoint
from .topology import sample_topology


def sample_power_grid(
        default_net,
        total_load_sampling_method='constant',
        total_load_params=None,
        active_load_sampling_method='homothetic',
        active_load_params=None,
        reactive_load_sampling_method='constant',
        reactive_load_params=None,
        active_gen_sampling_method='homothetic',
        active_gen_params=None,
        voltage_setpoint_sampling_method='constant',
        voltage_setpoint_params=None,
        topology_sampling_method='constant',
        topology_params=None):
    """Generates a single power grid instance."""

    net = copy.deepcopy(default_net)
    total_load = sample_total_load(default_net, total_load_sampling_method, total_load_params)
    sample_active_load(net, default_net, total_load, active_load_sampling_method, active_load_params)
    sample_reactive_load(net, default_net, reactive_load_sampling_method, reactive_load_params)
    sample_active_generation(net, default_net, total_load, active_gen_sampling_method, active_gen_params)
    sample_voltage_setpoint(net, default_net, voltage_setpoint_sampling_method, voltage_setpoint_params)
    sample_topology(net, default_net, topology_sampling_method, topology_params)

    return net