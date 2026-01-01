"""
 Title:         Exp
 Description:   Plots experimental creep data
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += [".."]
from opt_all.helper.general import csv_to_dict
from opt_all.io.plotter import prep_plot, set_limits, save_plot
from copy import deepcopy
import matplotlib.pyplot as plt

# Data information
CAL_ALL = False
DATA_LIST = [
    {"path": "data/experimental/tensile/inl/AirBase_800_D7.csv",   "after": 0.62, "limits": ((0, 1.0), (0, 500))},
    {"path": "data/experimental/tensile/inl/AirBase_900_D10.csv",  "after": 0.59, "limits": ((0, 1.0), (0, 250))},
    {"path": "data/experimental/tensile/inl/AirBase_1000_D12.csv", "after": 0.52, "limits": ((0, 1.0), (0, 160))},
]
OUTPUT_PATH = "results"

def main() -> None:
    """
    Main function
    """
    for i, data in enumerate(DATA_LIST):
        data_dict = csv_to_dict(data["path"])
        data_dict = remove_data(data_dict, data["after"], "strain")
        prep_plot("Strain", "Stress", "mm/mm", "MPa")
        plt.scatter(data_dict["strain"], data_dict["stress"], color="gray", s=8**2)
        set_limits(data["limits"][0], data["limits"][1])
        save_plot(f"{OUTPUT_PATH}/exp_{i+1}.png")

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

# Calls the main function
if __name__ == "__main__":
    main()
