"""
 Title:         Error Template
 Description:   Contains the basic structure for an error class
 Author:        Janzen Choi

"""

# Libraries
import importlib, os, pathlib, sys
from moga_neml.models.__model__ import __Model__

# The Error Template Class
class __Error__:

    def __init__(self, name:str, x_label:str, y_label:str, weight:str,
                 exp_data:dict, model:__Model__):
        """
        Class for defining an error

        Parameters:
        * `name`:     The name of the error
        * `x_label`:  The label for the x axis
        * `y_label`:  The label for the y axis
        * `weight`:   The weight applied to the error
        * `exp_data`: The experimental data
        * `model`:    The model
        """
        self.name     = name
        self.x_label  = x_label
        self.y_label  = y_label
        self.weight   = weight
        self.exp_data = exp_data
        self.model    = model

    def get_name(self) -> str:
        """
        Returns the name of the error
        """
        return self.name

    def get_x_label(self) -> str:
        """
        Returns the x label of the error
        """
        if self.x_label == "":
            raise ValueError("The x label has not been defined!")
        return self.x_label

    def get_y_label(self) -> str:
        """
        Returns the y label of the error
        """
        if self.y_label == "":
            raise ValueError("The y label has not been defined!")
        return self.y_label

    def get_group_key(self, group_name:bool=True, group_type:bool=True,
                      group_labels:bool=True) -> str:
        """
        Gets error name, type, and both labels, if they exist;
        controls how the errors are grouped together when optimising

        Parameters:

        """
        group_str_list = []
        if group_name:
            group_str_list.append(self.name)
        if group_type:
            group_str_list.append(self.exp_data["type"])
        if group_labels and self.x_label != "":
            group_str_list.append(self.x_label)
        if group_labels and self.y_label != "":
            group_str_list.append(self.y_label)
        if group_str_list != []:
            return "_".join(group_str_list)
        return "error" # combine all errors to one

    def get_weight(self) -> float:
        """
        Returns the weight of the error
        """
        return self.weight

    def get_exp_data(self) -> dict:
        """
        Gets the experimental data
        """
        return self.exp_data

    def get_data(self, field:str):
        """
        Returns a field of the experimental data

        Parameters:
        * `field`: The name of the field
        """
        if not field in self.exp_data.keys():
            raise ValueError(f"The experimental data does not contain the {field} field")
        return self.exp_data[field]

    def get_x_data(self) -> list:
        """
        Gets the x data
        """
        x_label = self.get_x_label()
        return self.exp_data[x_label]

    def get_y_data(self) -> list:
        """
        Gets the y data
        """
        y_label = self.get_y_label()
        return self.exp_data[y_label]

    def get_model(self) -> __Model__:
        """
        Gets the model
        """
        return self.model

    def enforce_data_type(self, type:str) -> None:
        """
        Enforces a certain type of data

        Parameters:
        * `type`: The type of the experimental data
        """
        if self.exp_data["type"] != type:
            raise ValueError(f"Failed to initialise the '{self.name}' error because it only works with {type} data!")

    def enforce_model(self, model_name:str) -> None:
        """
        Enforces a certain model

        Parameters:
        * `model_name`: The name of the model
        """
        if self.model.get_name() != model_name:
            raise ValueError(f"Failed to initialise the '{self.name}' error because it only works with the {model_name} model!")

    def initialise(self) -> None:
        """
        Runs at the start, once (optional placeholder)
        """
        pass

    def get_value(self) -> float:
        """
        Returns an error (must be overridden)
        """
        raise NotImplementedError

# Creates and return a error
def create_error(error_name:str, x_label:str, y_label:str, weight:float,
              exp_data:dict, model:__Model__, **kwargs) -> __Error__:
    """
    Gets an error

    Parameters:
    * `error_name`:  The name of the error
    * `x_label`:     The label for the x axis
    * `y_label`:     The label for the y axis
    * `weight`:      The weight applied to the error
    * `exp_data`:    The experimental data
    * `model`:       The model

    Returns the error object
    """

    # Get available errors in current folder
    errors_dir = pathlib.Path(__file__).parent.resolve()
    files = os.listdir(errors_dir)
    files = [file.replace(".py", "") for file in files]
    files = [file for file in files if not file in ["__error__", "__pycache__"]]
    
    # Raise error if error name not in available errors
    if not error_name in files:
        raise NotImplementedError(f"The error '{error_name}' has not been implemented")

    # Prepare dynamic import
    module_path = f"{errors_dir}/{error_name}.py"
    spec = importlib.util.spec_from_file_location("error_file", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    
    # Import, initialise, and return error
    from error_file import Error
    error = Error(error_name, x_label, y_label, weight, exp_data, model)
    error.initialise(**kwargs)
    return error
