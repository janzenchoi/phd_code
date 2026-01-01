"""
 Title:         Performance plotter
 Description:   Creates plots for looking at the performance of the simulations
 Author:        Janzen Choi

"""

# Libraries
import math, numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
from scipy.interpolate import splev, splrep, splder
import sys; sys.path += ["../../../"]
from moga_neml.models.evpcd import Model as EVPCD
from moga_neml.models.evpwdb import Model as EVPWD
from moga_neml.drivers.driver import Driver
from moga_neml.optimise.curve import Curve
from moga_neml.errors.yield_point import get_yield
from params import *

# Constants
DATA_PATH = "../../data"
CALIBRATION = True

# Option
OPTIONS = [
    {"name": "cr_strain",   "info": r"$E_{\epsilon_{area}}$",      "handle": lambda x : get_area(x, "creep", "time", "strain"),     "limit": (0, 1.0)},
    {"name": "cr_min_rate", "info": r"$E_{\dot{\epsilon}_{min}}$", "handle": lambda x : get_mr(x, "creep", "time", "strain"),       "limit": (0, 0.1)},
    {"name": "cr_time_f",   "info": r"$E_{t_f}$",                  "handle": lambda x : get_max(x, "creep", "time"),                "limit": (0, 0.1)},
    {"name": "cr_strain_f", "info": r"$E_{\epsilon_f}$",           "handle": lambda x : get_max(x, "creep", "strain"),              "limit": (0, 0.1)},
    {"name": "ts_stress",   "info": r"$E_{\sigma_{area}}$",        "handle": lambda x : get_area(x, "tensile", "strain", "stress"), "limit": (0, 0.1)},
    {"name": "ts_yield",    "info": r"$E_{\sigma_{y}}$",           "handle": lambda x : get_yield_stress(x, "tensile"),             "limit": (0, 0.1)},
    {"name": "ts_uts",      "info": r"$E_{\sigma_{UTS}}$",         "handle": lambda x : get_max(x, "tensile", "stress"),            "limit": (0, 0.1)},
    {"name": "ts_strain_d", "info": r"$E_{\epsilon_d}$",           "handle": lambda x : get_end(x, "tensile", "strain"),            "limit": (0, 1.0)},
]

# Model
MODEL = [
    {"name": "cd", "object": EVPCD(""), "opt_params": EVPCD_OPT_PARAMS, "oth_params": EVPCD_OTH_PARAMS},
    {"name": "wd", "object": EVPWD(""), "opt_params": EVPWD_OPT_PARAMS, "oth_params": EVPWD_OTH_PARAMS},
][int(sys.argv[1])]

# Experimental data
EXP_INFO_LIST = [
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_800_70_G44.csv", "calib": True,  "time_end": None, "yield": None, "min_rate": 9.0345e-5},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_800_80_G25.csv", "calib": True,  "time_end": None, "yield": None, "min_rate": 2.3266e-4},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_800_60_G32.csv", "calib": False, "time_end": None, "yield": None, "min_rate": 2.8910e-5},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_800_65_G33.csv", "calib": False, "time_end": None, "yield": None, "min_rate": 5.0385e-5},
    {"path": f"{DATA_PATH}/tensile/inl/AirBase_800_D7.csv",     "calib": True,  "time_end": None, "yield": 291,  "min_rate": None},
]

# The Interpolator Class
class Interpolator:

    # Constructor
    def __init__(self, x_list, y_list, resolution=50, smooth=False):
        thin_x_list = get_thinned_list(x_list, resolution)
        thin_y_list = get_thinned_list(y_list, resolution)
        smooth_amount = resolution if smooth else 0
        self.spl = splrep(thin_x_list, thin_y_list, s=smooth_amount)
    
    # Convert to derivative
    def differentiate(self):
        self.spl = splder(self.spl)

    # Evaluate
    def evaluate(self, x_list):
        return list(splev(x_list, self.spl))

# Returns a thinned list
def get_thinned_list(unthinned_list:list, density:int) -> list:
    src_data_size = len(unthinned_list)
    step_size = src_data_size / density
    thin_indexes = [math.floor(step_size*i) for i in range(1, density - 1)]
    thin_indexes = [0] + thin_indexes + [src_data_size - 1]
    return [unthinned_list[i] for i in thin_indexes]

# Tries to float cast a value
def try_float_cast(value:str) -> float:
    try:
        return float(value)
    except:
        return value

# Finds the tensile strain to failure based on the first stress value at 80% of the tensile curve's UTS
def find_tensile_strain_to_failure(stress_list:list) -> int:
    stress_to_failure = max(stress_list) * 0.80
    max_index = stress_list.index(max(stress_list))
    for i in range(max_index, len(stress_list)):
        if stress_list[i] < stress_to_failure:
            return i
    return None

# Removes data after a specific value of a curve
def remove_data_after(exp_data:dict, x_value:float, x_label:str) -> dict:

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

# Converts CSV data into a curve dict
def get_exp_data_dict(headers:list, data:list) -> dict:
    
    # Get indexes of data
    list_indexes = [i for i in range(len(data[2])) if data[2][i] != ""]
    info_indexes = [i for i in range(len(data[2])) if data[2][i] == ""]
    
    # Create curve
    curve = {}
    for index in list_indexes:
        value_list = [float(d[index]) for d in data]
        value_list = get_thinned_list(value_list, 200)
        curve[headers[index]] = value_list
    for index in info_indexes:
        curve[headers[index]] = try_float_cast(data[0][index])

    # Remove data of tensile curves after 80% of the UTS
    if curve["type"] == "tensile":
        end_index = find_tensile_strain_to_failure(curve["stress"])
        end_strain = curve["strain"][end_index]
        curve = remove_data_after(curve, end_strain, "strain")

    # Return curve
    return curve

# Removes data from a curve
def remove_data(exp_data:dict, label:str, value:float=None) -> dict:

    # If the value is none, then don't remove anything
    if value == None:
        return exp_data

    # Create a copy of the curve with empty lists
    new_curve = deepcopy(exp_data)
    for header in new_curve.keys():
        if isinstance(new_curve[header], list) and len(new_curve[header]) == len(exp_data[label]):
            new_curve[header] = []
            
    # Remove data after specific value
    for i in range(len(exp_data[label])):
        if exp_data[label][i] > value:
            break
        for header in new_curve.keys():
            if isinstance(new_curve[header], list) and len(exp_data[header]) == len(exp_data[label]):
                new_curve[header].append(exp_data[header][i])
    
    # Return new data
    return new_curve

# Gets the curve dict given a file path
def get_exp_data(file_path:str) -> dict:
    with open(file_path, "r") as file:
        headers = file.readline().replace("\n","").split(",")
        data = [line.replace("\n","").split(",") for line in file.readlines()]
        exp_data = get_exp_data_dict(headers, data)
        return exp_data

# Gets simulation data from parameters
def get_sim_data(exp_info:list, params_str:str, model) -> dict:

    # Initialise
    params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]
    results_dict = {}

    # Iterate through experimental data
    for exp_dict in exp_info:

        # Only consider calibration data
        if CALIBRATION != None:
            if CALIBRATION and not exp_dict["calib"]:
                continue
            elif not CALIBRATION and exp_dict["calib"]:
                continue

        # Get experimental data
        exp_data = get_exp_data(exp_dict["path"])
        exp_data = remove_data(exp_data, "time", exp_dict["time_end"])
        for field in ["calib", "yield", "min_rate"]:
            exp_data[field] = exp_dict[field]
        curve = Curve(exp_data, model)

        # Prepare results list
        title = curve.get_exp_data()["title"]
        results_dict[title] = {"exp": exp_data, "sim": []}

        # Iterate through parameters
        for params in params_list:
            model.set_exp_data(exp_data)
            calibrated_model = model.calibrate_model(*params)
            driver = Driver(curve, calibrated_model)
            results = driver.run()
            results_dict[title]["sim"].append(results)
    
    # Return dictionary
    return results_dict

# Extracts two lists of experimental and simulated data
def extract_results(results_dict:dict, data_type:str) -> tuple:
    
    # Initialise
    first_dict = results_dict[list(results_dict.keys())[0]]
    num_sims = len(first_dict["sim"])
    exp_data_list = [[] for _ in range(num_sims)]
    sim_data_list = [[] for _ in range(num_sims)]

    # Iterate through results dictionary
    for title in results_dict.keys():
        exp_data = results_dict[title]["exp"]
        if exp_data["type"] != data_type:
            continue
        for i in range(num_sims):
            exp_data_list[i].append(exp_data)
            sim_data_list[i].append(results_dict[title]["sim"][i])
    
    # Return everything
    return exp_data_list, sim_data_list

# Gets the averaged relative error
def get_ARE(exp_list:list, sim_list:list) -> float:
    sre_list = []
    for i in range(len(exp_list)):
        sre = ((sim_list[i]-exp_list[i])/exp_list[i])**2
        sre_list.append(sre)
    objective_value = np.average(sre_list)
    # re_list = []
    # for i in range(len(exp_list)):
    #     re = abs((sim_list[i]-exp_list[i])/exp_list[i])
    #     re_list.append(re)
    # objective_value = np.average(re_list)
    return objective_value

# Gets the average relative error for the common area
def get_area_ARE(exp_data:dict, sim_data:dict, x_label:str, y_label:str) -> tuple:
    min_x_end = min(exp_data[x_label][-1], sim_data[x_label][-1])
    x_list = np.linspace(0, min_x_end, 50)
    exp_interp = Interpolator(exp_data[x_label], exp_data[y_label])
    exp_y_list = exp_interp.evaluate(x_list)
    sim_interp = Interpolator(sim_data[x_label], sim_data[y_label])
    sim_y_list = sim_interp.evaluate(x_list)
    objective_value = get_ARE(exp_y_list, sim_y_list)
    return objective_value

# Gets the objective value for the areas
def get_area(results_dict:dict, data_type:str, x_label:str, y_label:str) -> list:
    objective_values = []
    exp_data_list, sim_data_list = extract_results(results_dict, data_type)
    for i in range(len(exp_data_list)):
        area_errors = []
        for exp_data, sim_data in zip(exp_data_list[i], sim_data_list[i]):
            area_error = get_area_ARE(exp_data, sim_data, x_label, y_label)
            area_errors.append(area_error)
        objective_values.append(np.average(area_errors))
    return objective_values

# Gets the objective value for the minimum rate
def get_mr(results_dict:dict, data_type:str, x_label:str, y_label:str) -> list:
    objective_values = []
    exp_data_list, sim_data_list = extract_results(results_dict, data_type)
    for i in range(len(exp_data_list)):
        exp_mr_list = [exp_data["min_rate"] for exp_data in exp_data_list[i]]
        sim_mr_list = []
        for sim_data in sim_data_list[i]:
            sim_interpolator = Interpolator(sim_data[x_label], sim_data[y_label])
            sim_interpolator.differentiate()
            sim_rate = sim_interpolator.evaluate(sim_data[x_label])
            sim_mr = sim_rate[len(sim_rate)//2]*3600
            sim_mr_list.append(sim_mr)
        objective_value = get_ARE(exp_mr_list, sim_mr_list)
        objective_values.append(objective_value)
    return objective_values

# Gets the objective value for the max point
def get_max(results_dict:dict, data_type:str, label:str) -> list:
    objective_values = []
    exp_data_list, sim_data_list = extract_results(results_dict, data_type)
    for i in range(len(exp_data_list)):
        exp_max_list = [max(exp_data[label]) for exp_data in exp_data_list[i]]
        sim_max_list = [max(sim_data[label]) for sim_data in sim_data_list[i]]
        objective_value = get_ARE(exp_max_list, sim_max_list)
        objective_values.append(objective_value)
    return objective_values

# Gets the yield stress
def get_yield_stress(results_dict:dict, data_type:str) -> list:
    objective_values = []
    exp_data_list, sim_data_list = extract_results(results_dict, data_type)
    for i in range(len(exp_data_list)):
        exp_end_list = [exp_data["yield"] for exp_data in exp_data_list[i]]
        sim_end_list = [get_yield(sim_data["strain"], sim_data["stress"])[1]
                        for sim_data in sim_data_list[i]]
        objective_value = get_ARE(exp_end_list, sim_end_list)
        objective_values.append(objective_value)
    return objective_values

# Gets the objective value for the end point
def get_end(results_dict:dict, data_type:str, label:str) -> list:
    objective_values = []
    exp_data_list, sim_data_list = extract_results(results_dict, data_type)
    for i in range(len(exp_data_list)):
        exp_yield_list = [exp_data[label][-1] for exp_data in exp_data_list[i]]
        sim_yield_list = [sim_data[label][-1] for sim_data in sim_data_list[i]]
        objective_value = get_ARE(exp_yield_list, sim_yield_list)
        objective_values.append(objective_value)
    return objective_values

# Transposes a 2D list of lists
def transpose(list_of_lists:list) -> list:
    transposed = np.array(list_of_lists).T.tolist()
    return transposed

# Initialise plots
fig, axes = plt.subplots(ncols=len(OPTIONS), nrows=1, figsize=(len(OPTIONS)*2, 5))
fig.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.8, wspace=0.5)
colour_list = ["red", "blue"]
rgb_list = [(255, 193, 184), (182, 190, 242)]

# Run simulations
opt_2_results_dict = get_sim_data(EXP_INFO_LIST, MODEL["opt_params"][0], MODEL["object"])
oth_2_results_dict = get_sim_data(EXP_INFO_LIST, MODEL["oth_params"][0], MODEL["object"])
opt_3_results_dict = get_sim_data(EXP_INFO_LIST, MODEL["opt_params"][1], MODEL["object"])
oth_3_results_dict = get_sim_data(EXP_INFO_LIST, MODEL["oth_params"][1], MODEL["object"])

# Calculate all objective values
ov_2_list = []
ov_3_list = []
for option in OPTIONS:
    ov_2 = option["handle"](opt_2_results_dict) + option["handle"](oth_2_results_dict)
    ov_3 = option["handle"](opt_3_results_dict) + option["handle"](oth_3_results_dict)
    ov_2_list.append(ov_2)
    ov_3_list.append(ov_3)

# Calculate averaged objective values
ov_2_avg = [np.average(ov_2) for ov_2 in transpose(ov_2_list)]
ov_3_avg = [np.average(ov_3) for ov_3 in transpose(ov_3_list)]
opt_index = ov_3_avg.index(min(ov_3_avg))

# Plot all objective values
for i, (axis, option) in enumerate(zip(axes, OPTIONS)):

    # Format boxplots
    ov_list = [ov_2_list[i], ov_3_list[i]]
    box_plots = axis.boxplot(ov_list, patch_artist=True, showfliers=False, widths=0.5)
    for j, ov in enumerate(ov_list):
        rgb = [rgb/255 for rgb in rgb_list[j]]
        box_plots["boxes"][j].set(linewidth=1, edgecolor="black", facecolor=rgb)
        box_plots["medians"][j].set_color("black")
        axis.scatter([j+1], ov[0], marker="o", color=colour_list[j], edgecolors="black", linewidth=1, s=8**2, zorder=3)
        # x_list = np.random.normal(i + 1, 0.05, len(ov))
        # axis.scatter(x_list[1:], y_list[1:], marker="o", color=colour_list[i], edgecolors="black", linewidth=1, s=5**2,  zorder=2, alpha=0.5)
    
    # Apply general format
    axis.set_title(option["info"], fontsize=16, pad=25)
    axis.tick_params(axis="y", labelsize=13)
    axis.yaxis.major.formatter._useMathText = True
    axis.set_xticks([])
    axis.set_xticklabels([])
    axis.set_ylim(option["limit"])
    axis.grid(axis="y")

    # Apply option specific format
    if option["name"] in ["ts_strain_d", "cr_strain"]:
        axis.ticklabel_format(axis="y", style="sci", scilimits=(-1,-1))
    else:
        axis.ticklabel_format(axis="y", style="sci", scilimits=(-2,-2))

# Save
plt.savefig(f"st_{MODEL['name']}.png")
