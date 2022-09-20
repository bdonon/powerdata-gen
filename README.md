# powerdatagen : Power Grid Datasets Generator
Generates a dataset of [pandapower](https://pandapower.org) power grids datasets from a single snapshot.

# Usage
```
python main.py --config_file config.json
```

# Infos

It generates both a train and a test sets from the same data generating process.

# Configuration

The file `config.json` defines the parameters of the data generation process.

| parameter          | function                                                               |
|--------------------|------------------------------------------------------------------------|
| `default_net_path` | Path to the default pandapower network. Should be a `.json` file.      |
| `dataset_name`     | Path where the generated dataset should be stored.                     |
| `n_train`          | Amount of samples in the train set.                                    |
| `n_test`           | Amount of samples in the test set.                                     |
| `sampling`         | Defines the data generating process from which power grids are sampled |

In the `sampling` field, one can define how the topology, loads and generation are built :

| parameter          | function                                                      |
|--------------------|---------------------------------------------------------------|
| `topology`         | Sampling of lines, generators and loads to be disconnected.   |
| `total_load`       | Sampling of total summed load in *MW*.                        |
| `active_load`      | Sampling of individual active load in *MW*.                   |
| `reactive_load`    | Sampling of individual reactive loads in *MVAr*.              |
| `active_gen`       | Sampling of individual active generation in *MW*.             |
| `voltage_setpoint` | Sampling of individual generator voltage setpoints in *p.u.*. |

## Topology

TODO

## Total load

Sampling of the total consumption of the grid, denoted as $P_{tot}^{new}$.
The following sampling methods are available, where parameters are denoted as $\alpha$ :

| method           | parameters | function                                                                                              |
|------------------|------------|-------------------------------------------------------------------------------------------------------|
| `constant`       | 0          | $P_{tot}^{new} = P_{tot}^{old}$.                                                                      |
| `uniform_factor` | 2          | $P_{tot}^{new} = \epsilon \times P_{tot}^{old}$ where $\epsilon \sim \mathcal{U}(\alpha_1, \alpha_2)$ |
| `normal_factor`  | 2          | $P_{tot}^{new} = \epsilon \times P_{tot}^{old}$ where $\epsilon \sim \mathcal{N}(\alpha_1, \alpha_2)$ |
| `uniform_values` | 2          | $P_{tot}^{new} \sim \mathcal{U}(\alpha_1, \alpha_2)$                                                  |
| `normal_values`  | 2          | $P_{tot}^{new} \sim \mathcal{N}(\alpha_1, \alpha_2)$                                                  |

