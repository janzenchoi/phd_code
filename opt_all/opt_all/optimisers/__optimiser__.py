"""
 Title:         Optimiser Template
 Description:   Contains the basic structure for an optimiser class
 Author:        Janzen Choi

"""

# Libraries
import importlib, os, pathlib, sys

# The Optimiser Template Class
class __Optimiser__:

    def __init__(self, name:str, controller):
        """
        Class for defining an optimiser
        
        Parameters:
        * `name`:       The name of the optimiser
        * `controller`: The controller object
        """
        self.name = name
        self.controller = controller

    def get_name(self) -> str:
        """
        Gets the name of the optimiser
        """
        return self.name

    def get_param_names(self) -> list:
        """
        Returns a list of the model's parameter names
        """
        return self.controller.get_param_names()

    def get_error_groups(self) -> list:
        """
        Returns a list of the error groups
        """
        return self.controller.get_error_groups()

    def calculate_errors(self, *params): # -> function handle
        """
        Returns the controller's function handler for calculating the errors
        """
        return self.controller.calculate_errors(*params)

    def get_fixed_params(self) -> dict:
        """
        Returns the dictionary of fixed parameters
        """
        return self.controller.get_fixed_params()
    
    def get_unfixed_params(self) -> list:
        """
        Returns a list of unfixed parameter names
        """
        all_param_names   = self.controller.model.get_param_names()
        fix_param_dict    = self.controller.get_fixed_params()
        unfix_param_names = [param_name for param_name in all_param_names if not param_name in fix_param_dict.keys()]
        return unfix_param_names

    def get_inited_params(self) -> dict:
        """
        Returns the dictionary of initialised parameters
        """
        return self.controller.get_inited_params()

    def get_bound_params(self) -> dict:
        """
        Returns a dictionary of the parameter bounds as tuples
        """
        return self.controller.get_bound_params()

    def initialise(self) -> None:
        """
        Runs at the start, once (must be overridden)
        """
        raise NotImplementedError

    def optimise(self): # -> Optimiser
        """
        Conducts the optimisation (must be overridden)
        """
        raise NotImplementedError

def create_optimiser(optimiser_name:str, controller, **kwargs) -> __Optimiser__:
    """
    Creates and return an optimiser

    Parameters:
    * `optimiser_name`: The name of the optimiser
    * `controller`:     The controller object

    Returns the optimiser
    """

    # Get available optimisers in current folder
    optimisers_dir = pathlib.Path(__file__).parent.resolve()
    files = os.listdir(optimisers_dir)
    files = [file.replace(".py", "") for file in files]
    files = [file for file in files if not file in ["__optimiser__", "__pycache__"]]
    
    # Raise error if optimiser name not in available optimisers
    if not optimiser_name in files:
        raise NotImplementedError(f"The optimiser '{optimiser_name}' has not been implemented")

    # Prepare dynamic import
    module_path = f"{optimisers_dir}/{optimiser_name}.py"
    spec = importlib.util.spec_from_file_location("optimiser_file", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    
    # Initialise and return the optimiser
    from optimiser_file import Optimiser
    optimiser = Optimiser(optimiser_name, controller)
    optimiser.initialise(**kwargs)
    return optimiser
