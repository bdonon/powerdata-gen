import copy

from .total_load import sample_total_load
from .active_load import sample_active_load
from .reactive_load import sample_reactive_load
from .active_generation import sample_active_generation
from .voltage_setpoint import sample_voltage_setpoint
from .topology import sample_topology


def sample_power_grid(default_net, config):
    """Generates a single power grid instance."""

    net = copy.deepcopy(default_net)
    total_load = sample_total_load(default_net, config["total_load"])
    sample_active_load(net, default_net, total_load, config["active_load"])
    sample_reactive_load(net, default_net, config["reactive_load"])
    sample_active_generation(net, default_net, total_load, config["active_gen"])
    sample_voltage_setpoint(net, default_net, config["voltage_setpoint"])
    #sample_topology(net, default_net, config["total_load"])
    return net
