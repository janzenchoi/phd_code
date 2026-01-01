"""
 Title:         The Controller class
 Description:   The intermediary between the interface and the rest of the code
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from opt_all.optimise.curve import Curve
from opt_all.optimise.recorder import Recorder
from opt_all.optimisers.__optimiser__ import create_optimiser
from opt_all.models.__model__ import create_model

# Constants
BIG_VALUE = 1e3

# The Controller Class
class Controller:

    def __init__(self, verbose:bool=True):
        """
        Initialises the Controller class to control the optimisation components
        
        Parameters:
        * `verbose`: Whether to display progress messages
        """
        self.verbose          = verbose
        self.model            = None
        self.param_names      = []
        self.bind_param_dict  = {}
        self.fix_param_dict   = {}
        self.init_param_dict  = {}
        self.curve_list       = []
        self.recorder         = None
        self.optimiser        = None
        self.reduction_method = lambda errors : np.average(errors)

    def define_model(self, model_name:str, **kwargs) -> None:
        """
        Defines a model for the optimisation

        Parameters:
        * `model_name`: The name of the model
        """
        if self.model != None:
            raise ValueError(f"The '{self.model.get_name()}' has already been defined!")
        self.model = create_model(model_name, **kwargs)
        self.param_names = self.model.get_param_names()

    def get_param_names(self) -> list:
        """
        Returns a list of the model's parameter names
        """
        return self.param_names

    def bind_param(self, param_name:str, lower_bound:float, upper_bound:float) -> None:
        """
        Sets the bounds of a parameter to be optimised
        
        Parameters:
        * `param_name`:  The name of the parameter
        * `lower_bound`: The lower bound of the parameter
        * `upper_bound`: The upper bound of the parameter
        """
        self.__check_param__(param_name, check_bind=True, check_fix=True)
        self.bind_param_dict[param_name] = (lower_bound, upper_bound)

    def fix_param(self, param_name:str, param_value:float) -> None:
        """
        Fixes a parameter to a value during the optimisation
        
        Parameters:
        * `param_name`:  The parameter to be fixed
        * `param_value`: The value the parameter will be fixed to
        """
        self.__check_param__(param_name, check_bind=True, check_fix=True, check_init=True)
        self.fix_param_dict[param_name] = param_value

    def init_param(self, param_name:str, param_value:float) -> None:
        """
        Initialises a parameter to a value at the start of the optimisation
        
        Parameters:
        * `param_name`:  The parameter to be initialised
        * `param_value`: The value the parameter will be initialised to
        """
        self.__check_param__(param_name, check_fix=True, check_init=True)
        self.init_param_dict[param_name] = param_value

    def get_bound_params(self) -> dict:
        """
        Returns the dictionary of bound parameters
        """
        return self.bind_param_dict

    def get_fixed_params(self) -> dict:
        """
        Returns the dictionary of fixed parameters
        """
        return self.fix_param_dict

    def get_inited_params(self) -> dict:
        """
        Returns the dictionary of initialised parameters
        """
        return self.init_param_dict

    def add_curve(self, exp_data:dict) -> None:
        """
        Adds an experimental curve to the controller
        
        Parameters:
        * `exp_data`: The corresponding experimental data
        """
        curve = Curve(exp_data, self.model)
        self.curve_list.append(curve)

    def get_curve_list(self) -> list:
        """
        Gets the list of curves
        """
        return self.curve_list

    def get_last_curve(self) -> Curve:
        """
        Returns the most recently added curve
        """
        if self.curve_list == []:
            raise ValueError("No curves have been added yet!")
        return self.curve_list[-1]

    def get_response(self, *params, curve:Curve) -> dict:
        """
        Gets the response from the model

        Parameters:
        * `curve`:  The curve to use to get the response
        * `params`: The parameters for the prediction

        Returns a dictionary of the response
        """

        # Get the model's response
        self.model.set_exp_data(curve.get_exp_data())
        response = self.model.get_response(*params)
        
        # Check the model's response
        if response == None:
            return
            
        # Return if valid
        return response
        
    def get_error_groups(self) -> list:
        """
        Returns the list of the error groups;
        groups by names if not defined
        """
        errors = [curve.get_error_list() for curve in self.curve_list]
        error_groups = [e.get_group() for sub_list in errors for e in sub_list]
        error_groups = list(set(error_groups))
        return error_groups

    def incorporate_fixed_params(self, *params:tuple) -> list:
        """
        Incorporates the fixed parameters

        Parameters:
        * `params`: The parameters
        """
        params = list(params)
        param_names = self.model.get_param_names()
        fix_indexes = [i for i in range(len(param_names)) if param_names[i] in self.fix_param_dict.keys()]
        for fix_index in fix_indexes:
            fix_value = self.fix_param_dict[param_names[fix_index]]
            params.insert(fix_index, fix_value)
        return tuple(params)

    def calculate_errors(self, *params:tuple, update:bool=True) -> dict:
        """
        Calculates the error values for a set of parameters

        Parameters:
        * `params`: The parameters for the prediction
        * `update`: Whether to update the record with the parameters

        Returns a dictionary of the errors
        """

        # Initialise
        params = self.incorporate_fixed_params(*params)
        error_groups = self.get_error_groups()
        empty_list_list = [[] for _ in range(len(error_groups))]
        error_dict = {key: value for key, value in zip(error_groups, empty_list_list)}
        failed_dict = {key: value for key, value in zip(error_groups, [BIG_VALUE] * len(error_groups))}

        # Get model responses
        curve_list = [curve for curve in self.curve_list if not curve.is_validation()]
        response_list = [self.get_response(*params, curve=curve) for curve in curve_list]
        if None in response_list:
            return failed_dict

        # Iterate through experimental data
        for i, curve in enumerate(curve_list):
            error_list = curve.get_error_list()
            for error in error_list:
                error_value = error.get_value(response_list[i])
                error_value = error_value * error.get_weight() if error_value != None else BIG_VALUE
                error_dict[error.get_group()].append(error_value)

        # Reduce the errors
        reduced_error_dict = {}
        for error_group in error_groups:
            reduced_error_dict[error_group] = self.reduction_method(error_dict[error_group])
        
        # Update the recorder and return the reduced errors
        if update:
            self.recorder.update(list(params), list(reduced_error_dict.values()))
        return reduced_error_dict

    def set_reduction_method(self, reduction_method) -> None:
        """
        Sets the reduction method; if not defined, uses np.average

        Parameters:
        * `reduction_method`: Function handler for reduction method
        """
        self.reduction_method = reduction_method

    def reduce_errors(self, errors:list) -> float:
        """
        Reduces a list of errors into a single value
        
        Parameters:
        * `errors`: The list of errors

        Returns the reduced value
        """
        return self.reduction_method(errors)

    def start_recorder(self, output_path:str, storage:int=10, interval:int=1000,
                       export:bool=False, verbose:bool=True) -> None:
        """
        Initialises the recorder class

        Parameters:
        * `output_path`: The path to the output directory
        * `storage`:     The number of solutions to store
        * `interval`:    The number of evaluations for each record
        * `export`:      Whether to export data during recording or not
        * `verbose`:     Whether to output the recording progress
        """
        self.recorder = Recorder(self, output_path, storage, interval, export, verbose)

    def optimise(self, optimiser_name:str, **kwargs) -> None:
        """
        Defines an optimiser and conducts the optimisation

        Parameters:
        * `optimiser_name`: The name of the optimiser
        """
        if self.recorder == None:
            self.start_recorder()
        self.optimiser = create_optimiser(optimiser_name, self, **kwargs)
        if self.verbose:
            print()
        self.optimiser.optimise()
        if self.verbose:
            print()
        self.recorder.output_results()

    def __check_param__(self, param_name:str, check_bind:bool=False, check_fix:bool=False, check_init:bool=False) -> None:
        """
        Checks whether a parameter can be bound, fixed, or initialised

        Parameters:
        * `param_name`: The name of the parameter
        * `check_bind`: Whether to check if the parameters have been bound
        * `check_fix`:  Whether to check if the parameters have been fixed
        * `check_init`: Whether to check if the parameters have been initialised
        """
        if not param_name in self.param_names:
            raise ValueError(f"The '{param_name}' parameter is not defined in the '{self.model.get_name()}' model!")
        if check_bind and param_name in self.bind_param_dict.keys():
            raise ValueError(f"The '{param_name}' parameter has already been bound!")
        if check_fix and param_name in self.fix_param_dict.keys():
            raise ValueError(f"The '{param_name}' parameter has already been fixed!")
        if check_init and param_name in self.init_param_dict.keys():
            raise ValueError(f"The '{param_name}' parameter has already been initialised!")
