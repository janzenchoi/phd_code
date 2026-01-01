"""
 Title:         Constraint Template
 Description:   Contains the basic structure for a constraint class
 Author:        Janzen Choi

"""

# Libraries
import importlib, os, pathlib, sys
from moga_neml.optimise.curve import Curve
from moga_neml.models.__model__ import __Model__

# The Constraint Template Class
class __Constraint__:

    def __init__(self, name:str, x_label:str, y_label:str, model:__Model__):
        """
        Class for defining a constraint

        Parameters:
        * `name`:          The name of the constraint
        * `x_label`:       The label for the x axis
        * `y_label`:       The label for the y axis
        * `model`:         The model
        """
        self.name       = name
        self.x_label    = x_label
        self.y_label    = y_label
        self.model      = model
        self.curve_list = []

    def get_name(self) -> str:
        """
        Returns the name of the constraint
        """
        return self.name

    def get_x_label(self) -> str:
        """
        Returns the x label of the constraint
        """
        if self.x_label == "":
            raise ValueError("The x label has not been defined!")
        return self.x_label

    def get_y_label(self) -> str:
        """
        Returns the y label of the constraint
        """
        if self.y_label == "":
            raise ValueError("The y label has not been defined!")
        return self.y_label

    def add_curve(self, curve:Curve) -> None:
        """
        Adds a curve to the list
        
        Parameters:
        * `curve`: The curve
        """
        self.curve_list.append(curve)

    def get_curve_list(self) -> list:
        """
        Returns the list of curves
        """
        return self.curve_list

    def get_model(self) -> __Model__:
        """
        Gets the model
        """
        return self.model

    def initialise(self) -> None:
        """
        Runs at the start, once (optional placeholder);
        note that changes to the script are required so that the
        initialisation can use information about all the curves added
        """
        pass

    def check(self) -> bool:
        """
        Checks whether a constraint has been passed or not (must be overridden)
        """
        raise NotImplementedError

# Creates and return a constraint
def create_constraint(constraint_name:str, x_label:str, y_label:str,
                      model:__Model__, **kwargs) -> __Constraint__:
    """
    Gets a constraint

    Parameters:
    * `constraint_name`: The name of the constraint
    * `x_label`:         The label for the x axis
    * `y_label`:         The label for the y axis
    * `model`:           The model

    Returns the constraint object
    """

    # Get available constraints in current folder
    constraints_dir = pathlib.Path(__file__).parent.resolve()
    files = os.listdir(constraints_dir)
    files = [file.replace(".py", "") for file in files]
    files = [file for file in files if not file in ["__constraint__", "__pycache__"]]
    
    # Raise constraint if constraint name not in available constraints
    if not constraint_name in files:
        raise NotImplementedError(f"The constraint '{constraint_name}' has not been implemented")

    # Prepare dynamic import
    module_path = f"{constraints_dir}/{constraint_name}.py"
    spec = importlib.util.spec_from_file_location("constraint_file", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    
    # Import, initialise, and return constraint
    from constraint_file import Constraint
    constraint = Constraint(constraint_name, x_label, y_label, model)
    constraint.initialise(**kwargs)
    return constraint
