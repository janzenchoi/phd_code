# MOGA NEML

The repository contains code for calibrating the constitutive parameters of phenomenological creep models. The code combines the multi-objective genetic algorithm (MOGA) implemented in Pymoo with the nuclear engineering material model library (NEML). The following README was last updated on the 19th of December, 2023.

# Installation

The following section details the requirements to run the script.

## NEML

NEML is a tool for developing / running structural material models. To install NEML for this repository, please follow the instructions below. Note that these instructions are slightly modified from the [official instructions](https://neml.readthedocs.io/en/dev/started.html).

To install NEML, first clone the repository recursively using the following command.
```
git clone --recursive https://github.com/Argonne-National-Laboratory/neml.git
```

Once done, move into the NEML directory.
```
cd neml
```
Then compile NEML using the following configurations. You can run `cmake` with `-D USE_OPENMP=ON` to enable multithreading for certain models (e.g., Taylor Models).
```
cmake -D WRAP_PYTHON=ON -D CMAKE_BUILD_TYPE=Release .
make -j 2
```

After installing NEML, add NEML to the system path. You can do this by going to your home directory, adding the following line to the `~/.bashrc` file. Note that `<path_to_neml>` refers to the absolute path to the installed NEML directory.
```
export PYTHONPATH=$PYTHONPATH:<path_to_neml>
```

Make sure to source the `.bashrc` file or restart the terminal, so that NEML is added to the system path properly.

## Python Packages

The scripts also require several Python packages.

To install these packages, `pip` is required.

If you do not have `pip` installed, please following [these instructions](https://linuxize.com/post/how-to-install-pip-on-ubuntu-18.04/).

Once `pip` is installed, you can run `pip3 install -r requirements.txt` from the directory to install the Python packages.

## Importing `moga_neml`

The user can add the `moga_neml` package to the system path so that they can import the code anywhere on their machine. This involves simply adding the following line to the `~/.bashrc` file, as follows. Note that `<path_to_moga_neml>` refers to the absolute path to the `moga_neml` directory.
```
export PYTHONPATH=$PYTHONPATH:<path_to_moga_neml>
```

Alternatively, the user can import `moga_neml` dynamically depending on the relative path between the main `moga_neml` directory and their script. For instance, if the user wants to run a script in the `moga_neml/scripts/` directory, they can use the following.
```
import sys; sys.path += [".."]
import moga_neml
```

# Interacting with `moga_neml`

The following section provides a tutorial on using the `moga_neml` code.

## Interface Class

The `Interface` class allows the user to interact with the `moga_neml` code. To access the `Interface` class, the user must first import the `moga_neml` package and initialise an `Interface` object. The following is an example of doing so from the `moga_neml/scripts/` directory.
```py
import sys; sys.path += [".."]
from moga_neml import Interface
itf = Interface()
```

The `Interface` class contains several optional arguments. These include:
* `title`: This optional argument appends a title in front of the directory in which the output files will be placed in. The default value for this argument is an empty string.
* `input_path`: This optional argument defines the relative path to the input directory, which stores the experimental data. The default value for this argument is `"./data"`.
* `output_path`: This optional argument defines the relative path to the output directory, which tells the script where to place the output files. The default value for this arguemnt is `"./results"`.
* `verbose`: This optional argument tells the script whether to display any information about the actions of the `Interface` class in the terminal. The default value for this argument is `True`, meaning that the information will be displayed in the terminal.
* `output_here`: This optional argument tells the script whether to just place the output files in the same directory as the script. The default value for this is `False`. Note that when the user sets the argument to `True`, the `title` and `output_path` values will not have any effect.

The implementation of the `Interface` class can be accessed via `moga_neml/moga_neml/itf.py`. The next sections provide descriptions of the available functions, their available arguments, and how to use them. Note that additional descriptions of the `Interface` functions can also be accessed by hovering your cursor over the functions. However, this functionality is only supported by some IDEs (e.g., Visual Studio Code).

## Defining the Model (`define_model`)

The `define_model` function defines the model to be optimised.
* `model_name`: This argument defines the name of the model, which corresponds to the name of the model file in the `moga_neml/moga_neml/models/` directory.
* `**kwargs`: This optional argument allows the user to pass on some arguments to the defined model's `initialise` function.

## Reading an experimental dataset (`read_data`)

The `read_data` function reads experimental data into the `Interface` class.
* `file_path`: This argument defines the path to the experimental data. Note that this path appends the `input_path` value defined when initialising the `Interface` class.
* `thin_data`: This optional argument tells the script whether to thin the data before reading the experimental data into the `Interface` class. The default value for this argument is `True`.
* `num_points`: This optional argument defines how many points the experimental data will be thinned to. This argument only works if the `thin_data` argument has been set to `True`. The default value for this argument is `1000`.

## Changing a field in the experimental data (`change_data`)

The `change_data` function changes files in the last read experimental data by the `read_data` function.
* `field`: This argument defines the name of the field.
* `value`: This argument defines the desired value corresponding to the field.

This function relies on the `read_data` function to be called first.

## Removing damage from creep data (`remove_damage`)

The `remove_damage` function removes the the tertiary regime of experimental creep data using their stationary points. This function applies only to the last read experimental data by the `read_data` function.
* `window`: This optional argument allows the user to define the window size to determine the stationary points. The default value of this argument is `0.1`, which will tell the function to search using intervals of 10% of the number of data points in the experimental data.
* `acceptance`: This optional argument allows the user to define the acceptance rate to validate stationary points. The default value of this argument is `0.9`, which tells the function to accept that a point is stationary if 90% of the derivatives on both sides of the point have the correct sign.

This function relies on the `read_data` function to be called first.

## Removing oxidation from creep data (`remove_oxidation`)

The `remove_oxidation` function removes data after the tertiary regime of experimental creep data (resulting from oxidation) using their stationary points. This function applies only to the last read experimental data by the `read_data` function.
* `window`: This optional argument allows the user to define the window size to determine the stationary points. The default value of this argument is `0.1`, which will tell the function to search using intervals of 10% of the number of data points in the experimental data.
* `acceptance`: This optional argument allows the user to define the acceptance rate to validate stationary points. The default value of this argument is `0.9`, which tells the function to accept that a point is stationary if 90% of the derivatives on both sides of the point have the correct sign.

This function relies on the `read_data` function to be called first.

## Removing data manually (`remove_manual`)

The `remove_manual` function removes data after a point which the user defines.
* `label`: This argument defines the data label (e.g., `"strain"`, `"stress"`, `"time"`).
* `value`: This argument defines the value after which data will be removed.

If `label` is set to `time` and `value` is set to `100`, then the function will remove data after `time==100` in the experimental data.

This function relies on the `read_data` function to be called first.

## Defining an error (`add_error`)

The `add_error` function defines an error for the MOGA to minimise during the optimisation.
* `error_name`: This argument defines the name of the error, which corresponds to the name of the error file in the `moga_neml/moga_neml/errors/` directory.
* `x_label`: This argument defines the type of horizontal data the error will use when calculating the error value.
* `y_label`: This argument defines the type of vertical data the error will use when calculating the error value. This argument only applies to some errors.
* `weight`: This optional argument defines the weight of the error when calculating the final objective value.
* `**kwargs`: This optional argument allows the user to pass on some arguments to the defined error's `initialise` function.

This function relies on the `read_data` function to be called first.

Note that if an experimental dataset is read in but no errors or constraints are defined for it, then it will still be included in the MOGA optimisation for validation. This means that any outputted plots / results will still include the experimental dataset, but the dataset will not influence the optimisation.

## Grouping the errors (`group_errors`)

The `group_errors` function defines how the errors will be grouped into objective functions for the MOGA optimisation.
* `name`: This optional argument tells the MOGA to group the errors by their name. The default value for this argument is `True`.
* `type`: This optional argument tells the MOGA to group the errors by the data types of the experimental data. The default value for this argument is `True`.
* `labels`: This optional argument tells the MOGA to group the errors by the labels used when defining the errors. The default value for this argument is `True`.

Note that this function is optional, and the default values will be set without the function being called. Additionally, if all the arguments are set to false, then the errors will be grouped into a single objective function.

## Reducing the errors (`reduce_errors`)

The `reduce_erroprs` function defines how the error values will be combined to calculate the objective values for the MOGA optimisation.
* `method`: This optional argument sets the reduction method. The available values include `"sum"`, `"average"`, `"square_sum"`, and `"square_average"`. The default value for this argument is `"average"`.

Note that this function is optional, and the default value will be set without the function being called.

## Reducing the objective values (`reduce_objectives`)

The `reduce_objectves` function defines how the objective values will be combined to calculate the optimal set of parameters from the population of parameters.
* `method`: This optional argument sets the reduction method. The available values include `"sum"`, `"average"`, `"square_sum"`, and `"square_average"`. The default value for this argument is `"average"`.

Note that this function is optional, and the default value will be set without the function being called.

## Defining a constraint (`add_constraint`)

The `add_constraint` function defines a constraint for the MOGA optimisation. If the constraint is violated, then the MOGA will reject the corresponding parameters.
* `constraint_name`: This argument defines the name of the constraint, which corresponds to the name of the constraint file in the `moga_neml/moga_neml/constraints/` directory.
* `x_label`: This argument defines the type of horizontal data the constraint will use when determining whether the constraint has been violated.
* `y_label`: This argument defines the type of vertical data the constraint will use when determining whether the constraint has been violated.
* `**kwargs`: This optional argument allows the user to pass on some arguments to the defined constraint's `initialise` function.

This function relies on the `read_data` function to be called first.

## Fixing a parameter (`fix_param`)

The `fix_param` function tells the MOGA to fix a parameter to a value when optimising.
* `param_name`: This argument defines the name of the parameter.
* `param_value`: This argument defines the value the parameter will be fixed to.

This function relies on the `define_model` function to be called first.

## Fixing multipler parameters (`fix_params`)

The `fix_params` function tells the MOGA to fix multiple parameters during the optimisation. This function can be used in lieu of the `fix_param` function.
* `param_values`: This argument defines a list of the fixed parameter values. Note that the script will fix the first `len(param_values)` parameters to those values.

This function relies on the `define_model` function to be called first.

## Initialising a parameter (`init_param`)

The `init_param` function tells the MOGA to initialise a parameter to a value for the initial population of the optimisation. This differs from the `fix_param` function in that the MOGA will still try to change the initialised parameter's values during the optimisation.
* `param_name`: This argument defines the name of the parameter.
* `param_value`: This argument defines the value the parameter will be initialised to.

This function relies on the `define_model` function to be called first.

## Initialising multipler parameters (`init_params`)

The `init_params` function tells the MOGA to initialise multiple parameters during the optimisation. This function can be used in lieu of the `init_param` function.
* `param_values`: This argument defines a list of the initialised parameter values. Note that the script will initialise the first `len(param_values)` parameters to those values.

This function relies on the `define_model` function to be called first.

## Setting a custom driver (`set_driver`)

The `set_driver` function forces the script to use a specific NEML driver instead of the pre-defined drivers in the script. Information about these drivers can be found on the [official NEML documentation](https://neml.readthedocs.io/en/dev/python/drivers.html#driver-classes).
* `driver_type`: This arugment defines the name of the NEML driver.
* `**kwargs`: This argument allows the user to pass on some arguments to the defined NEML driver. Consult the NEML documentation to figure out which arguments to define.

Note that this function is optional, since the script already wraps several of the NEML drivers (i.e., `"creep"`, `"tensile"`, and (strain-controlled) `"cyclic"`). This function should only be used if the desired driver has not been wrapped or if the user wants to alter the set argument values in the driver.

## Plotting the experimental data (`plot_experimental`)

The `plot_experimental` function creates a plot of all the experimental data that has been read by the `read_data` function.
* `x_log`: This optional argument tells the function whether to plot the x-axis on a log scale. The default value of this argument is `False`.
* `y_log`: This optional argument tells the function whether to plot the y-axis on a log scale. The default value of this argument is `False`.

This function relies on the `read_data` function to be called first.

## Plotting multiple simulation results (`plot_simulation`)

The `plot_simulation` function creates a plot of all the experimental data that has been read by the `read_data` function as well as multiple simulated responses from multiple sets of parameters.
* `params_list`: This argument defines a list of lists of parameter values to pass to the defined model to obtain the multiple simulated responses. The user can optionally just pass a list of parameter values if the user desires to only obtain a single simulated response.
* `alpha_list`: This optional argument defines a list of alpha values to set the transparency of the plotted lines. The default value of this argument is a list of `1.0` values of the same length as `params_list`.
* `clip`: This optional argument tells the function whether to clip the simulated response to the last value of the experimental data. The default value of this argument is `False`.
* `limits_dict`: This optional argument defines the lower and upper bounds of the outputted plot. This argument should be defined as a dictionary of tuples of tuples - e.g., `e.g., {"tensile": ((0, 1), (2, 3)), "creep": ((3, 2), (0,3))}`. The default value for this argument is `None`, meaning that the limits will be determined automatically.

This function relies on the `read_data` and `define_model` functions to be called first. The function will raise an error if any of the defined parameters are invalid for the defined model.

Note that defining the parameters as arguments to this function is similar to fixing the parameters via `fix_params`, meaning that there will be clashes if the parameter values are defined twice.

## Plot the parameter distribution (`plot_distribution`)

The `plot_distribution` function creates a plot of boxplots for multiple sets of parameters.
* `params_list`: This argument defines a list of lists of parameter values to pass to the defined model to obtain the multiple simulated responses. The user can optionally just pass a list of parameter values if the user desires to only obtain a single simulated response.
* `limits_dict`: This optional argument defines the lower and upper bounds of the boxplots. This argument should be defined as a dictionary of tuples (i.e., `(lower, upper)`) with keys corresponding to the names of the parameters of the model. The default value for this argument is `None`, meaning that the limits will be determined automatically.
* `log`: This optional argument tells the function whether to apply the log scale for the boxplots. The default value for this argument is `False`.

## Plotting simulation results (`plot_simulation`)

The `plot_simulation` function creates a `.xlsx` file with information about the optimisation and errors used for a set of parameters.
* `params_list`: This argument defines a list of lists of parameter values to pass to the defined model to obtain the multiple simulated responses. The user can optionally just pass a list of parameter values if the user desires to only obtain a single simulated response.

This function relies on the `read_data` and `define_model` functions to be called first. The function will raise an error if the defined parameters are invalid for the defined model. Additionally, the user can optionally call the `add_error` function beforehand to obtain the error values corresponding to the set of parameter values.

Note that defining the parameters as arguments to this function is similar to fixing the parameters via `fix_params`, meaning that there will be clashes if the parameter values are defined twice.

## Saving the model (`save_model`)

The `save_model` function creates `.xml` files for use in other programs (e.g., Abaqus, MOOSE). The function will output a number of files depending on the number of experimental data has been read by the `read_data` function.
* `params`: This argument defines a list of parameter values to pass to the defined model to obtain the simulated responses.

This function relies on the `read_data` and `define_model` functions to be called first. The function will raise an error if the defined parameters are invalid for the defined model.

Note that defining the parameters as arguments to this function is similar to fixing the parameters via `fix_params`, meaning that there will be clashes if the parameter values are defined twice.

## Recording the results (`set_recorder`)

The `set_recorder` function sets the options for recording the results during the MOGA optimisation.
* `interval`: This optional argument defines the number of generations the MOGA should run before recording the results of the optimisation. The results will be stored in a `.xlsx` file, similar with the `get_results` function. The default value for this argument is `10`.
* `plot_opt`: This optional argument tells the function whether to output a plot of the simulated and experimental results when recording the results. The default value for this argument is `False`.
* `plot_loss`: This optional argument tells the function whether to output the loss history when recording the results. The output will contain a plot as well as a `.csv` file containing the generations and loss. The default value for this argument is `False`.
* `save_model`: This optional argument tells the function whether to save the models when recording the results. The models will be stored in `.xml` files, similar with the `save_model` function.

Note that this function is optional, and the default value will be set without the function being called.

## Running the optimisation (`optimise`)

The `optimise` function conducts the MOGA optimisation.
* `num_gens`: This optional argument defines the number of generations to run the MOGA optimisation. The default value for this argument is `10000`.
* `population`: This optional argument defines the population size. The default value for this argument is `100`.
* `offspring`: This optional argument defines the number of offspring to produce at each generation. The default value for this argument is `50`.
* `crossover`: This optional argument defines the crossover probability when breeding the chromosomes. The default value for this argument is `0.80`, meaning that the crossover probability is 80%.
* `mutation`: This optional argument defines the mutation probability when breeding the chromosomes. The default value for this argument is `0.01`, meaning that the mutation probability is 1%.

The function returns the optimised parameters as a dictionary once the MOGA optimisation finishes.

# Example `moga_neml` scripts

The following section contains some examples of using functions in the `Interface` class.

## Creep model optimisation for one creep curve

```py
# Import moga_neml
import sys; sys.path += [".."]
from moga_neml.interface import Interface

# Initialise Interface and define model
itf = Interface("creep optimisation")
itf.define_model("evpcd")

# Read data and add errors
itf.read_data("creep/inl_1/AirBase_800_80_G25.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")

# Optimise
itf.optimise(
    num_gens   = 100,
    population = 100,
    offspring  = 50,
    crossover  = 0.8,
    mutation   = 0.01
)
```

## Creep model optimisation for two creep curves with validation data

```py
# Import moga_neml
import sys; sys.path += [".."]
from moga_neml.interface import Interface

# Initialise Interface and define model
itf = Interface("creep optimisation with validation")
itf.define_model("evpcd")

# Read first creep curve, add errors, and add constraints
itf.read_data("creep/inl_1/AirBase_800_80_G25.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")
itf.add_constraint("inc_end", "strain")
itf.add_constraint("dec_end", "time")

# Read second creep curve, add errors, and add constraints
itf.read_data("creep/inl_1/AirBase_800_70_G44.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")
itf.add_constraint("inc_end", "strain")
itf.add_constraint("dec_end", "time")

# Add validation data
itf.read_data("creep/inl_1/AirBase_800_65_G33.csv")
itf.read_data("creep/inl_1/AirBase_800_60_G32.csv")

# Optimise
itf.optimise(
    num_gens   = 250,
    population = 100,
    offspring  = 50,
    crossover  = 0.8,
    mutation   = 0.01
)
```

## Creep model optimisation for elastic-plastic model with creep and tensile curves

```py
# Import moga_neml
import sys; sys.path += [".."]
from moga_neml.interface import Interface

# Initialise Interface and define model
itf = Interface("elastic-plastic creep and tensile optimisation")
itf.define_model("evp")

# Read first creep curve, remove damage, and add error
itf.read_data("creep/inl_1/AirBase_800_80_G25.csv")
itf.remove_damage()
itf.add_error("area", "time", "strain")

# Read second creep curve, remove damage, and add error
itf.read_data("creep/inl_1/AirBase_800_70_G44.csv")
itf.remove_damage()
itf.add_error("area", "time", "strain")

# Read tensile, manually remove damage, and add errors
itf.read_data("tensile/inl/AirBase_800_D7.csv")
itf.remove_manual("strain", 0.3)
itf.add_error("yield_point", yield_stress=291)
itf.add_error("area", "strain", "stress")

# Optimise
itf.optimise(
    num_gens   = 250,
    population = 100,
    offspring  = 50,
    crossover  = 0.8,
    mutation   = 0.01
)
```

## Creep optimisation with fixed elastic-plastic parameters

```py
# Import moga_neml
import sys; sys.path += [".."]
from moga_neml.interface import Interface

# Initialise Interface and define model
itf = Interface("fixed creep optimisation")
itf.define_model("evpcd")

# Fix elastic-plastic parameters
itf.fix_param("evp_s0",  17.217)
itf.fix_param("evp_R",   179.74)
itf.fix_param("evp_d",   0.61754)
itf.fix_param("evp_n",   4.4166)
itf.fix_param("evp_eta", 1783.5)

# Read first creep curve and add errors
itf.read_data("creep/inl_1/AirBase_800_80_G25.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")

# Read second creep curve and add errors
itf.read_data("creep/inl_1/AirBase_800_70_G44.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")

# Optimise
itf.optimise(
    num_gens   = 250,
    population = 100,
    offspring  = 50,
    crossover  = 0.8,
    mutation   = 0.01
)
```

## Creep optimisation with initialised elastic-plastic parameters

```py
# Import moga_neml
import sys; sys.path += [".."]
from moga_neml.interface import Interface

# Initialise Interface and define model
itf = Interface("initialised creep optimisation")
itf.define_model("evpcd")

# Initialise elastic-plastic parameters
itf.init_params([17.217, 179.74, 0.61754, 4.4166, 1783.5])

# Read first creep curve and add errors
itf.read_data("creep/inl_1/AirBase_800_80_G25.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")

# Read second creep curve and add errors
itf.read_data("creep/inl_1/AirBase_800_70_G44.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")

# Optimise
itf.optimise(
    num_gens   = 250,
    population = 100,
    offspring  = 50,
    crossover  = 0.8,
    mutation   = 0.01
)
```

## Back-to-back cyclic optimisations with initialised parameters

```py
import sys; sys.path += [".."]
from moga_neml.interface import Interface

# Define model
itf = Interface("ricvih_1")
itf.define_model("ricvih")

# Add cyclic data, change data, remove data after initial stress-strain, and add error
itf.read_data("cyclic/Airbase316.csv", num_points=5000)
itf.change_data("num_cycles", 0)
itf.remove_manual("strain", 0.014)
itf.add_error("area", "strain", "stress", num_points=100)

# First optimisation for initial stress-strain curve
itf.set_recorder(1, plot_opt=True)
opt_params = itf.optimise(50, 100, 50, 0.8, 0.01)

# Redefine model
itf = Interface("ricvih_2")
itf.define_model("ricvih")

# Initialise with initial parameters
for param_name in ["vih_s0", "c_gs1", "c_gs2", "c_cs1", "c_cs2"]:
    itf.fix_param(param_name, opt_params[param_name])

# Add cyclic data and add errors
itf.read_data("cyclic/Airbase316.csv", num_points=5000)
itf.add_error("area_saddle", "time", "strain", num_points=100, tolerance=0.005)
itf.add_error("area_saddle", "time", "stress", num_points=100, tolerance=10.0)
itf.add_error("saddle", "time", "stress")
itf.add_error("num_peaks", "time", "strain")
itf.add_error("end", "time")

# Second optimisation for entire cyclic data
itf.set_recorder(1, plot_opt=True)
opt_params = itf.optimise(100, 100, 50, 0.8, 0.01)
```

## Outputting the experimental data plot, creep simulation plot, error information, and models

```py
# Import moga_neml
import sys; sys.path += [".."]
from moga_neml.interface import Interface

# Initialise Interface and define model
itf = Interface("optimisation results")
itf.define_model("evpcd")

# Read first creep curve and add errors
itf.read_data("creep/inl_1/AirBase_800_80_G25.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")

# Read second creep curve and add errors
itf.read_data("creep/inl_1/AirBase_800_70_G44.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")

# Define parameters
params = [17.217, 179.74, 0.61754, 4.4166, 1783.5, 3109.8, 4.8245, 6.6364]

# Plot experimental data and simulation response
itf.plot_experimental(x_log=True)
itf.plot_simulation(params, x_log=True)

# Get error information and model
itf.get_results(params)
itf.save_model(params)
```