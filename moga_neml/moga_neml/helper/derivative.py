"""
 Title:         Derivative
 Description:   For interpolating and differentating curves
 Author:        Janzen Choi

"""

# Libraries
from copy import deepcopy
from moga_neml.helper.interpolator import Interpolator

def get_bfd(x_list:list, y_list:list) -> tuple:
    """
    Gets the derivative via backward finite difference

    Parameters:
    * `x_list`: The list of x values
    * `y_list`: The list of y values
    
    Returns the dertivative of the lists
    """
    new_x_list, dy_list = [], []
    for i in range(1,len(x_list)):
        if x_list[i] > x_list[i-1]:
            new_x_list.append(x_list[i])
            dy_list.append((y_list[i]-y_list[i-1])/(x_list[i]-x_list[i-1]))
    return new_x_list, dy_list

def remove_after_sp(exp_data:dict, nature:str, x_label:str, y_label:str, window:int,
                    acceptance:int, nominal:int=0) -> dict:
    """
    Removes data after the Xth local minima/maxima

    Parameters:
    * `exp_data`:   The dictionary of experimental data
    * `nature`:     The nature of the stationary point
    * `x_label`:    The label of the x axis
    * `y_label`:    The label of the y axis
    * `window`:     The window size to determine the stationary point
    * `acceptance`: The acceptance rate (0..1)
    * `nominal`:    The nominal of the staionary point to be selected

    Returns the data after the removal
    """

    # Get all stationary points
    exp_data = deepcopy(exp_data)
    d_exp_data = differentiate_curve(exp_data, x_label, y_label)
    sp_list = get_stationary_points(d_exp_data, x_label, y_label, window, acceptance)
    
    # Get all stationary points
    sp_list = [sp for sp in sp_list if sp["nature"] == nature]
    if len(sp_list) <= nominal:
        return exp_data
    sp = sp_list[nominal]

    # Remove data after local stationary point
    exp_data[x_label] = [exp_data[x_label][i] for i in range(len(exp_data[x_label]))
                         if i < sp["index"]]
    exp_data[y_label] = [exp_data[y_label][i] for i in range(len(exp_data[y_label]))
                         if i < sp["index"]]
    return exp_data

def get_stationary_points(exp_data:dict, x_label:str, y_label:str,
                          window:int, acceptance:int) -> list:
    """
    Gets a list of the stationary points and their nature (of a noisy curve)

    Parameters:
    * `exp_data`:   The dictionary of experimental data
    * `x_label`:    The label of the x axis
    * `y_label`:    The label of the y axis
    * `window`:     The window size to determine the stationary point
    * `acceptance`: The acceptance rate (0..1)

    Returns a list of dictionaries of stationary points
    """

    # Initialise
    d_exp_data = differentiate_curve(exp_data, x_label, y_label)
    dy_label = f"d_{y_label}"
    sp_list = []

    # Gets the locations where the derivative passes through the x axis
    for i in range(len(d_exp_data[x_label])-1):
        if ((d_exp_data[y_label][i] <= 0 and d_exp_data[y_label][i+1] >= 0) or (d_exp_data[y_label][i] >= 0 and d_exp_data[y_label][i+1] <= 0)):
            sp_list.append({
                x_label:  exp_data[x_label][i],
                y_label:  exp_data[y_label][i],
                dy_label: d_exp_data[y_label][i],
                "index":  i,
                "nature": get_sp_nature(d_exp_data[y_label], i, window, acceptance)
            })
    
    # Return list of dictionaries
    return sp_list

def get_sp_nature(dy_list:list, index:int, window=0.1, acceptance=0.9) -> str:
    """
    Checks the left and right of a list of values to determine if a point is stationary

    Parameters:
    * `dy_list`:    The list of derivative values
    * `index`:      The index of the staionary points
    * `window`:     The window size to determine the stationary point
    * `acceptance`: The acceptance rate (0..1)

    Returns the nature of the stationary point
    """
    
    # Redefine window as a fraction of the data size
    window_abs = round(len(dy_list) * window)
    
    # Determine gradient on the left
    dy_left = dy_list[index-window_abs:index]
    left_pos_size = len([dy for dy in dy_left if dy > 0])
    left_pos = left_pos_size > window_abs*acceptance
    left_neg = left_pos_size < window_abs*(1-acceptance)
    
    # Determine gradient on the right
    dy_right = dy_list[index:index+window_abs+1]
    right_pos_size = len([dy for dy in dy_right if dy > 0])
    right_pos = right_pos_size > window_abs*acceptance
    right_neg = right_pos_size < window_abs*(1-acceptance)

    # Determine nature
    if left_pos and right_neg:
        return "max"
    elif left_neg and right_pos:
        return "min"
    else:
        return "uncertain"
  
def differentiate_curve(exp_data:dict, x_label:str, y_label:str) -> dict:
    """
    For differentiating a curve

    Parameters:
    * `exp_data`:   The dictionary of experimental data
    * `x_label`:    The label of the x axis
    * `y_label`:    The label of the y axis

    Returns the differentiated data
    """
    exp_data = deepcopy(exp_data)
    interpolator = Interpolator(exp_data[x_label], exp_data[y_label])
    interpolator.differentiate()
    exp_data[y_label] = interpolator.evaluate(exp_data[x_label])
    return exp_data