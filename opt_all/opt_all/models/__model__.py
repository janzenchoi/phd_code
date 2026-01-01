"""
 Title:         Model Template
 Description:   Contains the basic structure for a model class
 Author:        Janzen Choi

"""

# Libraries
import importlib, inspect, os, pathlib, sys

# The Model Template Class
class __Model__:

    def __init__(self, name:str):
        """
        Class for defining a model
        """
        self.name = name
        self.exp_data = {}

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
            raise ValueError(f"The experimental data does not contain the '{field}' field")
        return self.exp_data[field]

    def get_param_names(self) -> list:
        """
        Returns a list of the parameter names for a model
        """
        model_params = inspect.signature(self.get_response).parameters
        param_names = list(model_params.keys())
        return param_names

    def initialise(self) -> None:
        """
        Runs at the start, once
        """
        pass
        
    def get_response(self, *params) -> dict:
        """
        Gets the model (must be overridden); returns none if the parameters / model is invalid
        """
        raise NotImplementedError

def create_model(model_path:str, **kwargs) -> __Model__:
    """
    Gets the model file's content
    
    Parameters:
    * `model_path`:  The path to the the model
    """

    # Separate model file and path
    model_file = model_path.split("/")[-1]
    model_path = "/".join(model_path.split("/")[:-1])
    models_dir = pathlib.Path(__file__).parent.resolve()
    models_dir = f"{models_dir}/{model_path}"

    # Get available models in current folder
    files = os.listdir(models_dir)
    files = [file.replace(".py", "") for file in files]
    files = [file for file in files if not file in ["__model__", "__pycache__"]]
    
    # Raise error if model name not in available models
    if not model_file in files:
        raise NotImplementedError(f"The model '{model_file}' has not been implemented")

    # Import and prepare model
    module_path = f"{models_dir}/{model_file}.py"
    spec = importlib.util.spec_from_file_location("model_file", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    
    # Initialise and return the model
    from model_file import Model
    model = Model(model_file)
    model.initialise(**kwargs)
    return model
