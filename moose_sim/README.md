# Simulator for DEER

For running material simulations using DEER. The following README file was last updated on the 24th of July, 2024.

# Importing `moose_sim`

The user can add the `moose_sim` package to the system path so that they can import the code anywhere on their machine. This involves simply adding the following line to the `~/.bashrc` file, as follows. Note that `<path_to_moose_sim>` refers to the absolute path to the `moose_sim` directory.
```
export PYTHONPATH=$PYTHONPATH:<path_to_moose_sim>
```

Alternatively, the user can import `moose_sim` dynamically depending on the relative path between the main `moose_sim` directory and their script. For instance, if the user wants to run a script in the `moose_sim/scripts/` directory, they can use the following.
```
import sys; sys.path += [".."]
import moose_sim
```

# Interacting with `moose_sim`

The following section provides a tutorial on using the `moose_sim` code.

## Interface Class

The `Interface` class allows the user to interact with the `moose_sim` code. To access the `Interface` class, the user must first import the `moose_sim` package and initialise an `Interface` object. The following is an example of doing so from the `moose_sim/scripts/` directory.
```py
import sys; sys.path += [".."]
from moose_sim import Interface
itf = Interface()
```

The `Interface` class contains several optional arguments. These include:
* `title`: This optional argument appends a title in front of the directory in which the output files will be placed in. The default value for this argument is an empty string.
* `input_path`: This optional argument defines the relative path to the input directory, which tells the script where to read the input files. The default value for this argument is `"./data"`.
* `output_path`: This optional argument defines the relative path to the output directory, which tells the script where to place the output files. The default value for this argument is `"./results"`.
* `verbose`: This optional argument tells the script whether to display any information about the actions of the `Interface` class in the terminal. The default value for this argument is `True`, meaning that the information will be displayed in the terminal.
* `output_here`: This optional argument tells the script whether to just place the output files in the same directory as the script. The default value for this is `False`. Note that when the user sets the argument to `True`, the `title` and `output_path` values will not have any effect.

The implementation of the `Interface` class can be accessed via `moose_sim/moose_sim/interface.py`. The next sections provide descriptions of the available functions, their available arguments, and how to use them. Note that additional descriptions of the `Interface` functions can also be accessed by hovering your cursor over the functions. However, this functionality is only supported by some IDEs (e.g., Visual Studio Code).

## Defining the mesh (`define_mesh`)

The `define_mesh` function defines the mesh to run the simulation on.

Parameters:
* `mesh_file`:        The name of the mesh file.
* `orientation_file`: The name of the orientation file.
* `degrees`:          Whether the orientation data is in degrees (or radians); the default value is `True`, which indicates that the data is in degrees.
* `active`:           Whether the orientation data is active (or passive); the default value is `True`, which indicates that the data is in active rotation.

## Defining the material (`define_material`)

The `define_material` function defines the name and parameters of the material.

Parameters:
* `material_name`:   The name of the material.
* `material_params`: Dictionary of parameter values.

The user can additionally enter custom arguments to pass through custom material files.

## Defining the material (`define_simulation`)

The `define_simulation` function defines the name and parameters of the simulation.

Parameters:
* `simulation_name`:   The name of the simulation.
* `simulation_params`: Dictionary of parameter values.

The user can additionally enter custom arguments to pass through custom material files.

## Running the simulation (`simulate`)

The `simulate` function runs the simulation.

Parameters:
* `opt_path`:       Path to the *-opt executable.
* `num_processors`: The number of processors.
* `timeout`:        The maximum amount of time (in seconds) to run the simulation.

## Exporting the parameters (`export_params`)

The `export_params` function exports the material and simulation parameters to a CSV file.

Parameters:
* `params_file`: The name of the parameter file. The default value is `"params.txt"`.

## Compressing the output (`compress_csv`)

The `compress_csv` function compresses the CSV output of simulation by rounding the values to certain significant figures.

Parameters:
* `sf`:      The significant figures to round the values.
* `exclude`: The fields to exclude in the compressed results.

## Conduct post processing (`post_process`)

The `post_process` function conducts post processing after the simmulation has been completed. Note that the post processing is reliant on the implementation of the `post_process` function in defined simulation (via `define_simulation`).

Parameters:
* `sim_path`: The path to conduct the post processing; uses current result path if undefined.

The user can additionally enter custom arguments to pass through custom material files.

## Removing unnecessary files (`remove_files`)

The `remove_files` function removes certain files after the simulation ends.

Parameters:
* `keyword_list`: List of keywords to remove files. For instance, if the value is `["results"]`, then all files (and folders) that have `"results"` in their names will be recursively removed.

Use this function carefully as it may cause catastrophic damage if used incorrectly.

