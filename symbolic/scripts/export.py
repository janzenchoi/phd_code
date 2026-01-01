import os
import sys; sys.path += [".."]
from symbolic.io.files import csv_to_dict, dict_to_stdout

# Constants
INPUT_PATH  = "results"
FILE_NAME   = "error.csv"

# Read data
dir_path_list = os.listdir(INPUT_PATH)
headers = ["path", "cal_nrmse", "val_nrmse", "cal_anrmse", "val_anrmse"]
summary_dict = dict(zip(headers, [[] for _ in headers]))

# Iterate through results
for dir_path in dir_path_list:

    # Read data
    file_path = f"{INPUT_PATH}/{dir_path}/{FILE_NAME}"
    if not os.path.exists(file_path):
        continue

    # Add data
    data_dict = csv_to_dict(file_path)
    summary_dict["path"].append(dir_path)
    for header in headers[1:]:
        summary_dict[header].append(data_dict[header])

# Output summary
dict_to_stdout(summary_dict)
