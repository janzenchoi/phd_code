"""
 Title:         Summarise
 Description:   Summarises the results of the sampled simulations
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += ["../.."]
import os
from moose_sim.analyse.pole_figure import IPF, get_lattice
from moose_sim.helper.general import transpose, round_sf
from moose_sim.helper.io import csv_to_dict, dict_to_csv

# Constants
SIM_PATH = "/mnt/c/Users/z5208868/OneDrive - UNSW/H0419460/results/moose_sim/2024-08-01 (617_s3_sm)"
PARAMS = ["cp_tau_s", "cp_b", "cp_tau_0", "cp_n"]

def get_param_dict(params_path:str) -> dict:
    """
    Gets the parameters from a file
    
    Parameters:
    * `params_path`: The path to the parameters file
    
    Returns a dictionary of the parameter values
    """
    with open(params_path, "r") as fh:
        line_list = [line.replace("\n", "").replace(":", "") for line in fh.readlines()]
        param_dict = {line.split(" ")[0]: float(line.split(" ")[1]) for line in line_list
                      if line.split(" ")[0] in PARAMS}
        return param_dict

def get_trajectories(data_dict:dict) -> dict:
    """
    Gets the reorientation trajectories

    Parameters:
    * `data_dict`: The data dictionary
    
    Return trajectories as a dictoinary of lists of euler angles
    """
    grain_ids = [int(key.replace("g","").replace("_phi_1",""))
                 for key in data_dict.keys() if "_phi_1" in key]
    trajectories = {}
    for grain_id in grain_ids:
        trajectory = [data_dict[f"g{grain_id}_{phi}"] for phi in ["phi_1", "Phi", "phi_2"]]
        trajectory = transpose(trajectory)
        trajectories[grain_id] = trajectory
    return trajectories

# Read all summary files
dir_path_list = [f"{SIM_PATH}/{dir_path}" for dir_path in os.listdir(SIM_PATH)
            if os.path.exists(f"{SIM_PATH}/{dir_path}/summary.csv")]
summary_path_list = [f"{dir_path}/summary.csv" for dir_path in dir_path_list]
summary_dict_list = [csv_to_dict(summary_path) for summary_path in summary_path_list]
param_dict_list = [get_param_dict(f"{dir_path}/params.txt") for dir_path in dir_path_list]
print(len(param_dict_list))

# Initialise IPF-100
lattice = get_lattice("fcc")
ipf = IPF(lattice)
get_ipf = lambda euler : ipf.get_points(euler, [1,0,0])

# Convert euler-bunge angles into IPF-100 coordinates
for summary_dict in summary_dict_list:
    
    # Get trajectories
    trajectories = get_trajectories(summary_dict)
    
    # Remove euler-bunge angles
    phi_keys = [key for key in summary_dict.keys() if "phi" in key.lower()]
    for phi_key in phi_keys:
        summary_dict.pop(phi_key)

    # Convert trajectories into IPF-100 values
    for grain_id in trajectories.keys():
        ipf_xy = [get_ipf(euler) for euler in trajectories[grain_id]]
        summary_dict[f"g{grain_id}_ipf_x"] = round_sf([xy[0][0] for xy in ipf_xy], 5)
        summary_dict[f"g{grain_id}_ipf_y"] = round_sf([xy[0][1] for xy in ipf_xy], 5)
        
# Initialise a summary dictionary for the summaries
key_list = list(param_dict_list[0].keys()) + list(summary_dict_list[0].keys())
super_summary_dict = dict(zip(key_list, [[] for _ in range(len(key_list))]))
first_key = [list(summary_dict_list[0].keys())][0][0]
num_values = len(summary_dict_list[0][first_key])
print(num_values)

# Iterate through the results
for summary_dict, param_dict in zip(summary_dict_list, param_dict_list):
    for key in param_dict:
        super_summary_dict[key] += [param_dict[key]]*(num_values-1)
    for key in summary_dict:
        super_summary_dict[key] += round_sf(summary_dict[key][1:], 5)
         
# Save the super summary dictionary
dict_to_csv(super_summary_dict, "summary.csv")
