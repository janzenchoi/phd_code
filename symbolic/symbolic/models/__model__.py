"""
 Title:         Model
 Description:   For creating model files
 Author:        Janzen Choi

"""

# Libraries
import importlib, os, pathlib, sys, numpy as np
from symbolic.helper.general import flatten

# Model Class
class __Model__:

    def __init__(self, name:str, output_path:str):
        """
        Template class for model objects
        
        Parameters:
        * `name`:        The name of the model
        * `output_path`: Output path
        """
        self.name = name
        self.output_path = output_path

    def get_name(self) -> str:
        """
        Gets the name of the model
        """
        return self.name

    def get_fit_weights(self, data_list:list) -> np.array:
        """
        Gets an array of weights corresponding to the fitting data

        Parameters:
        * `data_list`: List of data objects
        
        Returns the new array of weights
        """
        weights_list = [[w*data.get_weight() for w in data.get_weights()] for data in data_list]
        weights_list = flatten(weights_list)
        weights_array = np.array(weights_list)
        return weights_array

    def initialise(self, **kwargs) -> None:
        """
        Initialises the model; must be overridden
        """
        raise NotImplementedError(f"The 'initialise' function has not been defined for the '{self.name}' model!")

    def fit(self, data_list:list) -> None:
        """
        Performs the fitting; must be overridden

        Parameters:
        * `data_list`: List of datasets
        """
        raise NotImplementedError(f"The 'fit' function has not been defined for the '{self.name}' model!")
    
    def predict(self, data_list:list) -> list:
        """
        Predicts data using fit; must be overridden

        Parameters:
        * `data_list`: List of datasets

        Returns the predicted data
        """
        raise NotImplementedError(f"The 'predict' function has not been implemented for the '{self.name}' model!")
    
    def get_latex(self) -> str:
        """
        Returns the LaTeX equation of the final fit; must be overridden
        """
        raise NotImplementedError(f"The 'get_latex' function has not been implemented for the '{self.name}' model!")

def get_model(model_path:str, output_path:str, **kwargs) -> str:
    """
    Gets the model file's content
    
    Parameters:
    * `model_path`:  The path to the the model
    * `output_path`: The path to the output file
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
    model = Model(model_file, output_path)
    model.initialise(**kwargs)
    return model
