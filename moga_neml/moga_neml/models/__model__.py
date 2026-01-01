"""
 Title:         Model Template
 Description:   Contains the basic structure for a model class
 Author:        Janzen Choi

"""

# Libraries
import importlib, os, pathlib, sys

# The Model Template Class
class __Model__:

    def __init__(self, name:str):
        """
        Class for defining a model
        """
        self.name = name
        self.param_dict = {}
        self.exp_data = {}

    def add_param(self, name:str, l_bound:float=0.0e0, u_bound:float=1.0e0) -> None:
        """
        Adds a parameter and bounds

        Parameters:
        * `name`:    The name of the parameter
        * `l_bound`: The lower bound of the optimisation
        * `u_bound`: The upper bound of the optimisation
        """
        if name in self.param_dict.keys():
            raise ValueError("The parameter has already been defined!")
        self.param_dict[name] = {"l_bound": l_bound, "u_bound": u_bound}

    def set_exp_data(self, exp_data:dict) -> None:
        """
        Sets the experimental data

        Parameter:
        * `exp_data`: The experimental data
        """
        self.exp_data = exp_data

    def get_name(self) -> str:
        """
        Gets the name of the mmodel
        """
        return self.name

    def get_exp_data(self) -> list:
        """
        Returns the experimental data
        """
        return self.exp_data

    def get_data(self, field:str):
        """
        Gets the data corresponding to a field
        
        Parameters:
        * `field`: The name of the field

        Returns the data
        """
        if not field in self.exp_data.keys():
            raise ValueError(f"The experimental data does not contain the {field} field")
        return self.exp_data[field]

    def get_param_dict(self) -> dict:
        """
        Returns the parameter info
        """
        return self.param_dict

    def get_calibrated_model(self, *params): # -> NEML Model
        """
        Calibrates a model and returns it

        Parameters:
        * `params`: The parameter values to calibrate the model

        Returns the calibrated model
        """
        self.calibrated_model = self.calibrate_model(*params)
        return self.calibrated_model

    def get_last_calibrated_model(self):
        """
        Gets the last calibrated model
        """
        if self.calibrated_model == None:
            raise ValueError("Could not get the calibrated model because it has not been calibrated yet!")
        return self.calibrated_model
    
    def record_results(self, output_path:str, *params) -> None:
        """
        Records something if desired
        
        Parameters:
        * `output_path`: The path to the output directory
        """
        pass

    def initialise(self) -> None:
        """
        Runs at the start, once (must be overridden)
        """
        raise NotImplementedError
        
    def calibrate_model(self, *params): # -> NEML Model
        """
        Gets the model (must be overridden); returns none if the parameters / model is invalid
        """
        raise NotImplementedError

def create_model(model_name:str, **kwargs) -> __Model__:
    """
    Creates and return a model

    Parameters:
    * `model_name`: The name of the model

    Returns the model
    """

    # Get available models in current folder
    models_dir = pathlib.Path(__file__).parent.resolve()
    files = os.listdir(models_dir)
    files = [file.replace(".py", "") for file in files]
    files = [file for file in files if not file in ["__model__", "__pycache__"]]
    
    # Raise error if model name not in available models
    if not model_name in files:
        raise NotImplementedError(f"The model '{model_name}' has not been implemented")

    # Prepare dynamic import
    module_path = f"{models_dir}/{model_name}.py"
    spec = importlib.util.spec_from_file_location("model_file", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    
    # Initialise and return the model
    from model_file import Model
    model = Model(model_name)
    model.initialise(**kwargs)
    return model
