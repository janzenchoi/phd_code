import os
import sys; sys.path += [".."]
from opt_all.helper.general import csv_to_dict, dict_to_csv, dict_to_stdout, flatten

# Constants
# PARAM_NAMES = ["a", "b", "c", "d"] # theta
PARAM_NAMES = flatten([[f"{pn}{i+1}" for i in range(4)] for pn in "anq"]) # phi
# INPUT_PATH  = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/opt_all/2025-10-07 phi_ox"
INPUT_PATH  = "results/2025-10-08 phi_ox"
OUTPUT_PATH = f"{INPUT_PATH}/params_fit.csv"

# Initialise
dir_path_list = os.listdir(INPUT_PATH)
headers = PARAM_NAMES
# headers = ["label", "error"] + PARAM_NAMES
summary_dict = dict(zip(headers, [[] for _ in headers]))

# Iterate through results
for dir_path in dir_path_list:

    # Read data
    file_path = f"{INPUT_PATH}/{dir_path}/params.csv"
    if not os.path.exists(file_path):
        continue

    # Add label for parameter
    # label = dir_path.split("_")[3]
    # summary_dict["label"].append(label)

    # Append parameters
    data_dict = csv_to_dict(file_path)
    for pn in PARAM_NAMES:
        param_name = f"Param ({pn})"
        if param_name in data_dict.keys():
            param_value = data_dict[param_name][0]
            summary_dict[pn].append(param_value)

    # Add error
    # summary_dict["error"].append(data_dict["Reduced Error"][0])

# Save parameters
dict_to_csv(summary_dict, OUTPUT_PATH)
dict_to_stdout(summary_dict)
