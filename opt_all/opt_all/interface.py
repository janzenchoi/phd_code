"""
 Title:         Optimiser Interface
 Description:   Interface for calibrating models
 Author:        Janzen Choi

"""

# Libraries
import inspect, re, time
from opt_all.helper.general import safe_mkdir, get_thinned_list
from opt_all.optimise.controller import Controller
from opt_all.io.reader import read_exp_data

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
        self.__controller__  = Controller(verbose)
        self.__print_index__ = 0
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
        file_path = inspect.currentframe().f_back.f_code.co_filename
        file_name = file_path.split("/")[-1].replace(".py","")
        title = f"_{file_name}" if title == "" else f"_{title}"
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
        Defines a model for the optimisation

        Parameters:
        * `model_name`: The name of the model
        """
        self.__print__(f"Defining the '{model_name}' model")
        self.__controller__.define_model(model_name, **kwargs)

    def bind_param(self, param_name:str, lower_bound:float, upper_bound:float) -> None:
        """
        Sets the bounds of a parameter to be optimised
        
        Parameters:
        * `param_name`:  The name of the parameter
        * `lower_bound`: The lower bound of the parameter
        * `upper_bound`: The upper bound of the parameter
        """
        self.__print__(f"Binding '{param_name}' to ({lower_bound}, {upper_bound})", sub_index=True)
        self.__check_model__()
        self.__controller__.bind_param(param_name, lower_bound, upper_bound)

    def fix_param(self, param_name:str, param_value:float) -> None:
        """
        Fixes a parameter to a value during the optimisation
        
        Parameters:
        * `param_name`:  The parameter to be fixed
        * `param_value`: The value the parameter will be fixed to
        """
        self.__print__(f"Fixing '{param_name}' to {param_value}", sub_index=True)
        self.__check_model__()
        self.__controller__.fix_param(param_name, param_value)

    def init_param(self, param_name:str, param_value:float) -> None:
        """
        Initialises a parameter to a value at the start of the optimisation
        
        Parameters:
        * `param_name`:  The parameter to be initialised
        * `param_value`: The value the parameter will be initialised to
        """
        self.__print__(f"Initialising '{param_name}' to {param_value}", sub_index=True)
        self.__check_model__()
        self.__controller__.init_param(param_name, param_value)

    def read_data(self, file_path:str) -> None:
        """
        Reads in the experimental data from a file
        
        Parameters:
        * `file_path`:  The name of the file relative to the defined `input_path`
        * `thin_data`:  Whether to thin the data or not
        * `num_points`: How many points to thin the data to
        """
        self.__print__(f"Reading data from '{file_path}'")
        exp_data = read_exp_data(self.__input_path__, file_path)
        self.__controller__.add_curve(exp_data)

    def sparsen_data(self, new_size:int) -> None:
        """
        Sparsens the most recently added data

        Parameters:
        * `num_points`: New size for the data

        Returns the sparsened datasets
        """
        self.__print__(f"Sparsening the data to {new_size} points", sub_index=True)
        curve = self.__controller__.get_last_curve()
        exp_data = curve.get_exp_data()
        for field in exp_data.keys():
            if isinstance(exp_data[field], list):
                exp_data[field] = get_thinned_list(exp_data[field], new_size)
        curve.set_exp_data(exp_data)
    
    def get_data(self) -> dict:
        """
        Gets the dictionary of the most recently added experimental data
        """
        self.__print__(f"Retrieving the most recently added data", sub_index=True)
        curve = self.__controller__.get_last_curve()
        return curve.get_exp_data()

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
        curve.set_exp_data(exp_data)
    
    def remove_after(self, field:str, value:float) -> None:
        """
        Removes data for a field after a defined value
        
        Parameters:
        * `field`: The field for which data will be removed from
        * `value`: The value after which data will be removed
        """
        self.__print__(f"Manually removing data after {field} == {value}", sub_index=True)
        curve = self.__controller__.get_last_curve()
        curve.remove_data(field, value, after=True)
    
    def remove_before(self, field:str, value:float) -> None:
        """
        Removes data for a field before a defined value
        
        Parameters:
        * `field`: The field for which data will be removed from
        * `value`: The value after which data will be removed
        """
        self.__print__(f"Manually removing data before {field} == {value}", sub_index=True)
        curve = self.__controller__.get_last_curve()
        curve.remove_data(field, value, after=False)

    def add_error(self, error_name:str, labels:list=None, weight:float=1.0, group:str=None, **kwargs) -> None:
        """
        Adds an error to optimise for the most recently added experimental data
        
        Parameters:
        * `error_name`: The name of the error
        * `labels`:     The list of labels (e.g., time, strain)
        * `weight`:     The factor multipled with the error when the errors are reduced
        * `kwargs`:     Any additional keyword arguments to pass to the model
        """
        self.__print__(f"Adding '{error_name}' error", sub_index=True)
        curve = self.__controller__.get_last_curve()
        labels = [] if labels == None else labels
        curve.add_error(error_name, labels, weight, str(group), **kwargs)

    def set_function(self, function) -> None:
        """
        Runs a custom function during recording; function arguments must have
        exactly three arguments: dictionary containing experimental data,
        dictionary containing simulated data, and the path to the output folder.

        Parameters:
        * `function`: The function to run
        """
        self.__print__(f"Setting up a function to run during recording", sub_index=True)
        num_args = len(inspect.signature(function).parameters)
        if num_args != 3:
            raise ValueError(f"Defined function must have exactly three arguments ({num_args})!")
        curve = self.__controller__.get_last_curve()
        curve.add_function(function)
        
    def set_reduction_method(self, reduction_method) -> None:
        """
        Sets the reduction method; if not defined, uses np.average

        Parameters:
        * `reduction_method`: Function handler for reduction method
        """
        self.__print__("Setting custom reduction method for the optimisation")
        self.__controller__.set_reduction_method(reduction_method)

    def start_recorder(self, storage:int=10, interval:int=1000, export:bool=False) -> None:
        """
        Outputs the results

        Parameters:
        * `storage`:  The number of solutions to store
        * `interval`: The number of evaluations for each record
        * `export`:   Whether to export data during recording or not
        """
        self.__print__(f"Setting the recorder for the optimisation")
        self.__controller__.start_recorder(self.__output_path__, storage, interval, export, self.__verbose__)        

    def record_plot(self, x_field:str, y_field:str, x_units:str="", x_scale:float=1.0,
                    y_scale:float=1.0, y_units:str="", x_limits:tuple=None,
                    y_limits:tuple=None, file_name:str="", conditions:dict={}) -> None:
        """
        Plots the fitting results during recording

        Parameters:
        * `x_field`:    Field to use for the x-axis
        * `y_field`:    Field to use for the y-axis
        * `x_scale`:    Factor to apply to x values
        * `y_scale`:    Factor to apply to y values
        * `x_limits`:   Limits to apply on the x-axis
        * `y_limits`:   Limits to apply on the y-axis
        * `file_name`:  Custom name for the plot file
        * `conditions`: Conditions to constrain plotting
        """
        self.__print__(f"Setting up plot for the {y_field}-{x_field} curves during recording")
        self.__check_recorder__()
        file_name = file_name if file_name != "" else "plot_fit"
        plot_path = self.__get_output__(file_name)
        self.__controller__.recorder.add_plot_record(x_field, y_field, x_scale, y_scale,
                                                     x_units, y_units, x_limits, y_limits,
                                                     plot_path, conditions)

    def optimise(self, optimiser_name:str, **kwargs) -> None:
        """
        Defines an optimiser and conducts the optimisation

        Parameters:
        * `optimiser_name`: The name of the optimiser
        """
        self.__print__(f"Conducting the optimisation with the '{optimiser_name}' optimiser")
        self.__check_model__()
        self.__check_curves__("There are no experimental curves to optimise!")
        self.__check_errors__("Optimisation cannot run without any objective functions!")
        self.__controller__.optimise(optimiser_name, **kwargs)

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

    def __check_params__(self, params:list) -> None:
        """
        Checks whether a set of parameters is valid
        
        Parameters:
        * `params`: The parameter values for the model
        """
        param_names = self.__controller__.get_param_names()
        if len(params) != len(param_names):
            message = f"The number of input parameters ({len(params)}) do not match the "
            message += f"number of parameters in the model ({len(param_names)})!"
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

    def __check_recorder__(self) -> None:
        """
        Checks that the recorder has been started
        """
        if self.__controller__.recorder == None:
            raise ValueError("The recorder has not been started!")

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
