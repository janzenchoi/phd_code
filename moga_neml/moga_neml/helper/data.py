"""
 Title:         Curve related Functions
 Description:   Contains functions to manipulate curves
 Author:        Janzen Choi

"""

# Libraries
import math, numpy as np
from copy import deepcopy

def exclude_outliers(x_list:list, y_list:list):
    """
    Returns the coordinates of non-outliers (good to use with derivatives)
    
    Parameters:
    * `x_list`: The list of the x values
    * `y_list`: The list of the y values
    
    Returns the coordinates of the non-outliers, as two separate lists
    """
    q_1 = np.percentile(y_list, 25)
    q_3 = np.percentile(y_list, 75)
    u_bound = q_3 + 1.5*(q_3-q_1)
    l_bound = q_1 - 1.5*(q_3-q_1)
    index_list = [i for i in range(len(y_list))
                  if y_list[i] >= l_bound and y_list[i] <= u_bound]
    x_list = [x_list[i] for i in index_list]
    y_list = [y_list[i] for i in index_list]
    return x_list, y_list

def get_thinned_list(unthinned_list:list, density:int) -> list:
    """
    Gets a thinned list

    Parameters:
    * `unthinned_list`: The list before thinning
    * `density`:        The goal density of the thinned list

    Returns the thinned list
    """
    src_data_size = len(unthinned_list)
    step_size = src_data_size / density
    thin_indexes = [math.floor(step_size*i) for i in range(1, density - 1)]
    thin_indexes = [0] + thin_indexes + [src_data_size - 1]
    thinned_list = [unthinned_list[i] for i in thin_indexes]
    return thinned_list

def get_custom_thin_indexes(src_data_size:int, dst_data_size:int, distribution) -> list:
    """
    Returns a list of indexes corresponding to thinned data based on
    a defined cumulative distribution function
    
    Parameters:
    * `src_data_size`: The initial data size
    * `dst_data_size`: The goal data size
    * `distribution`:  The distribution function to thin the data

    Returns the custom thinned indexes
    """
    unmapped_indexes = [distribution(i/dst_data_size) for i in range(1,dst_data_size-1)]
    thin_indexes = [math.floor(i*src_data_size) for i in unmapped_indexes]
    thin_indexes = [0] + thin_indexes + [src_data_size-1]
    return thin_indexes

def find_tensile_strain_to_failure(stress_list:list) -> int:
    """
    Finds the tensile strain to failure based on the first stress value
    at 80% of the tensile curve's UTS

    * `data_list`: The list of stress values

    Returns the closest index if found; otherwise, return None
    """
    stress_to_failure = max(stress_list) * 0.80
    max_index = stress_list.index(max(stress_list))
    for i in range(max_index, len(stress_list)):
        if stress_list[i] < stress_to_failure:
            return i
    return -1

def remove_data_after(exp_data:dict, x_value:float, x_label:str) -> dict:
    """
    Removes data after a specific value of a curve

    Parameters:
    * `exp_data`: The curve to remove the data from
    * `x_value`:  The value to start removing the data
    * `x_label`:  The label corresponding to the value

    Returns the curve after data removal
    """

    # Initialise new curve
    new_exp_data = deepcopy(exp_data)
    for header in new_exp_data.keys():
        if isinstance(new_exp_data[header], list) and len(exp_data[header]) == len(exp_data[x_label]):
            new_exp_data[header] = []
            
    # Remove data after specific value
    for i in range(len(exp_data[x_label])):
        if exp_data[x_label][i] > x_value:
            break
        for header in new_exp_data.keys():
            if isinstance(new_exp_data[header], list) and len(exp_data[header]) == len(exp_data[x_label]):
                new_exp_data[header].append(exp_data[header][i])
    
    # Return new data
    return new_exp_data
