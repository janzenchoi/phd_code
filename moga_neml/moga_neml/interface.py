"""
 Title:         Optimiser Interface
 Description:   Interface for calibrating NEML models
 Author:        Janzen Choi

"""

# Libraries
import re, time
from moga_neml.io.reader import read_exp_data, check_exp_data
from moga_neml.optimise.recorder import Recorder
from moga_neml.optimise.controller import Controller
from moga_neml.optimise.problem import Problem
from moga_neml.optimise.moga import MOGA
from moga_neml.helper.data import remove_data_after
from moga_neml.helper.derivative import remove_after_sp
from moga_neml.helper.experiment import get_units
from moga_neml.helper.general import safe_mkdir

# Interface Class
class Interface:

    def __init__(self, title:str="", input_path:str="./data", output_path:str="./results",
                 verbose:bool=True, output_here:bool=False):
        """
        Class to interact with the optimisation code
        
        Parameters:
        * `title`:       Title of the output folder
        * `input_path`:  Path to the input folder
        * `output_path`: Path to the output folder
        * `verbose`:     If true, outputs messages for each function call
        * `output_here`: If true, just dumps the output in ths executing directory
        """

        # Initialise internal variables
        self.__controller__  = Controller()
        self.__recorder__    = None
        self.__print_index__ = 0
        self.__print_subindex__ = 0
        self.__verbose__     = verbose
        
        # Print starting message
        time_str = time.strftime("%A, %D, %H:%M:%S", time.localtime())
        self.__print__(f"\n  Starting on {time_str}\n", add_index=False)
        
        # Get start time
        self.__start_time__ = time.time()
        time_stamp = time.strftime("%y%m%d%H%M%S", time.localtime(self.__start_time__))
        
        # Define input and output
        self.__input_path__ = input_path
        self.__get_input__  = lambda x : f"{self.__input_path__}/{x}"
        title = "" if title == "" else f"_{title}"
        title = re.sub(r"[^a-zA-Z0-9_]", "", title.replace(" ", "_"))
        self.__output_dir__ = "." if output_here else time_stamp
        self.__output_path__ = "." if output_here else f"{output_path}/{self.__output_dir__}{title}"
        self.__get_output__ = lambda x : f"{self.__output_path__}/{x}"
        
        # Create directories
        if not output_here:
            safe_mkdir(output_path)
            safe_mkdir(self.__output_path__)
    
    def define_model(self, model_name:str, **kwargs) -> None:
        """
        Defines the model to be optimised
        
        Parameters:
        * `model_name`: The name of the model
        * `kwargs`:     Any additional keyword arguments to pass to the model
        """
        self.__print__(f"Defining model '{model_name}'")
        self.__controller__.define_model(model_name, **kwargs)
    
    def read_data(self, file_path:str, thin_data:bool=True, num_points:int=1000) -> None:
        """
        Reads in the experimental data from a file
        
        Parameters:
        * `file_path`:  The name of the file relative to the defined `input_path`
        * `thin_data`:  Whether to thin the data or not
        * `num_points`: How many points to thin the data to
        """
        self.__print__(f"Reading data from '{file_path}'")
        exp_data = read_exp_data(self.__input_path__, file_path, thin_data, num_points)
        self.__controller__.add_curve(exp_data)

    def get_data(self, field:str) -> str:
        """
        Gets the value of a field from the most recently added experimental data

        Parameters:
        * `field`: The field to be accessed

        Returns the value
        """
        self.__print__(f"Accessing the `{field}` field", sub_index=True)
        curve = self.__controller__.get_last_curve()
        exp_data = curve.get_exp_data()
        return exp_data[field]

    def change_data(self, field:str, value) -> None:
        """
        Changes a field in the most recently added experimental data

        Parameters:
        * `field`: The field to be changed
        * `value`: The new value to replace the existing value
        """
        self.__print__(f"Changing the '{field}' field", sub_index=True)
        curve = self.__controller__.get_last_curve()
        exp_data = curve.get_exp_data()
        exp_data[field] = value
        check_exp_data(exp_data)
        curve.set_exp_data(exp_data)

    def remove_damage(self, window:int=0.1, acceptance:float=0.9) -> None:
        """
        Removes the tertiary creep from the most recently added creep curve, by removing the data
        points after the minimum creep rate
        
        Parameters:
        * `window`:     The window ratio to identify the stationary points of the derivative; the actual
                        window size is the product of `window` and the number of data points (1000)
        * `acceptance`: The acceptance value for identifying the nature of stationary points; should
                        have a value between 0.5 and 1.0
        """
        self.__print__(f"Removing the tertiary creep", sub_index=True)
        curve = self.__controller__.get_last_curve()
        if curve.get_type() != "creep":
            raise ValueError("Cannot remove damage because it can only be removed for creep curves!")
        exp_data = curve.get_exp_data()
        exp_data = remove_after_sp(exp_data, "min", "time", "strain", window, acceptance, 0)
        curve.set_exp_data(exp_data)

    def remove_oxidation(self, window:int=0.1, acceptance:float=0.9) -> None:
        """
        Removes the data after the tertiary creep for the most recently added
        
        Parameters:
        * `window`:     The window ratio to identify the stationary points of the derivative; the actual
                        window size is the product of `window` and the number of data points (1000)
        * `acceptance`: The acceptance value for identifying the nature of stationary points; should
                        have a value between 0.5 and 1.0
        """
        self.__print__(f"Removing the oxidised creep", sub_index=True)
        curve = self.__controller__.get_last_curve()
        if curve.get_type() != "creep":
            raise ValueError("Cannot remove oxidised creep because it can only be removed for creep curves!")
        exp_data = curve.get_exp_data()
        exp_data = remove_after_sp(exp_data, "max", "time", "strain", window, acceptance, 0)
        curve.set_exp_data(exp_data)
    
    def remove_manual(self, label:str, value:float) -> None:
        """
        Removes the data for a curve at a specific value
        
        Parameters:
        * `label`: The measurement corresponding to the value (e.g., strain, stress)
        * `value`: The value to start removing data
        """
        curve = self.__controller__.get_last_curve()
        units = get_units(label)
        self.__print__(f"Removing the values after {label} of {value}{units}", sub_index=True)
        exp_data = curve.get_exp_data()
        exp_data = remove_data_after(exp_data, value, label)
        curve.set_exp_data(exp_data)

    def add_error(self, error_name:str, x_label:str="", y_label:str="", weight:float=1, **kwargs) -> None:
        """
        Adds an error to optimise for the most recently added experimental data
        
        Parameters:
        * `error_name`: The name of the error
        * `x_label`:    The measurement on the x-axis (e.g., time, strain)
        * `y_label`:    The measurement on the y-axis (e.g., strain, stress)
        * `weight`:     The factor multipled with the error when the errors are reduced
        * `kwargs`:     Any additional keyword arguments to pass to the model
        """
        
        # Display error information
        labels = f"{x_label}-{y_label}" if x_label != "" and y_label != "" else f"{x_label}" if x_label != "" else ""
        label_str = f"for {labels} " if labels != "" else ""
        weight_str = f"with a weight of {weight}" if weight != 1 else ""
        self.__print__(f"Adding '{error_name}' error {label_str}{weight_str}", sub_index=True)
        
        # Add error to curve
        curve = self.__controller__.get_last_curve()
        curve.add_error(error_name, x_label, y_label, weight, **kwargs)

    def group_errors(self, name:bool=True, type:bool=True, labels:bool=True):
        """
        Sets the options for the grouping of errors into objective functions; if all the parameters
        are set to false, then the errors will be grouped into a single objective function
        
        Parameters:
        * `name`:   If true, the errors will be grouped by their names (e.g., end_value, area)
        * `type`:   If true, the errors will be grouped by the data types (e.g., creep, tensile)
        * `labels`: If true, the errors will be grouped by their measurements (e.g., strain, stress)
        """
        self.__controller__.set_error_grouping(name, type, labels)
        group_str = self.__controller__.get_error_grouping()
        group_str_out = f"based on {group_str}" if group_str != "" else "individually"
        self.__print__(f"Grouping the errors {group_str_out}") # prints after action
    
    def reduce_errors(self, method:str="average"):
        """
        Sets the reduction method to convert a list of error values into a single
        value for each objective function; the reduced values are then optimised
        by the multi-objective genetic algorithm
        
        Parameters:
        * `method`: The reduction method ("sum", "average", "square_sum", "square_average")
        """
        self.__print__(f"Reducing the errors based on {method}")
        self.__controller__.set_error_reduction_method(method)
    
    def reduce_objectives(self, method:str="average"):
        """
        Sets the reduction method to convert a list of objective function values into a
        single value; this single value is for determining the optimal solution in the
        collection of solutions during the optimisation process
        
        Parameters:
        * `method`: The reduction method ("sum", "average", "square_sum", "square_average")
        """
        self.__print__(f"Reducing the objective functions based on {method}")
        self.__controller__.set_objective_reduction_method(method)

    def add_constraint(self, constraint_name:str, x_label:str="", y_label:str="", **kwargs) -> None:
        """
        Adds a constraint to all the curves that prevent a solution from being accepted

        Parameters:
        * `constraint_name`: The name of the constraint
        * `x_label`:    The measurement on the x-axis (e.g., time, strain)
        * `y_label`:    The measurement on the y-axis (e.g., strain, stress)
        * `kwargs`:     Any additional keyword arguments to pass to the model
        """
        self.__print__(f"Adding the {constraint_name} constraint to the optimisation", sub_index=True)
        self.__controller__.add_constraint(constraint_name, x_label, y_label, **kwargs)

    def fix_param(self, param_name:str, param_value:float) -> None:
        """
        Fixes a parameter to a value and stops it from changing during the optimisation
        
        Parameters:
        * `param_name`:  The name of the parameter
        * `param_value`: The value the parameter will be fixed to
        """
        self.__print__("Fixing the '{}' parameter to fixed value of {:0.4}".format(param_name, float(param_value)))
        self.__check_model__()
        self.__controller__.fix_param(param_name, param_value)

    def fix_params(self, param_values:list) -> None:
        """
        Fixes multiple parameters to a list of values to stop them from changing during
        the optimisation; note that the script assumes that the first len(param_values)
        are being fixed

        Parameters:
        * `param_values`: A list of parameter values to be fixed
        """
        self.__print__(f"Fixing the first {len(param_values)} parameters of the model")
        self.__check_model__()
        unfix_param_names = self.__controller__.get_unfix_param_names()
        for i in range(len(param_values)):
            self.__controller__.fix_param(unfix_param_names[i], param_values[i])

    def init_param(self, param_name:str, param_value:float) -> None:
        """
        Gives a parameter an initial value in the initial population of the optimisation
        
        Parameters:
        * `param_name`:  The name of the parameter
        * `param_value`: The value the parameter is initialised to
        """
        self.__print__("Setting the '{}' parameter to an initial value of {:0.4}".format(param_name, float(param_value)))
        self.__check_model__()
        self.__controller__.init_param(param_name, param_value)

    def init_params(self, param_values:list) -> None:
        """
        Initialises multiple parameters to a list of values for the initial population of
        the optimisation; note that the script assumes that the first len(param_values)
        are being initialised

        Parameters:
        * `param_values`: A list of parameter values to be initialised
        """
        self.__print__(f"Initialising the first {len(param_values)} of the model")
        self.__check_model__()
        unfix_param_names = self.__controller__.get_unfix_param_names()
        for i in range(len(param_values)):
            self.__controller__.init_param(unfix_param_names[i], param_values[i])

    def set_custom_driver(self, driver_type:str, **kwargs) -> None:
        """
        Forces the optimiser to use a specific driver instead of one of the defined ones
        
        Parameters:
        * `driver_type`: The driver type
        """
        self.__print__(f"Setting a custom '{driver_type}' driver", sub_index=True)
        curve = self.__controller__.get_last_curve()
        curve.set_custom_driver(driver_type, kwargs)

    def plot_experimental(self, x_log:bool=False, y_log:bool=False) -> None:
        """
        Visualises the experimental data
        
        Parameters:
        * `x_log`: Whether to log the x-axis
        * `y_log`: Whether to log the y-axis
        """
        
        # Display informative message
        self.__print__(f"Visualising the experimental data")
        
        # Iterate through the curves and plot them
        type_list = self.__controller__.get_all_types()
        for type in type_list:
            file_path = self.__get_output__(f"exp_{type}")
            self.__check_curves__("There are no experimental curves to plot!")
            self.__controller__.plot_exp_curves(type, file_path, x_log, y_log)

    def plot_simulation(self, params_list:list, alpha_list:list=None, clip:bool=False, limits_dict:dict=None) -> None:
        """
        Visualises the simulated curves from a set of parameters
        
        Parameters:
        * `params_list`: A list of parameter sets for the model; note that defining the parameters as
                         arguments to this function is similar to fixing the parameters via `fix_params`,
                         meaning that there will be clashes if the parameter values are defined twice.
        * `alpha_list`:  A list of alpha values for the plots
        * `clip`:        Whether to clip the predictions so they end at the same x position as the
                         experimental data
        * `limits_dict`: The lower and upper bound of the plot for the scales; dictionary of tuples of
                         tuples; e.g., {"tensile": ((0, 1), (2, 3)), "creep": ((3, 2), (0,3))}
        """

        # Print out message and check
        params_list = self.__process_params_list__(params_list)
        self.__print__(f"Plotting the predictions for {len(params_list)} sets of parameters")
        self.__check_model__()
        self.__check_curves__("There are no experimental curves to plot!")
        self.__check_params_list__(params_list)

        # Check lower and upper limits for scales
        type_list = self.__controller__.get_all_types()
        if limits_dict != None:
            if len(limits_dict.keys()) != len(type_list):
                raise ValueError("Could not plot because the number of limits do not match the number of types!")
            for limits in limits_dict.values():
                if len(limits) != 2 or limits[0][0] > limits[0][1] or limits[1][0] > limits[1][1]:
                    raise ValueError("Could not plot because the limits are incorrectly defined!")

        # Get default alpha values if not defined
        if alpha_list == None:
            alpha_list = [1.0] * len(params_list)

        # Iterate through types and plot predictions
        for i in range(len(type_list)):
            file_path = self.__get_output__(f"prds_{type_list[i]}")
            x_limits, y_limits = None, None
            if limits_dict != None:
                x_limits = limits_dict[type_list[i]][0]
                y_limits = limits_dict[type_list[i]][1]
            self.__controller__.plot_prd_curves(params_list, alpha_list=alpha_list, clip=clip, type=type_list[i],
                                                file_path=file_path, x_limits=x_limits, y_limits=y_limits)

    def plot_distribution(self, params_list:list, limits_dict:dict=None, log:bool=False, horizontal:bool=True) -> None:
        """
        Visualises the distribution of parameters
        
        Parameters:
        * `params_list`:   A list of parameter sets for the model; note that defining the parameters as
                           arguments to this function is similar to fixing the parameters via `fix_params`,
                           meaning that there will be clashes if the parameter values are defined twice.
        * `limits_dict`:   A dictionary of tuples (i.e., (lower, upper)) defining the scale for each parameter
        * `log`:           Whether to apply log scale or not
        * `horizontal`:    Whether to plot the boxplots horizontally (or vertically)
        """

        # Print out message and check
        params_list = self.__process_params_list__(params_list)
        self.__print__(f"Plotting the distributions for {len(params_list)} sets of parameters")
        self.__check_curves__("There are no experimental curves to plot!")
        self.__check_params_list__(params_list)
        
        # Check lower and upper limits for scales
        if limits_dict != None:
            input_params = list(limits_dict.keys())
            model_params = self.__controller__.get_unfix_param_names()
            if not all(x in input_params for x in model_params) or not all(x in model_params for x in input_params):
                raise ValueError("Could not plot because the defined parameters do not match the model's parameters!")
            for limits in limits_dict.values():
                if len(limits) != 2 or limits[0] > limits[1]:
                    raise ValueError("Could not plot because the limits are incorrectly defined!")
        
        # Plot the boxplots
        file_path = self.__get_output__(f"box_plot.png")
        self.__controller__.plot_distribution(params_list, file_path, limits_dict, log, horizontal)

    def get_results(self, params_list:list) -> None:
        """
        Gets the optimisation, parameter, and error summary from a set of parameters
        
        Parameters:
        * `params_list`: A list of parameter sets for the model; note that defining the parameters as
                         arguments to this function is similar to fixing the parameters via `fix_params`,
                         meaning that there will be clashes if the parameter values are defined twice.
        """
        
        # Display and check
        params_list = self.__process_params_list__(params_list)
        self.__print__(f"Getting the results for {len(params_list)} sets of parameters")
        self.__check_model__()
        self.__check_curves__("There are no experimental curves to plot!")
        self.__check_params_list__(params_list)

        # Initialise recorder
        recorder = Recorder(self.__controller__, 0, self.__output_path__)
        recorder.define_hyperparameters(0, len(params_list), 0, 0, 0)
        
        # Add parameters and create record
        for params in params_list:
            param_name_list = self.__controller__.get_unfix_param_names()
            param_value_dict = {key: value for key, value in zip(param_name_list, params)}
            error_value_dict = self.__controller__.calculate_objectives(*params, include_validation=True)
            recorder.update_optimal_solution(param_value_dict, error_value_dict)
        recorder.create_record(self.__get_output__("results"), replace=False)
    
    def save_model(self, params:list) -> None:
        """
        Calibrates the model with parameters and saves the model as an XML file
        
        Parameters:
        * `params`: The parameter values of the model; note that defining the parameters as
                    arguments to this function is similar to fixing the parameters via `fix_params`,
                    meaning that there will be clashes if the parameter values are defined twice.
        """

        # Display and check
        param_str = ["{:0.4}".format(float(param)) for param in params]
        self.__print__("Saving the calibrated model for {}".format(str(param_str).replace("'", "")))
        self.__check_model__()
        self.__check_curves__("Results cannot obtained without experimental curves!")
        self.__check_params__(params)

        # Save the model
        recorder = Recorder(self.__controller__, 0, self.__output_path__, "")
        recorder.define_hyperparameters(0, 1, 0, 0, 0)
        recorder.save_calibrated_model(list(params))
    
    def set_recorder(self, interval:int=10, plot_opt:bool=False, plot_loss:bool=False,
                     save_model:bool=False) -> None:
        """
        Sets the options for the results recorder
        
        Parameters:
        * `interval`:   The number of generations for which the most updated results will
                        be generated
        * `plot_opt`:   Whether to plot the best plot after every update
        * `plot_loss`:  Whether to plot the loss history after every update
        * `save_model`: Whether to save the best calibrated model
        """
        self.__print__(f"Initialising the recorder with an interval of {interval}")
        self.__recorder__ = Recorder(self.__controller__, interval, self.__output_path__,
                                     plot_opt, plot_loss, save_model)
    
    def optimise(self, num_gens:int=10000, population:int=100, offspring:int=50,
                 crossover:float=0.80, mutation:float=0.01) -> dict:
        """
        Prepares and conducts the optimisation
        
        Parameters:
        * `num_gens`:   The number of generations to optimise
        * `population`: The number of solutions in the initial population
        * `offspring`:  The number of solutions introduced after each generation
        * `crossover`:  The crossover probability; should be between 0.0 and 1.0
        * `mutation`:   The mutation probability; should be between 0.0 and 1.0
        """
        
        # Display and conduct checks
        self.__print__(f"Conducting the optimisation ({num_gens}, {population}, {offspring}, {crossover}, {mutation})")
        self.__check_model__()
        self.__check_curves__("Optimisation cannot run without experimental curves!")
        self.__check_errors__("Optimisation cannot run without any objective functions!")
        
        # Adds the recorder if it has not been defined; otherwise, check defined recorder
        if self.__recorder__ == None:
            self.__recorder__ = Recorder(self.__controller__, 10, self.__output_path__)
        self.__check_variable__(self.__recorder__, "Optimisation cannot run without initialising a recorder!")
        
        # Initialise and run the optimisation
        problem = Problem(self.__controller__, self.__recorder__)
        self.__recorder__.define_hyperparameters(num_gens, population, offspring, crossover, mutation)
        moga = MOGA(problem, num_gens, population, offspring, crossover, mutation)
        moga.optimise()

        # Get the results, print, and return the parameters
        opt_params = self.__recorder__.get_opt_params()
        opt_error = self.__recorder__.get_opt_error()
        print(f"\n\tParams:\t{opt_params}\n\tError:\t{opt_error}")
        return opt_params

    def __print__(self, message:str, add_index:bool=True, sub_index:bool=False) -> None:
        """
        Displays a message before running the command (for internal use only)
        
        Parameters:
        * `message`:   the message to be displayed
        * `add_index`: if true, adds a number at the start of the message
        * `sub_index`: if true, adds a number as a decimal
        """
        
        # Special printing cases
        if not self.__verbose__:
            return
        if not add_index:
            print(message)
            return
        
        # Prints with an index / subindex
        if sub_index:
            self.__print_subindex__ += 1
            print_index = f"     {self.__print_index__}.{self.__print_subindex__}"
        else:
            self.__print_index__ += 1
            self.__print_subindex__ = 0
            print_index = f"{self.__print_index__}"
        print(f"   {print_index})\t{message} ...")

    def __process_params_list__(self, params_list:list) -> list:
        """
        Converts a list of parameters into a list of parameter sets

        Parameters:
        * `params_list`: The list of parameters

        Returns the new parameter list 
        """
        if not isinstance(params_list[0], list):
            params_list = [params_list]
        return params_list

    def __check_model__(self) -> None:
        """
        Checks whether the model has been defined
        """
        if self.__controller__.model == None:
            raise ValueError("The model must be defined first!")

    def __check_curves__(self, message:str) -> None:
        """
        Checks the experimental data
        
        Parameters:
        * `message`: The message to display if error is raised
        """
        curve_list = self.__controller__.get_curve_list()
        if len(curve_list) == 0:
            raise ValueError(message)
        
    def __check_errors__(self, message:str) -> None:
        """
        Checks the errors
        
        Parameters:
        * `message`: The message to display if error is raised
        """
        curve_list = self.__controller__.get_curve_list()
        num_errors = [len(curve.get_error_list()) for curve in curve_list]
        if sum(num_errors) == 0:
            raise ValueError(message)
    
    def __check_variable__(self, variable, message:str) -> None:
        """
        Checks that a variable has been initialised
        
        Parameters:
        * `variable`: The variable to check
        * `message`:  The message to display if error is raised
        """
        if variable == None:
            raise ValueError(message)
    
    def __check_params__(self, params:list) -> None:
        """
        Checks whether a set of parameters is valid
        
        Parameters:
        * `params`: The parameter values for the model
        """
        param_name_list = self.__controller__.get_unfix_param_names()
        if len(params) != len(param_name_list):
            message = f"The number of input parameters ({len(params)}) do not match the "
            message += f"number of parameters in the model ({len(param_name_list)})!"
            raise ValueError(message)

    def __check_params_list__(self, params_list:list) -> None:
        """
        Checks whether a list of parameter sets is valid
        
        Parameters:
        * `params_list`: A list of parameter sets for the model
        """
        if len(params_list) == 0:
            raise ValueError("No parameters have been defined!")
        for params in params_list:
            self.__check_params__(params)

    def __del__(self):
        """
        Prints out the final message (for internal use only)
        """
        time_str = time.strftime("%A, %D, %H:%M:%S", time.localtime())
        duration = round(time.time() - self.__start_time__)
        duration_h = duration // 3600
        duration_m = (duration - duration_h * 3600) // 60
        duration_s = duration - duration_h * 3600 - duration_m * 60
        duration_str_list = [
            f"{duration_h} hours" if duration_h > 0 else "",
            f"{duration_m} mins" if duration_m > 0 else "",
            f"{duration_s} seconds" if duration_s > 0 else ""
        ]
        duration_str = ", ".join([d for d in duration_str_list if d != ""])
        self.__print__(f"\n  Finished on {time_str} in {duration_str}\n", add_index=False)