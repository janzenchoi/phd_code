import os
import sys; sys.path += [".."]
from symbolic.io.files import csv_to_dict, dict_to_stdout

# Constants
INPUT_PATH  = "results"
FILE_NAME   = "are.txt"

# Read data
dir_path_list = os.listdir(INPUT_PATH)
headers = ["path", "cal_are", "val_are"]
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
    summary_dict["cal_are"].append(data_dict["are"][0])
    summary_dict["val_are"].append(data_dict["are"][1])

# Output summary
dict_to_stdout(summary_dict)
