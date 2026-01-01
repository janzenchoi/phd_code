"""
 Title:         Problem
 Description:   For defining the MOGA problem
 Author:        Janzen Choi

"""

# Libraries
import warnings
import numpy as np
from pymoo.core.problem import ElementwiseProblem
from moga_neml.optimise.controller import Controller
from moga_neml.optimise.recorder import Recorder

# The Problem class
class Problem(ElementwiseProblem):

    def __init__(self, controller:Controller, recorder:Recorder):
        """
        Class for defining the problem

        Parameters:
        * `controller`: The controller used to control the optimisation
        * `recorder`:   The recorder used to record the results during the optimisation
        """

        # Initialise
        self.controller = controller
        self.recorder   = recorder
        
        # Get parameter information
        unfix_param_dict = self.controller.get_unfix_param_dict()
        l_bound_list = [unfix_param_dict[param_name]["l_bound"] for param_name in unfix_param_dict.keys()]
        u_bound_list = [unfix_param_dict[param_name]["u_bound"] for param_name in unfix_param_dict.keys()]
        self.unfixed_param_names = list(unfix_param_dict.keys())
        
        # Define the element wise problem
        super().__init__(
            n_var = len(unfix_param_dict.keys()),
            n_obj = len(self.controller.get_objective_info_list()),
            xl    = np.array(l_bound_list),
            xu    = np.array(u_bound_list),
        )
    
    def get_controller(self) -> Controller:
        """
        Gets the controller
        """
        return self.controller
    
    def get_recorder(self) -> Recorder:
        """
        Gets the recorder
        """
        return self.recorder
    
    def get_param_value_dict(self, params:tuple) -> dict:
        """
        Creates the parameter dictionary

        Parameters:
        * `params`: A list of the parameter values

        Returns the dictionary of parameters
        """
        param_dict = self.controller.get_model().get_param_dict()
        param_value_dict = {}
        for i in range(len(params)):
            param_name = param_dict[list(param_dict.keys())[i]]
            param_value_dict[param_name] = params[i]
        return param_value_dict
    
    def _evaluate(self, params:tuple, out:dict, *args, **kwargs) -> None:
        """
        Minimises expression "F" such that the expression "G <= 0" is satisfied

        Parameters:
        * `params`: A list of the parameter values
        * `out`:    The dictionary to attach the error values
        """

        # Ignore warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Get error values
            error_value_dict = self.controller.calculate_objectives(*params)
            out["F"] = list(error_value_dict.values())
            
            # Get parameter values and update recorder
            param_value_dict = {key: value for key, value in zip(self.unfixed_param_names, params)}
            self.recorder.update_iteration(param_value_dict, error_value_dict)
            