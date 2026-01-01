"""
 Title:         Assess
 Description:   Assesses multiple symbolic regression results
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += ["../.."]
from opt_all.helper.general import csv_to_dict, dict_to_csv, transpose, calculate_cov, round_sf
from opt_all.helper.interpolator import intervaluate
from opt_all.io.plotter import prep_plot, set_limits, add_legend, save_plot
from opt_all.io.plotter import EXP_COLOUR, CAL_COLOUR, VAL_COLOUR
from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np

# Plotting parameters
OXIDATION = True
TEMPERATURES = [800, 900, 1000]
STRESSES = [11, 12, 13, 16, 26, 28, 31, 36, 60, 65, 70, 80]
LIMITS = [((0,10000), (0,0.8)), ((0,10000), (0,0.5)), ((0,10000), (0,0.5))]
LIMITS[2] = LIMITS[2] if not OXIDATION else ((0,25000), (0,1.0))

# Data information
DATA_PATH = "../data/inl_1"
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

# Results information
# PARAMS_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/opt_all/2025-10-08 phi/params_fit.csv"
# OPT_INDEX = 4
PARAMS_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/opt_all/2025-10-08 phi_ox/params_fit.csv"
OPT_INDEX = 2
OUTPUT_PATH = "../results"

def evaluate_model(stress, temperature, params):

    # Get parameters
    a1, a2, a3, a4, n1, n2, n3, n4, q1, q2, q3, q4 = params
    get_phi = lambda a, n, q : a*stress**n*np.exp(-q/8.314/temperature)
    phi_1 = get_phi(a1, n1, q1)
    phi_2 = get_phi(a2, n2, q2)
    phi_3 = get_phi(a3, n3, q3)
    phi_4 = get_phi(a4, n4, q4)
    get_strain = lambda time : (phi_1*(1+phi_2)*time)**(1/(1+phi_2)) + (phi_3*(1-phi_4)*time)**(1/(1-phi_4))
    
    # Evaluate strains
    time_list = list(np.linspace(0, 1, 100))
    strain_list = [get_strain(time) for time in time_list]

    # Create dictionary and return
    results_dict = {
        "time": time_list,
        "strain": strain_list,
    }
    return results_dict

def main() -> None:
    """
    Main function
    """

    # Read experimental and simulated data
    exp_dict_list = get_exp_data()
    sim_dict_list_list = get_sim_data(exp_dict_list)

    # Create plots for each temperature
    for temperature, limits in zip(TEMPERATURES, LIMITS):

        # Initialise plot
        prep_plot("Time", "Strain", "h", "mm/mm")

        # Plot experimental data
        for exp_dict in exp_dict_list:
            if exp_dict["temperature"] == temperature:
                time_list = [t/3600 for t in exp_dict["time"]]
                plt.scatter(time_list, exp_dict["strain"], color=EXP_COLOUR, s=8**2)

        # Plot simulated data
        for exp_dict, sim_dict_list in zip(exp_dict_list, sim_dict_list_list):
            
            # Ignore irrelevant datasets
            if exp_dict["temperature"] != temperature:
                continue

            # Plot simulated data
            colour = CAL_COLOUR if exp_dict["fit"] else VAL_COLOUR
            for i, sim_dict in enumerate(sim_dict_list):
                alpha = 1.0 if OPT_INDEX == None or i==OPT_INDEX else 0.3
                time_list = [t/3600 for t in sim_dict["time"]]
                plt.plot(time_list, sim_dict["strain"], color=colour, linewidth=3, alpha=alpha)

        # Format and save plot
        set_limits(limits[0], limits[1])
        add_legend(calibration=True, validation=not CAL_ALL)
        save_plot(f"{OUTPUT_PATH}/assess_{temperature}.png")

    # Initialise errors
    num_sims = len(sim_dict_list_list[0])
    cal_strain_error = [[] for _ in range(num_sims)]
    val_strain_error = [[] for _ in range(num_sims)]

    # Iterate through each experiment-simulation
    for exp_dict, sim_dict_list in zip(exp_dict_list, sim_dict_list_list):
        for i, sim_dict in enumerate(sim_dict_list):

            # Calculate strain-time evolution errors
            min_ttf = min(max(exp_dict["time"]), max(sim_dict["time"]))
            time_list = list(np.linspace(0, min_ttf, 32))
            exp_strain_list = [intervaluate(exp_dict["time"], exp_dict["strain"], time) for time in time_list]
            sim_strain_list = [intervaluate(sim_dict["time"], sim_dict["strain"], time) for time in time_list]
            abs_err_strain = [abs(es-ss) for es, ss in zip(exp_strain_list, sim_strain_list)]
            error = np.average(abs_err_strain)/np.average(exp_strain_list)
            print(error)

            # Append errors
            if exp_dict["fit"]:
                cal_strain_error[i].append(error)
            else:
                val_strain_error[i].append(error)

    # Average errors
    for i in range(num_sims):
        cal_strain_error[i] = np.average(cal_strain_error[i])*100
        val_strain_error[i] = np.average(val_strain_error[i])*100

    # Export errors
    error_dict = {"cal": cal_strain_error, "val": val_strain_error}
    dict_to_csv(error_dict, f"{OUTPUT_PATH}/error.csv")

    # Print summary
    cal_cov, val_cov = get_cov(exp_dict_list, sim_dict_list_list)
    print(round_sf(np.average(cal_strain_error), 5))
    print(round_sf(np.average(val_strain_error), 5))
    print(round_sf(cal_cov, 5))
    print(round_sf(val_cov, 5))

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
        if not OXIDATION and data["ox"] != None:
            exp_dict = remove_data(exp_dict, data["ox"], "time")

        # Add additional information and append
        exp_dict["fit"] = data["fit"]
        exp_dict_list.append(exp_dict)

    # Return
    return exp_dict_list

def get_sim_data(exp_dict_list:list) -> list:
    """
    Gets the simulated data

    Parameters:
    * `exp_dict_list`: The experimental data

    Returns the simulated data as a list of lists
    """

    # Initialise
    param_dict = csv_to_dict(PARAMS_PATH)
    param_values_list = transpose(list(param_dict.values()))
    sim_dict_list_list = []

    # Iterate through experimental data
    for exp_dict in exp_dict_list:
        
        # Get information
        time_list = exp_dict["time"]
        stress = int(exp_dict["stress"])/80
        temperature = int(exp_dict["temperature"])/1000

        # Get simulated data
        sim_dict_list = []
        for param_values in param_values_list:
            sim_dict = evaluate_model(stress, temperature, param_values)
            max_time = max(time_list)
            sim_dict["time"] = [t*max_time for t in sim_dict["time"]]
            sim_dict_list.append(sim_dict)

        # Append
        sim_dict_list_list.append(sim_dict_list)

    # Return
    return sim_dict_list_list

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

def get_cov(exp_dict_list:list, sim_dict_list_list:list) -> tuple:
    """
    Calcualtes the coefficient of variation

    Parameters:
    * `exp_dict_list`:      The list of experimental datasets
    * `sim_dict_list_list`: The grid of simulated datasets

    Returns the average COV for the calibration and validation data
    """

    # Initialise
    cal_cov_list, val_cov_list = [], []
    
    # Go through datasets
    for exp_dict, sim_dict_list in zip(exp_dict_list, sim_dict_list_list):
        
        # Calculate COV
        data_grid = transpose([sim_dict["strain"] for sim_dict in sim_dict_list])[1:]
        cov_list = [calculate_cov(data_list) for data_list in data_grid]
        cov = np.average(cov_list)

        # Add COV to list
        if exp_dict["fit"]:
            cal_cov_list.append(cov)
        else:
            val_cov_list.append(cov)

    # Return average
    return np.average(cal_cov_list), np.average(val_cov_list)

# Calls the main function
if __name__ == "__main__":
    main()
