import os
import sys; sys.path += [".."]
from opt_all.helper.general import csv_to_dict, dict_to_csv, dict_to_stdout

# Constants
# PARAM_NAMES = ["t1", "t2", "t3", "t4"] # theta
# OUTPUT_PATH  = "results/theta"
# PARAM_NAMES = ["o1", "o2", "o3", "o4"] # omega
# OUTPUT_PATH  = "results/omega"
PARAM_NAMES = ["phi_1", "phi_2", "phi_3", "phi_4"] # phi
# OUTPUT_PATH  = "results/2025-10-05 phi_individual"
OUTPUT_PATH  = "results/2025-10-08 phi"
# OUTPUT_PATH  = "results/2025-10-08 phi_ox"

# Define data
CAL_ALL = False
DATA_LIST = [
    {"path": "inl_1/AirBase_800_80_G25.csv",  "fit": True, "tts": 2174580,  "ox": None},
    {"path": "inl_1/AirBase_800_70_G44.csv",  "fit": True, "tts": 4951332,  "ox": None},
    {"path": "inl_1/AirBase_800_65_G33.csv",  "fit": CAL_ALL, "tts": 7927344,  "ox": None},
    {"path": "inl_1/AirBase_800_60_G32.csv",  "fit": CAL_ALL, "tts": 12509442, "ox": None},
    {"path": "inl_1/AirBase_900_36_G22.csv",  "fit": True, "tts": 2484756,  "ox": None},
    {"path": "inl_1/AirBase_900_31_G50.csv",  "fit": True, "tts": 5122962,  "ox": None},
    {"path": "inl_1/AirBase_900_28_G45.csv",  "fit": CAL_ALL, "tts": 6807168,  "ox": None},
    {"path": "inl_1/AirBase_900_26_G59.csv",  "fit": CAL_ALL, "tts": 10289304, "ox": 20578608},
    {"path": "inl_1/AirBase_1000_16_G18.csv", "fit": True, "tts": 3883572,  "ox": 7767144},
    {"path": "inl_1/AirBase_1000_13_G30.csv", "fit": True, "tts": 8448138,  "ox": 16896276},
    {"path": "inl_1/AirBase_1000_12_G48.csv", "fit": CAL_ALL, "tts": 9102942,  "ox": 18205884},
    {"path": "inl_1/AirBase_1000_11_G39.csv", "fit": CAL_ALL, "tts": 9765990,  "ox": 19531980},
]

# Initialise
dir_path_list = os.listdir(OUTPUT_PATH)
headers = ["stress", "temperature"] + PARAM_NAMES
cal_dict = dict(zip(headers, [[] for _ in headers]))
val_dict = dict(zip(headers, [[] for _ in headers]))

# Iterate through results
for dir_path, data in zip(dir_path_list, DATA_LIST):

    # Read data
    file_path = f"{OUTPUT_PATH}/{dir_path}/params.csv"
    if not os.path.exists(file_path):
        continue

    # Append test conditions
    data_info = dir_path.split("_")
    if data["fit"]:
        cal_dict["temperature"].append(int(data_info[2])/1000)
        cal_dict["stress"].append(int(data_info[3])/80)
    else:
        val_dict["temperature"].append(int(data_info[2])/1000)
        val_dict["stress"].append(int(data_info[3])/80)

    # Append parameters
    data_dict = csv_to_dict(file_path)
    for pn in PARAM_NAMES:
        param_name = f"Param ({pn})"
        if param_name in data_dict.keys():
            param_value = data_dict[param_name][0]
            if data["fit"]:
                cal_dict[pn].append(param_value)
            else:
                val_dict[pn].append(param_value)

# Save parameters
dict_to_csv(cal_dict, f"{OUTPUT_PATH}/params_cal.csv")
dict_to_csv(val_dict, f"{OUTPUT_PATH}/params_val.csv")
