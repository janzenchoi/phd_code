"""
 Title:         Experiment related data
 Description:   Contains maps and functions for experiment results
 Author:        Janzen Choi

"""

# Libraries
import numpy as np

# Stores required fields for experimental data
DATA_FIELD_DICT = {
    "common":  {"lists": [], "values": ["temperature", "youngs", "poissons"]},
    "creep":   {"lists": ["time", "strain"], "values": ["stress"]},
    "tensile": {"lists": ["time", "strain", "stress"], "values": ["strain_rate"]},
    "cyclic":  {"lists": ["time", "strain", "stress"], "values": ["num_cycles", "strain_rate"]},
}

# Stores labels for each type of test
NEML_FIELD_CONVERSION = {
    "creep":   {"rtime": "time", "rstrain": "strain", "history": "history"},
    "tensile": {"strain": "strain", "stress": "stress", "history": "history"},
    "cyclic":  {"time": "time", "strain": "strain", "stress": "stress",
                "history": "history", "min": "min_stress", "max": "max_stress", "cycles": "cycles"}
}

# Identifies which fields to plot by default
DATA_FIELD_PLOT_MAP = {
    "creep":   [{"x": "time", "y": "strain"}],
    "tensile": [{"x": "strain", "y": "stress"}],
    "cyclic":  [
        {"x": "strain", "y": "stress"},
        {"x": "time", "y": "strain"},
        {"x": "time", "y": "stress"},
        {"x": "cycles", "y": "min_stress"},
        {"x": "cycles", "y": "max_stress"}
    ],
}

# Stores all the units
DATA_UNITS = {
    "poissons": "",
    "stress": "MPa",
    "strain": "mm/mm",
    "temperature": "°C",
    "time": "h",
    "peak_stress": "MPa",
    "youngs": "MPa",
}

def get_units(type:str) -> str:
    """
    Gets the units for a data type
    
    Parameters:
    * `type`: The data type

    Returns the units for the data type
    """
    if not type in DATA_UNITS:
        return ""
    return f" ({DATA_UNITS[type]})"

def get_labels_list(type:str) -> list:
    """
    Gets the labels for a data type
    
    Parameters:
    * `type`: The data type

    Returns a list of x and y labels for the data type
    """
    labels_list = []
    for i in range(len(DATA_FIELD_PLOT_MAP[type])):
        x_label = DATA_FIELD_PLOT_MAP[type][i]["x"]
        y_label = DATA_FIELD_PLOT_MAP[type][i]["y"]
        labels_list.append((x_label, y_label))
    return labels_list

def get_min_max_stress(x_list:list, y_list:list, tolerance:float) -> tuple:
    """
    Gets the peak stresses for cyclic data

    Parameters:
    * `x_list`:    The list of time values
    * `y_list`:    The list of stress values
    * `tolerance`: The tolerance used for the grouping
    
    Returns the list of min and max cycles and corresponding list of min and max stresses
    """
    # Get stationary point intervals
    dy_dx_list = np.gradient(y_list, x_list)
    sp_indexes = np.where(np.diff(np.sign(dy_dx_list)))[0]
    sp_x_list = np.array(x_list)[sp_indexes]
    sp_y_list = np.array(y_list)[sp_indexes]
    sp_x_list, sp_y_list = group_sp(sp_x_list, sp_y_list, tolerance)
    sp_x_list, sp_y_list = remove_zero_sp(sp_x_list, sp_y_list, tolerance)

    # Get list of min and max stresses
    min_stress_list, max_stress_list = [], []
    for i in range(len(sp_x_list)//2):
        peak_stress_list = [y_list[j] for j in range(len(y_list)) if x_list[j] >= sp_x_list[i] and x_list[j] <= sp_x_list[i+2]]
        min_stress_list.append(min(peak_stress_list))
        max_stress_list.append(max(peak_stress_list))

    # Return
    cycle_list = list(range(1, len(sp_x_list)//2+1))
    return cycle_list, min_stress_list, max_stress_list

def group_sp(x_list:list, y_list:list, tolerance:float) -> tuple:
    """
    Groups the stationary points together

    Parameters:
    * `x_list`:    The list of values corresponding to the y_list
    * `y_list`:    The list of values being grouped
    * `tolerance`: The tolerance used for the grouping
    
    Returns two lists representing the grouped stationary points
    """

    # Initialise
    sp_x_list = []
    sp_y_list = []
    curr_x_group = [x_list[0]]
    curr_y_group = [y_list[0]]

    # Start grouping
    for i in range(1, len(x_list)):
        if abs(y_list[i] - curr_y_group[-1]) < tolerance:
            curr_x_group.append(x_list[i])
            curr_y_group.append(y_list[i])
        else:
            sp_x_list.append(np.average(curr_x_group))
            sp_y_list.append(np.average(curr_y_group))
            curr_x_group = [x_list[i]]
            curr_y_group = [y_list[i]]

    # Final grouping and return
    sp_x_list.append(np.average(curr_x_group))
    sp_y_list.append(np.average(curr_y_group))
    return sp_x_list, sp_y_list

def remove_zero_sp(x_list:list, y_list:list, tolerance:float) -> tuple:
    """
    Removes stationary points close to 0

    Parameters:
    * `x_list`:    The list of x values
    * `y_list`:    The list of y values
    * `tolerance`: The tolerance used for the removal
    
    Returns two lists representing the non-close-to-zero stationary points
    """
    keep_indexes = [i for i in range(len(y_list)) if abs(y_list[i]) > tolerance]
    x_list = list(np.array(x_list)[keep_indexes])
    y_list = list(np.array(y_list)[keep_indexes])
    return x_list, y_list
