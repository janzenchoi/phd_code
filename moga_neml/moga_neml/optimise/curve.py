"""
 Title:         Curve
 Description:   For storing information about a curve
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.errors.__error__ import create_error
from moga_neml.models.__model__ import __Model__

# The Curve class
class Curve:
    
    def __init__(self, exp_data:dict, model:__Model__):
        """
        Stores information about a curve

        Parameters:
        * `exp_data`:      The experimental data
        * `model`:         The model to use for the predictions
        * `custom_driver`: The custom driver
        """

        # Initialise inputs variables
        self.exp_data = exp_data
        self.model    = model
        
        # Initialise internal variables
        self.custom_driver = None
        self.custom_driver_kwargs = None
        self.error_list = []
        self.prd_data = None # the latest predicted data, as a dictionary

    def set_exp_data(self, exp_data:dict) -> None:
        """
        Sets the experimental data

        Parameters:
        * `exp_data`: The experimental data
        """
        self.exp_data = exp_data
    
    def get_exp_data(self) -> dict:
        """
        Gets the experimental data
        """
        return self.exp_data

    def set_prd_data(self, prd_data:dict) -> None:
        """
        Sets the predicted data

        Parameters:
        * `prd_data`: The predicted data
        """
        self.prd_data = prd_data
    
    def get_prd_data(self) -> dict:
        """
        Gets the predicted data
        """
        return self.prd_data
    
    def get_type(self) -> str:
        """
        Gets the curve type
        """
        return self.exp_data["type"]

    def set_custom_driver(self, custom_driver:str, custom_driver_kwargs) -> None:
        """
        Sets the custom driver

        Parameters:
        * `custom_driver`: The custom driver handle
        """
        self.custom_driver = custom_driver
        self.custom_driver_kwargs = custom_driver_kwargs

    def get_custom_driver(self) -> tuple:
        """
        Returns the custom driver
        """
        return self.custom_driver, self.custom_driver_kwargs
    
    def get_error_list(self) -> list:
        """
        Gets the list of errors
        """
        return self.error_list
    
    def is_validation(self) -> bool:
        """
        Returns whether the curve is used for validation or not
        """
        return self.error_list == []

    def add_error(self, error_name:str, x_label:str, y_label:str, weight:float, **kwargs) -> None:
        """
        Adds an error to the list

        Parameters:
        * `error_name`:  The name of the error
        * `x_label`:     The label of the x axis
        * `y_label`:     The label of the y axis
        * `weight`:      The weight applied to the error
        """

        # Check labels
        for label in [x_label, y_label]:
            if label != "" and not label in self.exp_data.keys():
                raise ValueError(f"Error {error_name} cannot be added because '{label}' is not a field in the data!")
        
        # Add error
        error = create_error(error_name, x_label, y_label, weight, self.exp_data, self.model, **kwargs)
        self.error_list.append(error)
    