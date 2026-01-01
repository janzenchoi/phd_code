import os
import sys; sys.path += ["../.."]
from opt_all.helper.general import flatten, csv_to_dict, dict_to_csv, dict_to_stdout

# Parameters
PARAM_NAMES = ["a", "b", "c", "d"] # theta
INPUT_PATH  = "../results/2025-10-06 theta_6"
OUTPUT_PATH = f"{INPUT_PATH}/params_fit.csv"

# Initialise
headers = flatten([[f"{pn}{i+1}" for pn in "abcd"] for i in range(6)])
params_dict = dict(zip(headers, [[] for _ in range(len(headers))]))

# Identify all super directories
super_dir_path_list = [f"{INPUT_PATH}/{path}" for path in os.listdir(INPUT_PATH)]

# Iterate through all super directories
for super_dir_path in super_dir_path_list:

    # Ignore files
    if not os.path.isdir(super_dir_path):
        continue

    # Iterate through parameter data
    dir_path_list = [f"{super_dir_path}/{dir_path}" for dir_path in os.listdir(super_dir_path) if "param_t" in dir_path]
    for dir_path in dir_path_list:

        # Read parameters
        data_dict = csv_to_dict(f"{dir_path}/params.csv")
        number = dir_path[-1]

        # Append parameters
        for pn in PARAM_NAMES:
            param_name = f"Param ({pn})"
            if param_name in data_dict.keys():
                param_value = data_dict[param_name][0]
                params_dict[f"{pn}{number}"].append(param_value)

# Save parameters
dict_to_csv(params_dict, OUTPUT_PATH)
dict_to_stdout(params_dict)
