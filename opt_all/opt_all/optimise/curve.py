"""
 Title:         Curve
 Description:   For storing information about a curve
 Author:        Janzen Choi

"""

# Libraries
from copy import deepcopy
from opt_all.errors.__error__ import create_error
from opt_all.models.__model__ import __Model__

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
        self.function_list = [] # functions to run

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

    def has_field(self, field:str) -> bool:
        """
        Checks whether a field exists

        Parameters:
        * `field`: The field to be checked

        Returns whether the field exists
        """
        return field in self.exp_data.keys()

    def has_data(self, field:str, value:float) -> bool:
        """
        Checks whether the field has a certain value

        Parameters:
        * `field`: The field to be checked
        * `value`: The value to be compared

        Returns whether there is a match
        """
        if not self.has_field(field):
            return False
        if isinstance(self.exp_data[field], list):
            return value in self.exp_data[field]
        else:
            return value == self.exp_data[field]

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

    def add_error(self, error_name:str, labels:list, weight:float, group:str, **kwargs) -> None:
        """
        Adds an error to the list

        Parameters:
        * `error_name`: The name of the error
        * `labels`:     The list of labels
        * `weight`:     The weight applied to the error
        """

        # Check labels
        for label in labels:
            if label != "" and not label in self.exp_data.keys():
                raise ValueError(f"Error {error_name} cannot be added because '{label}' is not a field in the data!")
        
        # Add error
        error = create_error(error_name, labels, weight, group, self.exp_data, self.model, **kwargs)
        self.error_list.append(error)
    
    def remove_data(self, label:str, value:float, after:bool=True) -> None:
        """
        Removes data after a specific value of a curve

        Parameters:
        * `value`: The value to start removing the data
        * `label`: The label corresponding to the value
        * `after`: Whether to remove after

        Returns the curve after data removal
        """

        # Define before or after
        index_list = list(range(len(self.exp_data[label])))
        if after:
            comparator = lambda a, b : a > b
        else:
            comparator = lambda a, b : a < b
            index_list.reverse()

        # Initialise new curve
        new_exp_data = deepcopy(self.exp_data)
        for header in new_exp_data.keys():
            if isinstance(new_exp_data[header], list) and len(self.exp_data[header]) == len(self.exp_data[label]):
                new_exp_data[header] = []
                
        # Remove data after specific value
        for i in index_list:
            if comparator(self.exp_data[label][i], value):
                break
            for header in new_exp_data.keys():
                if isinstance(new_exp_data[header], list) and len(self.exp_data[header]) == len(self.exp_data[label]):
                    new_exp_data[header].append(self.exp_data[header][i])
        
        # Set new data
        self.exp_data = new_exp_data

    def add_function(self, function) -> None:
        """
        Adds function to run

        Parameters:
        * `function`: The function to run
        """
        self.function_list.append(function)

    def get_function_list(self) -> list:
        """
        Gets the list of functions to run
        """
        return self.function_list