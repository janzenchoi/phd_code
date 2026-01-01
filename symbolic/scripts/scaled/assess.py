"""
 Title:         Assess
 Description:   Assesses multiple symbolic regression results
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += ["../.."]
from symbolic.helper.general import transpose, round_sf
from symbolic.io.files import csv_to_dict, dict_to_csv, safe_mkdir
from symbolic.io.dataset import remove_data
from symbolic.helper.interpolator import intervaluate
from symbolic.helper.derivative import differentiate_curve
from symbolic.helper.plotter import prep_plot, set_limits, add_legend, save_plot
from symbolic.helper.plotter import EXP_COLOUR, CAL_COLOUR, VAL_COLOUR
import matplotlib.pyplot as plt
import numpy as np, os

# Plotting parameters
TERTIARY = True
OXIDATION = True
TEMPERATURES = [800, 900, 1000]
STRESSES = [11, 12, 13, 16, 26, 28, 31, 36, 60, 65, 70, 80]
LIMITS = [((0,10000), (0,0.8)), ((0,10000), (0,0.5)), ((0,10000), (0,0.5))]
LIMITS[2] = LIMITS[2] if not OXIDATION else ((0,25000), (0,1.0))

# Data information
DATA_PATH = "../data/creep/inl_1"
CAL_ALL = False
DATA_LIST = [
    {"path": "AirBase_800_80_G25.csv",  "fit": True,    "tts": 2174580,  "mcr": 23.3e-5/3600, "ox": None},
    {"path": "AirBase_800_70_G44.csv",  "fit": True,    "tts": 4951332,  "mcr": 9.03e-5/3600, "ox": None},
    {"path": "AirBase_800_65_G33.csv",  "fit": CAL_ALL, "tts": 7927344,  "mcr": 5.04e-5/3600, "ox": None},
    {"path": "AirBase_800_60_G32.csv",  "fit": CAL_ALL, "tts": 12509442, "mcr": 2.89e-5/3600, "ox": None},
    {"path": "AirBase_900_36_G22.csv",  "fit": True,    "tts": 2484756,  "mcr": 12.2e-5/3600, "ox": None},
    {"path": "AirBase_900_31_G50.csv",  "fit": True,    "tts": 5122962,  "mcr": 5.37e-5/3600, "ox": None},
    {"path": "AirBase_900_28_G45.csv",  "fit": CAL_ALL, "tts": 6807168,  "mcr": 3.53e-5/3600, "ox": None},
    {"path": "AirBase_900_26_G59.csv",  "fit": CAL_ALL, "tts": 10289304, "mcr": 2.19e-5/3600, "ox": 20578608},
    {"path": "AirBase_1000_16_G18.csv", "fit": True,    "tts": 3883572,  "mcr": 6.76e-5/3600, "ox": 7767144},
    {"path": "AirBase_1000_13_G30.csv", "fit": True,    "tts": 8448138,  "mcr": 2.66e-5/3600, "ox": 16896276},
    {"path": "AirBase_1000_12_G48.csv", "fit": CAL_ALL, "tts": 9102942,  "mcr": 0.99e-5/3600, "ox": 18205884},
    {"path": "AirBase_1000_11_G39.csv", "fit": CAL_ALL, "tts": 9765990,  "mcr": 1.29e-5/3600, "ox": 19531980},
]

# Results information
RESULTS_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/symbolic"
# RESULTS_DIR = "2025-10-03 scaled"
RESULTS_DIR = "2025-10-04 scaled_ox"
# RESULTS_DIR = "2025-10-04 scaled_ox_p1"
RESULTS_LIST = [f"{RESULTS_DIR}/{ip}" for ip in os.listdir(f"{RESULTS_PATH}/{RESULTS_DIR}")]
RESULTS_PREFIX = "data_fit"
OPT_INDEX = 2

# Other constants
OUTPUT_PATH = "../results/summary"

def main() -> None:
    """
    Main function
    """

    # Intiailise
    exp_dict_list = get_exp_data()
    sim_dict_list_list = get_sim_data(exp_dict_list)
    safe_mkdir(OUTPUT_PATH)

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
        if not TERTIARY:
            exp_dict = remove_data(exp_dict, data["tts"], "time")
        elif not OXIDATION and data["ox"] != None:
            exp_dict = remove_data(exp_dict, data["ox"], "time")

        # Add time- and strain-to-failure
        exp_dict["ttf"] = max(exp_dict["time"])
        exp_dict["stf"] = max(exp_dict["strain"])

        # Add additional information and append
        for field in ["fit", "ox", "mcr"]:
            exp_dict[field] = data[field]
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
    sim_dict_list_list = []

    # Iterate through experimental data
    for exp_dict in exp_dict_list:
        
        # Get information
        stress = int(exp_dict["stress"])
        temperature = int(exp_dict["temperature"])

        # Get simulated data from results list
        sim_dict_list = []
        for results in RESULTS_LIST:

            # Read results
            results_path = f"{RESULTS_PATH}/{results}/{RESULTS_PREFIX}_{temperature}_{stress}.csv"
            results_dict = csv_to_dict(results_path)
            
            # Get simulated data (assume one)
            time_field = [key for key in results_dict.keys() if "time" in key][0]
            strain_field = [key for key in results_dict.keys() if "strain" in key][0]
            sim_dict = {"time": results_dict[time_field], "strain": results_dict[strain_field]}

            # Add characteristic information
            sim_dict["mcr"] = min(differentiate_curve(sim_dict, "time", "strain")["strain"])
            sim_dict["ttf"] = max(sim_dict["time"])
            sim_dict["stf"] = max(sim_dict["strain"])
            sim_dict["fit"] = exp_dict["fit"]
            sim_dict["temperature"] = exp_dict["temperature"]

            # Append
            sim_dict_list.append(sim_dict)

        # Append
        sim_dict_list_list.append(sim_dict_list)

    # Return
    return sim_dict_list_list

def calculate_cov(data_list:list) -> float:
    """
    Calculates the coefficient of variation

    Parameters:
    * `data_list`: List of data points

    Returns the CoV (in %)
    """
    data_mean = np.mean(data_list)
    data_var = np.var(data_list, ddof=1)
    data_sd = np.sqrt(data_var)
    data_cov = data_sd/data_mean * 100 # %
    return data_cov

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
        cov_list = cov_list[30:]
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
