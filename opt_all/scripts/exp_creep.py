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

# Plotting parameters
TEMPERATURES = [800, 900, 1000]
LIMITS = [((0,10000), (0,0.8)), ((0,10000), (0,0.5)), ((0,25000), (0,1.0))]

# Data information
DATA_PATH = "data/inl_1"
CAL_ALL = False
DATA_LIST = [
    {"path": "AirBase_800_80_G25.csv",  "fit": True,    "ox": None},
    {"path": "AirBase_800_70_G44.csv",  "fit": True,    "ox": None},
    {"path": "AirBase_800_65_G33.csv",  "fit": CAL_ALL, "ox": None},
    {"path": "AirBase_800_60_G32.csv",  "fit": CAL_ALL, "ox": None},
    {"path": "AirBase_900_36_G22.csv",  "fit": True,    "ox": None},
    {"path": "AirBase_900_31_G50.csv",  "fit": True,    "ox": None},
    {"path": "AirBase_900_28_G45.csv",  "fit": CAL_ALL, "ox": None},
    {"path": "AirBase_900_26_G59.csv",  "fit": CAL_ALL, "ox": 20578608},
    {"path": "AirBase_1000_16_G18.csv", "fit": True,    "ox": 7767144},
    {"path": "AirBase_1000_13_G30.csv", "fit": True,    "ox": 16896276},
    {"path": "AirBase_1000_12_G48.csv", "fit": CAL_ALL, "ox": 18205884},
    {"path": "AirBase_1000_11_G39.csv", "fit": CAL_ALL, "ox": 19531980},
]
OUTPUT_PATH = "results"

def main() -> None:
    """
    Main function
    """

    # Read experimental and simulated data
    exp_dict_list = get_exp_data()
    
    # Create plots for each temperature
    for temperature, limits in zip(TEMPERATURES, LIMITS):

        # Initialise plot
        prep_plot("Time", "Strain", "h", "mm/mm")

        # Plot experimental data
        for exp_dict in exp_dict_list:
            if exp_dict["temperature"] == temperature:
                time_list = [t/3600 for t in exp_dict["time_ox"]]
                plt.scatter(time_list, exp_dict["strain_ox"], color="silver", s=8**2)
                time_list = [t/3600 for t in exp_dict["time"]]
                plt.scatter(time_list, exp_dict["strain"], color="gray", s=8**2)

        # Format and save plot
        set_limits(limits[0], limits[1])
        handles = [
            plt.scatter([], [], color="gray", label="Typical",  s=8**2),
            # plt.scatter([], [], color="silver", label="Atypical",  s=8**2)
        ]
        legend = plt.legend(handles=handles, ncol=1, framealpha=1, edgecolor="black",
                            fancybox=True, facecolor="white", fontsize=12, loc="upper left")
        plt.gca().add_artist(legend)
        save_plot(f"{OUTPUT_PATH}/exp_{temperature}.png")


def get_exp_data() -> list:
    """
    Gets the experimental data;
    Returns the experimental data
    """

    # Get experimental data
    exp_dict_list = []
    for data in DATA_LIST:

        # Read data
        exp_path = f"{DATA_PATH}/{data['path']}"
        exp_dict = csv_to_dict(exp_path)

        # Remove data
        time_ox = exp_dict["time"]
        strain_ox = exp_dict["strain"]
        if data["ox"] != None:
            exp_dict = remove_data(exp_dict, data["ox"], "time")
        exp_dict["time_ox"] = time_ox
        exp_dict["strain_ox"] = strain_ox

        # Add additional information and append
        exp_dict["ox"] = data["ox"]
        exp_dict["fit"] = data["fit"]
        exp_dict_list.append(exp_dict)

    # Return
    return exp_dict_list

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
