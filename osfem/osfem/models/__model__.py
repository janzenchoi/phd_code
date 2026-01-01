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
        self.data = None
        self.param_dict = {}

    def get_name(self) -> str:
        """
        Gets the name of the mmodel
        """
        return self.name

    def set_data(self, data:dict) -> None:
        """
        Sets the data

        Parameter:
        * `data`: The data
        """
        self.data = data
    
    def get_data(self) -> list:
        """
        Returns the data
        """
        return self.data

    def get_field(self, field:str):
        """
        Gets the data corresponding to a field
        
        Parameters:
        * `field`: The name of the field

        Returns the data
        """
        if not field in self.data.keys():
            raise ValueError(f"The experimental data does not contain the '{field}' field")
        return self.data[field]

    def add_param(self, param_name:str, label:str, l_bound:float, u_bound:float,
                  scale:float=None, limits:tuple=None) -> None:
        """
        Adds parameter information

        Parameters:
        * `param_name`: The name of the parameter
        * `label`:      Regex label for the parameter
        * `l_bound`:    The lower bound of the parameter
        * `u_bound`:    The upper bound of the parameter
        * `scale`:      Factor to scale the parameter
        * `limits`:     Limits for the boxplot
        """
        if scale == None:
            scale = lambda x : x
        if limits == None:
            limits = (l_bound, u_bound)
        self.param_dict[param_name] = {
            "label":   label,
            "l_bound": l_bound,
            "u_bound": u_bound,
            "scale":   scale,
            "limits":  limits,
        }

    def get_param_dict(self) -> dict:
        """
        Returns the parameter information
        """
        return self.param_dict

    def get_param_names(self) -> list:
        """
        Returns a list of the parameter names for a model
        """
        model_params = inspect.signature(self.evaluate).parameters
        param_names = list(model_params.keys())
        return param_names

    def initialise(self) -> None:
        """
        Runs at the start, once
        """
        pass
        
    def evaluate(self, *params) -> dict:
        """
        Gets the model (must be overridden); returns none if the parameters / model is invalid
        """
        raise NotImplementedError

    def evaluate_data(self, data_list:list, params:list) -> list:
        """
        Evaluates a model

        Parameters:
        * `model`:     The model to be evaluated
        * `data_list`: The data to evaluate the model with
        * `params`:    The parameters used for the evaluation

        Returns the evaluated response
        """
        prd_list = []
        for data in data_list:
            self.set_data(data)
            prd_list.append(self.evaluate(*params))
        return prd_list

def get_model(model_path:str, **kwargs) -> __Model__:
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
    
    # Initialise the model
    from model_file import Model
    model = Model(model_file)
    model.initialise(**kwargs)
    
    # Check if the model's parameters have all been defined
    param_names = model.get_param_names()
    param_dict = model.get_param_dict()
    for param_name in param_names:
        if not param_name in param_dict.keys():
            raise ValueError(f"The parameter '{param_name}' has not been defined!")

    # Return the model
    return model
