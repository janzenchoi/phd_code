"""
 Title:         Datset
 Description:   Class for storing data
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from symbolic.helper.general import transpose, get_thinned_list, get_spread_list, normalise
from symbolic.io.files import csv_to_dict
from scipy.interpolate import interp1d
from copy import deepcopy

# Dataset class
class Dataset:

    def __init__(self, csv_path:str, fitting:bool):
        """
        Constructor for the dataset class
        
        Parameters:
        * `csv_path`: Path to the CSV file
        * `fitting`:  Whether the dataset is for fitting
        """
        self.path = csv_path
        self.fitting = fitting
        self.data_dict = csv_to_dict(csv_path)
        self.weights = [1, 1] # uniform weighting
        self.weight = 1.0

    def get_path(self) -> str:
        """
        Returns the path to the CSV files
        """
        return self.path

    def is_fitting(self) -> bool:
        """
        Returns whether the dataset is intended for fitting
        """
        return self.fitting

    def set_data_dict(self, data_dict:dict) -> None:
        """
        Resets the data dictionary

        Parameters:
        * `data_dict`: The new data dictionary
        """
        self.data_dict = data_dict

    def get_data_dict(self) -> dict:
        """
        Returns the actual dataset
        """
        return self.data_dict
    
    def set_data(self, field:str, data) -> None:
        """
        Sets the data under a field
        
        Parameters:
        * `field`: The field under which the data is stored
        * `data`:  The data to be set
        """
        max_length = max([len(self.data_dict[field]) for field in self.data_dict.keys()
                          if isinstance(self.data_dict[field], list)])
        if isinstance(data, list) and len(data) != max_length:
            raise ValueError(f"The added '{field}' field in does not have the same entries as the existing fields!")
        self.data_dict[field] = data
    
    def get_data(self, field:str) -> list:
        """
        Gets the data under a field
        
        Parameters:
        * `field`: The field under which the data is stored
        
        Returns the data under the defined field
        """
        if not field in self.data_dict.keys():
            raise ValueError(f"The '{field}' field has not been defined!")
        return self.data_dict[field]

    def get_size(self) -> int:
        """
        Returns the size of the lists in the dataset;
        assumes all lists are of the same size
        """
        size_list = []
        for field in self.data_dict.keys():
            if isinstance(self.data_dict[field], list):
                size_list.append(len(self.data_dict[field])) 
        if size_list == []:
            return 0
        return max(size_list)

    def set_weight(self, weight:float) -> None:
        """
        Sets the weight of the data set relative to other datasets

        Parameters:
        * `weight`: Weight to apply
        """
        self.weight = weight

    def get_weight(self) -> float:
        """
        Gets the weight of the data set relative to other datasets
        """
        return self.weight

    def set_weights(self, weights:list) -> None:
        """
        Sets the weights in the data set

        Parameters:
        * `weights`: Weights to apply
        """
        self.weights = weights

    def get_weights(self) -> list:
        """
        Spline interpolates the weights based on the number of data points;
        assumes relatively uniform spreading of values
        """
        size = self.get_size()
        index_list = get_spread_list(len(self.weights), size)
        interp = interp1d(index_list, self.weights)
        weight_list = interp(range(size)).tolist()
        return weight_list

    def has_data(self, field:str, value:float) -> bool:
        """
        Checks whether the field has a certain value

        Parameters:
        * `field`: The field to be checked
        * `value`: The value to be compared

        Returns whether there is a match
        """
        if not field in self.data_dict.keys():
            return False
        if isinstance(self.data_dict[field], list):
            return value in self.data_dict[field]
        else:
            return value == self.data_dict[field]

    def get_list_fields(self) -> list:
        """
        Gets the fields containing lists
        """
        list_fields = []
        for field in self.data_dict.keys():
            if isinstance(self.data_dict[field], list):
                list_fields.append(field)
        return list_fields

    def get_nonlist_fields(self) -> list:
        """
        Gets the fields that do not contain lists
        """
        nonlist_fields = []
        for field in self.data_dict.keys():
            if not isinstance(self.data_dict[field], list):
                nonlist_fields.append(field)
        return nonlist_fields

def reintervalise(dataset:Dataset, field:str, bounds:tuple=None, num_points:int=None) -> Dataset:
    """
    Creates a copy of a dataset that equally spaces the data
    of a user-defined field;
    assumes that the data in the defined field contains a list;
    also assumes that the data is monotonic

    Parameters:
    * `dataset`: The dataset
    * `field`:   The field containing the data
    * `bounds`:  The bounds of the new interval;
                 uses old interval if undefined
    
    Returns the new dataset object
    """

    # Create copy of the dataset
    new_dataset = deepcopy(dataset)

    # Ensure the defined field contains a list
    list_fields = dataset.get_list_fields()
    if not field in list_fields:
        return new_dataset

    # Equally space the data in the defined field
    old_x_data_list = dataset.get_data(field)
    if bounds == None:
        bounds = (min(old_x_data_list), max(old_x_data_list))
    if num_points == None:
        num_points = len(old_x_data_list)
    new_x_data_list = np.linspace(bounds[0], bounds[1], num_points)

    # Perform reintervalisation
    for list_field in list_fields:

        # If field is target field, then just equate
        if field == list_field:
            new_dataset.set_data(field, new_x_data_list.tolist())

        # Otherwise, interpolate
        old_y_data_list = dataset.get_data(list_field)
        interpolator = interp1d(old_x_data_list, old_y_data_list)
        new_y_data_list = interpolator(new_x_data_list)
        new_dataset.set_data(list_field, new_y_data_list.tolist())

    # Return reintervalised dataset
    return new_dataset

def sparsen_data(data_list:Dataset, new_size:int) -> Dataset:
    """
    Sparsens a datset

    Parameters:
    * `data_list`: List of data objects
    * `new_size`:  New size for the data

    Returns the sparsened datasets
    """
    for data in data_list:
        data_dict = data.get_data_dict()
        for field in data_dict.keys():
            if isinstance(data_dict[field], list):
                data_dict[field] = get_thinned_list(data_dict[field], new_size)
        data.set_data_dict(data_dict)
    return data_list

def posify_data(data_list:Dataset) -> Dataset:
    """
    Makes all list values in a dataset > 0

    Parameters:
    * `data_list`: List of data objects
    * `new_size`:  New size for the data

    Returns the datasets with negative datapoints removed
    """
    for data in data_list:
        new_data_dict = {}
        data_dict = data.get_data_dict()
        for field in data_dict.keys():
            if isinstance(data_dict[field], list):
                new_data_dict[field] = [data for data in data_dict[field] if data > 0]
            else:
                new_data_dict[field] = data_dict[field]
        data.set_data_dict(new_data_dict)
    return data_list

def bind_data(data_list:Dataset, field:str, bounds:tuple) -> Dataset:
    """
    Binds data in a field

    Parameters:
    * `data_list`: List of data objects
    * `field`:     Field to bind
    * `bounds`:    Lower and upper bounds

    Returns the datasets with bounded datapoints
    """
    for data in data_list:
        new_data_dict = {}
        data_dict = data.get_data_dict()
        if not field in data_dict.keys():
            raise ValueError(f"The '{field}' field does not exist in the data!")
        index_list = [i for i in range(len(data_dict[field])) if data_dict[field][i]>=bounds[0] and data_dict[field][i]<=bounds[1]]
        for key in data_dict.keys():
            if isinstance(data_dict[key], list):
                new_data_dict[key] = [data_dict[key][i] for i in index_list]
            else:
                new_data_dict[key] = data_dict[key]
        data.set_data_dict(new_data_dict)
    return data_list

def add_field(data_list:Dataset, add_field) -> Dataset:
    """
    Adds a field to a list of data objects

    Parameters:
    * `data_list`: List of data objects
    * `add_field`: Function handler to add field;
                   Function should take in a dictionary and
                   return a dictionary

    Returns the datasets with newly added fields
    """
    for data in data_list:
        data_dict = data.get_data_dict()
        data_dict = add_field(data_dict)
        data.set_data_dict(data_dict)
    return data_list

def data_to_array(data_list:list, field_list:list) -> np.array:
    """
    Converts a list of data objects into a numpy array

    Parameters:
    * `data_list`:  List of data objects
    * `field_list`: List of fields

    Returns the data as a numpy array
    """

    # Prepare data list
    field_data_list = []
    
    # Synthesise the data
    for data in data_list:

        # Get data
        data_dict = data.get_data_dict()
        has_list = True in [isinstance(data_dict[field], list) for field in field_list]
        if has_list:
            max_length = max([len(data_dict[field]) for field in field_list if isinstance(data_dict[field], list)])
        else:
            max_length = 1

        # Add data
        field_data_sublist = [data_dict[field] if isinstance(data_dict[field], list) else [data_dict[field]]*max_length for field in field_list]
        field_data_sublist = transpose(field_data_sublist)
        field_data_list += field_data_sublist

    # Convert and return
    field_data_array = np.array(field_data_list)
    return field_data_array

def normalise_data(data:Dataset, field:str, bounds:tuple=(0,1)) -> Dataset:
    """
    Normalises a list in a datset

    Parameters:
    * `data`:   Data object
    * `field`:  The field to normalise
    * `bounds`: The lower and upper bounds as a tuple

    Returns the normalised data
    """
    data_dict = data.get_data_dict()
    if not field in data_dict.keys():
        raise ValueError(f"The '{field}' field does not exist!")
    if not isinstance(data_dict[field], list):
        raise ValueError(f"The '{field}' field does not contain a list of values!")
    data_dict[field] = normalise(data_dict[field], bounds[0], bounds[1])
    data.set_data_dict(data_dict)
    return data

def remove_data(data_dict:dict, x_value:float, x_label:str, after:bool=True) -> dict:
    """
    Removes data after a specific value of a curve

    Parameters:
    * `data_dict`: The data dictionary to remove the data from
    * `x_value`:   The value to start removing the data
    * `x_label`:   The label corresponding to the value
    * `after`:     Whether to remove before or after

    Returns the curve after data removal
    """

    # Define before or after
    index_list = list(range(len(data_dict[x_label])))
    if after:
        comparator = lambda a, b : a > b
    else:
        comparator = lambda a, b : a < b

    # Initialise new curve
    new_data_dict = deepcopy(data_dict)
    for header in new_data_dict.keys():
        if isinstance(new_data_dict[header], list) and len(data_dict[header]) == len(data_dict[x_label]):
            new_data_dict[header] = []
            
    # Remove data after specific value
    for i in index_list:
        if comparator(data_dict[x_label][i], x_value):
            continue
        for header in new_data_dict.keys():
            if isinstance(new_data_dict[header], list) and len(data_dict[header]) == len(data_dict[x_label]):
                new_data_dict[header].append(data_dict[header][i])

    # Return new data
    return new_data_dict
