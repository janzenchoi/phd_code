# Libraries
import sys; sys.path += [".."]
from osfem.general import csv_to_dict, dict_to_csv, round_sf
from osfem.data import get_creep, split_data_list
from osfem.modeller import Modeller
import numpy as np

# Define model
RESULTS_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/symbolic"
RESULTS_LIST = [

    # # Minimum creep rate
    # "2025-10-03 cbc_mcr_2/251003123455_cbc_mcr_all",
    # "2025-10-03 cbc_mcr_2/251003124144_cbc_mcr_all",
    # "2025-10-03 cbc_mcr_2/251003124310_cbc_mcr_all",
    # "2025-10-03 cbc_mcr_2/251003124628_cbc_mcr_all",
    # "2025-10-03 cbc_mcr_2/251003124838_cbc_mcr_all",

    # # Time-to-failure
    # "2025-10-03 cbc_ttf_2/251003132310_cbc_ttf_all",
    # "2025-10-03 cbc_ttf_2/251003132529_cbc_ttf_all",
    # "2025-10-03 cbc_ttf_2/251003132831_cbc_ttf_all",
    # "2025-10-03 cbc_ttf_2/251003141842_cbc_ttf_all",
    # "2025-10-03 cbc_ttf_2/251003142006_cbc_ttf_all",

    # Strain-to-failure
    # "2025-10-03 cbc_stf_2/251003133546_cbc_stf_all",
    # "2025-10-03 cbc_stf_2/251003133805_cbc_stf_all",
    # "2025-10-03 cbc_stf_2/251003133904_cbc_stf_all",
    # "2025-10-03 cbc_stf_2/251003134305_cbc_stf_all",
    # "2025-10-03 cbc_stf_2/251003134505_cbc_stf_all",

    # # Minimum creep rate, logged
    # "2025-10-20 cbc_mcr_log/251020222530_cbc_mcr_log",
    # "2025-10-20 cbc_mcr_log/251020222707_cbc_mcr_log",
    # "2025-10-20 cbc_mcr_log/251020222920_cbc_mcr_log",
    # "2025-10-20 cbc_mcr_log/251020224437_cbc_mcr_log",
    # "2025-10-20 cbc_mcr_log/251020224557_cbc_mcr_log",

    # # Time-to-failure, logged
    # "2025-10-20 cbc_ttf_log/251020225520_cbc_ttf_log",
    # "2025-10-20 cbc_ttf_log/251020225742_cbc_ttf_log",
    # "2025-10-20 cbc_ttf_log/251020230039_cbc_ttf_log",
    # "2025-10-20 cbc_ttf_log/251020230238_cbc_ttf_log",
    # "2025-10-20 cbc_ttf_log/251020230436_cbc_ttf_log",

    # Strain-to-failure, logged
    "2025-10-20 cbc_stf_log/251020232834_cbc_stf_log",
    "2025-10-20 cbc_stf_log/251020232939_cbc_stf_log",
    "2025-10-20 cbc_stf_log/251020233043_cbc_stf_log",
    "2025-10-20 cbc_stf_log/251020233358_cbc_stf_log",
    "2025-10-20 cbc_stf_log/251020233501_cbc_stf_log",
]

# Read experimental data
data_list = get_creep("data")
data_list = [data.update({"stress": data["stress"]/80}) or data for data in data_list]
data_list = [data.update({"temperature": data["temperature"]/1000}) or data for data in data_list]
cal_data_list, val_data_list = split_data_list(data_list)

# Identify optimal simulation
cal_are_list = [csv_to_dict(f"{RESULTS_PATH}/{folder}/are.txt")["are"][0] for folder in RESULTS_LIST]
opt_index = cal_are_list.index(min(cal_are_list))
print(opt_index)

# Initialise model
field = [field for field in ["mcr", "ttf", "stf"] if field in RESULTS_LIST[0]][0]
file_paths = [f"{RESULTS_PATH}/{folder}/data_fit.csv" for folder in RESULTS_LIST]
modeller = Modeller("sr_model", results_path="results", file_paths=file_paths)
modeller.field = field

# Save results
params_list = [[i] for i in range(len(file_paths))]
modeller.plot_1to1s(cal_data_list, val_data_list, params_list, opt_index)

# Save errors
cal_are = [modeller.get_are(cal_data_list, [i]) for i in range(len(RESULTS_LIST))]
val_are = [modeller.get_are(val_data_list, [i]) for i in range(len(RESULTS_LIST))]
avg_cal_cov = modeller.get_cov(cal_data_list, [[i] for i in range(len(RESULTS_LIST))])
avg_val_cov = modeller.get_cov(val_data_list, [[i] for i in range(len(RESULTS_LIST))])
print(round_sf(np.average(cal_are), 5))
print(round_sf(np.average(val_are), 5))
print(round_sf(avg_cal_cov, 5))
print(round_sf(avg_val_cov, 5))
# dict_to_csv(error_dict, "results/errors.csv")
