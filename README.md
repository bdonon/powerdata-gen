![](figures/powerdata-gen_banner_dark.png#gh-dark-mode-only)
![](figures/powerdata-gen_banner_light.png#gh-light-mode-only)

An open-source power grid dataset generator.

# Content
This tool generates a dataset of [pandapower](https://pandapower.org) power grids datasets from a single snapshot.

It is compatible with [powerdata-view](https://github.com/bdonon/powerdata-view) for dataset visualization.

It randomly samples power grids built from a provided source power grid to generate datasets (i.e. directories filled
with pandapower files).
After the sampling, an AC power flow is run and a filtering is applied to make sure that the generated dataset
satisfies certain conditions.

![](figures/sampling_dark.png#gh-dark-mode-only)
![](figures/sampling_light.png#gh-light-mode-only)

# Installation

First, you need to clone the repository :
```
git clone https://github.com/bdonon/powerdata-gen.git
```
Then, go inside the project :
```
cd powerdata_gen
```

## Virtual Environment
It is usually a good practice to have a virtual environment per project, so that any package installation that 
you do for one project will not alter the others.
There are multiple ways of creating a virtual environment (virtualenv, conda or even your IDE).

In the following, we guide you through the creation of a virtual environment using the package virtualenv :
```
pip install virtualenv
virtualenv venv -p python3.10
```
Then, you need to activate the virtual environment :
```
source venv/bin/activate
```

## Installing dependencies

Once your virtual environment activated, you will have to install the packages that powerdata-view requires :
```
pip install -r requirements.txt
```

# Basic Usage

To run powerdata-gen, you just need to run the following :
```
python main.py
```
The generated datasets are located in `outputs/`.

# Configuration File

The configuration is defined in `config/config.yaml`. Here are the different fields :
- `default_net_path`: Path to the source pandapower .json file.
- `n_train`: Amount of sampled power grids in the Train dataset.
- `n_val`: Amount of sampled power grids in the Val dataset.
- `n_test`: Amount of sampled power grids in the Test dataset.
- `seed`: Random seed for the data generation process.
- `sampling`: Defines the sampling methods for the different components of the grid.
  - `topology`: Topology sampling process, cf. below.
  - `total_total`: Total active load sum sampling process, cf. below.
  - `active_load`: Individual active load sampling process, cf. below.
  - `reactive_load`: Individual reactive load sampling process, cf. below.
  - `active_gen`: Individual active generation sampling process, cf. below.
  - `voltage_setpoint`: Individual voltage set points sampling process, cf. below.
- `powerflow`: Pandapower AC power flow options.
- `filtering`: Defines the filtering step that rejects invalid samples, cf. below.

## Sampling

As shown in the figure above, the sampling process can be split into multiple parts.
For each part, the configuration is required to provide a sampling method name, and a set of parameters 
(defined as a set of keyword arguments).

### Topology

Sampling of the power grid topology.

| method                 | parameters | process                                           |
|------------------------|------------|---------------------------------------------------|
| `constant`             | -          | Does nothing                                      |
| `random_disconnection` | See below  | Randomly disconnects lines, generators and loads. |

In the `random_disconnection` mode, one should define a list of disconnection probabilities
for generators, loads and lines.
For instance, let us consider the following parameters :
```
  topology:
    method: "random_disconnection"
    params:
      line:
        probs:
          0: 0.2
          4: 0.8
        black_list: [25, 30]
```
There is a *20%* probability that no lines are disconnected, and *80%* probability that 
four of them (uniformly selected) are disconnected.
Moreover, lines 25 and 30 are ``blacklisted'' and will not be disconnected at all.

### Total Load

Sampling of the total consumption of the grid, denoted as $P_{tot}^{new}$.
The following sampling methods and corresponding params are available:

| method           | params               | process                                                                                               |
|------------------|----------------------|-------------------------------------------------------------------------------------------------------|
| `constant`       | -                    | $P_{tot}^{new} = P_{tot}^{old}$.                                                                      |
| `uniform_factor` | `min_val`, `max_val` | $P_{tot}^{new} = \epsilon \times P_{tot}^{old}$ ; $\epsilon \sim \mathcal{U}([`min_val`, `max_val`])$ |
| `normal_factor`  | `mean`, `std`        | $P_{tot}^{new} = \epsilon \times P_{tot}^{old}$ ; $\epsilon \sim \mathcal{N}(`mean`; `std`)$          |
| `uniform_values` | `min_val`, `max_val` | $P_{tot}^{new} \sim \mathcal{U}([`min_val`, `max_val`])$                                              |
| `normal_values`  | `mean`, `std`        | $P_{tot}^{new} \sim \mathcal{N}(`mean`; `std`)$                                                       |

### Active Load

Sampling of the individual active loads in *MW*.
The following sampling methods and corresponding params are available:

| method                       | parameters    | process                                                                                                                                                    |
|------------------------------|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `homothetic`                 | -             | $P_i^{new} = P_i^{old} \times \frac{P_{tot}^{new}}{P_{tot}^{old}}$                                                                                         |
| `uniform_independent_factor` | `beta`        | $P_i^{new} = (\epsilon_i - \frac{1}{n} + \frac{P_i^{old}}{P_{tot}^{old}}) \times P_{tot}^{new} ; \epsilon \sim \mathcal{U}(S(`beta`))$                     |
| `normal_independent_factor`  | `mean`, `std` | $P_i^{new} = (\epsilon_i - \frac{\sum \epsilon_j}{n} + \frac{P_i^{old}}{P_{tot}^{old}}) \times P_{tot}^{new} ; \epsilon_i \sim \mathcal{N}(`mean`; `std`)$ |
| `uniform_independent_values` | `beta`        | $P_i^{new} = \epsilon_i \times P_{tot}^{new} ; \epsilon \sim \mathcal{U}(S(`beta`))$                                                                       |
| `normal_independent_values`  | `mean`, `std` | $P_i^{new} = (\epsilon_i + \frac{1-\sum \epsilon_j}{n}) \times P_{tot}^{new} ; \epsilon_i \sim \mathcal{N}(`mean`; `std`)$                                 |

[^1] scaled so that it respects the total load.

where $n$ is the amount of loads and $S(\alpha) = \lbrace x | \sum x_i = 1, x_i \leq \alpha \rbrace $.

In the four last sampling methods, the parameter $`beta` \in [0,1]$ controls the spread 
of the distribution. Let us consider the case of the `uniform_independent_values`.
- If $`beta` = 0$, then the distribution is a dirac where all loads are the same.
- If $`beta` = 1$ then the distribution is uniform over a simplex.

![Active load sampling](./figures/active_load_dark.png#gh-dark-mode-only)
![Active load sampling](./figures/active_load_light.png#gh-light-mode-only)

> **WARNING**: The marginal distributions displayed in the figures above are only valid 
> if there are only two loads. When dealing with n loads, the uniform sampling 
> will amount to sampling from a n-dimensional simplex, thus making the marginal 
> distributions skewed towards low values.

### Reactive Load

Sampling of the individual reactive loads in *MVAr*.
The sampling of the reactive load is performed after the sampling of active loads.
In many of the proposed methods, the reactive power of a load depends on the new value of the active power.
The following sampling methods and corresponding params are available:

| method                               | parameters                      | process                                                                                                                      |
|--------------------------------------|---------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| `constant`                           | -                               | $Q_i^{new} = Q_i^{old}$                                                                                                      |
| `constant_pq_ratio`                  | -                               | $Q_i^{new} = P_i^{new} \times \frac{Q_i^{old}}{P_i^{old}}$                                                                   |
| `uniform_homothetic_factor`          | `min_val`, `max_val`            | $Q_i^{new} = \epsilon \times Q_i^{old}; \epsilon \sim \mathcal{U}([`min_val`, `max_val`])$                                   |
| `normal_homothetic_factor`           | `mean`, `std`                   | $Q_i^{new} = \epsilon \times Q_i^{old}; \epsilon \sim \mathcal{N}(`mean`; `std`)$                                            |
| `uniform_independent_factor`         | `min_val`, `max_val`            | $Q_i^{new} = \epsilon_i \times Q_i^{old}; \epsilon_i \sim \mathcal{U}([`min_val`, `max_val`])$                               |
| `normal_independent_factor`          | `mean`, `std`                   | $Q_i^{new} = \epsilon_i \times Q_i^{old}; \epsilon_i \sim \mathcal{N}(`mean`; `std`)$                                        |
| `uniform_independent_values`         | `min_val`, `max_val`            | $Q_i^{new} \sim \mathcal{U}([`min_val`, `max_val`])$                                                                         |
| `normal_independent_values`          | `mean`, `std`                   | $Q_i^{new} \sim \mathcal{N}(`mean`; `std`)$                                                                                  |
| `uniform_power_factor`               | `pf_min`, `pf_max`, `flip_prob` | $pf_i \sim \mathcal{U}([`pf_min`, `pf_max`]), P(sign_i=-1) = `flip_prob`, Q_i = sign_i \times P_i \times tan(arccos(pf_i)) $ |

![Reactive load sampling](./figures/reactive_load_dark.png#gh-dark-mode-only)
![Reactive load sampling](./figures/reactive_load_light.png#gh-light-mode-only)

### Active Generation

Sampling of the individual active loads in *MW*.
The following sampling methods and corresponding params are available:

| method                       | parameters                                                                               | process                                                                                                                                                                                                         |
|------------------------------|------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `homothetic`                 | -                                                                                        | $P_i^{new} = P_i^{old} \times \frac{P_{tot}^{new}}{P_{tot}^{old}}$                                                                                                                                              |
| `uniform_independent_factor` | `beta`                                                                                   | $P_i^{new} = (\epsilon_i - \frac{1}{n} + \frac{P_i^{old}}{P_{tot}^{old}}) \times P_{tot}^{new} ; \epsilon \sim \mathcal{U}(S(`beta`))$                                                                          |
| `normal_independent_factor`  | `mean`, `std`                                                                            | $P_i^{new} = (\epsilon_i - \frac{\sum \epsilon_j}{n} + \frac{P_i^{old}}{P_{tot}^{old}}) \times P_{tot}^{new} ; \epsilon_i \sim \mathcal{N}(`mean`; `std`)$                                                      |
| `uniform_independent_values` | `beta`                                                                                   | $P_i^{new} = \epsilon_i \times P_{tot}^{new} ; \epsilon \sim \mathcal{U}(S(`beta`))$                                                                                                                            |
| `normal_independent_values`  | `mean`, `std`                                                                            | $P_i^{new} = (\epsilon_i + \frac{1-\sum \epsilon_j}{n}) \times P_{tot}^{new} ; \epsilon_i \sim \mathcal{N}(`mean`; `std`)$                                                                                      |
| `dc_opf`                     | `min_cp0`, `max_cp0`, `min_cp1`, `max_cp1`, `min_cp2`, `max_cp2`                         | DC-OPF with random polynomial cost coefficients $c_0\sim \mathcal{U}([`min_cp0`, `max_cp0`])$, $c_1\sim \mathcal{U}([`min_cp1`, `max_cp1`])$, $c_2\sim \mathcal{U}([`min_cp2`, `max_cp2`])$.                    |
| `dc_opf_disconnect`          | `max_loading_percent`, `min_cp0`, `max_cp0`, `min_cp1`, `max_cp1`, `min_cp2`, `max_cp2`  | DC-OPF with disconnection with random polynomial cost coefficients $c_0\sim \mathcal{U}([`min_cp0`, `max_cp0`])$, $c_1\sim \mathcal{U}([`min_cp1`, `max_cp1`])$, $c_2\sim \mathcal{U}([`min_cp2`, `max_cp2`])$. | 

In the `dc_opf_disconnect` mode, unused generators are disconnected.

### Voltage Set Points

Sampling of the individual voltage set points in *p.u.*.
The following sampling methods and corresponding params are available:

| method                               | parameters           | process                                                                                        |
|--------------------------------------|----------------------|------------------------------------------------------------------------------------------------|
| `constant`                           | -                    | $V_i^{new} = V_i^{old}$                                                                        |
| `uniform_homothetic_factor`          | `min_val`, `max_val` | $V_i^{new} = \epsilon \times V_i^{old}; \epsilon \sim \mathcal{U}([`min_val`, `max_val`])$     |
| `normal_homothetic_factor`           | `mean`, `std`        | $V_i^{new} = \epsilon \times V_i^{old}; \epsilon \sim \mathcal{N}(`mean`; `std`)$              |
| `uniform_independent_factor`         | `min_val`, `max_val` | $V_i^{new} = \epsilon_i \times V_i^{old}; \epsilon_i \sim \mathcal{U}([`min_val`, `max_val`])$ |
| `normal_independent_factor`          | `mean`, `std`        | $V_i^{new} = \epsilon_i \times V_i^{old}; \epsilon_i \sim \mathcal{N}(`mean`, `std`)$          |
| `uniform_independent_values`         | `min_val`, `max_val` | $V_i^{new} \sim \mathcal{U}([`min_val`, `max_val`])$                                           |
| `normal_independent_values`          | `mean`, `std`        | $V_i^{new} \sim \mathcal{N}(`mean`; `std`)$                                                    |

![Voltage setpoint sampling](./figures/voltage_setpoint_dark.png#gh-dark-mode-only)
![Voltage setpoint sampling](./figures/voltage_setpoint_light.png#gh-light-mode-only)

## Filtering

After the sampling and the AC power flow step, each data sample is passed to a filtering function that
checks a certain amount of conditions, and rejects invalid samples.
Here are the currently implemented filtering options :
- `max_loading_percent`: Maximum branch loading percent. Rejects samples with overflow.
- `max_count_voltage_violation`: Maximum amount of voltage violations. Rejects samples with too many 
  voltage violations.
- `allow_disconnected_bus`
- `allow_negative_load`
- `allow_out_of_range_gen`

# Using a Different Configuration File

If you want to define a different configuration file (e.g. `config_2.yaml`), make sure to 
place it inside the `config/` directory, and use it using the following :
```
python main.py --config-name=config_2.yaml
```

# Contact

If you have any questions, please contact me at [balthazar.donon@uliege.be](mailto:balthazar.donon@uliege.be)
