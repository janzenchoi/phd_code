import sys; sys.path += [".."]
from osfem.general import csv_to_dict, flatten, dict_to_stdout, dict_to_csv
import os

INPUT_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/osfem"
MODEL_NAMES = [
    "mcr_arr", "mcr_bar", "mcr_alt",
    "ttf_mg",  "ttf_dsm", "ttf_llm",
    "stf_mmg", "stf_efm", "stf_sfm",
]

dir_path_list = [f"{INPUT_PATH}/{ip}/error.csv" for ip in os.listdir(INPUT_PATH)]

headers = flatten([[f"{mn}_cal", f"{mn}_val"] for mn in MODEL_NAMES])
summary_dict = dict(zip(headers, [[] for _ in range(len(headers))]))

for mn in MODEL_NAMES:
    dir_path = [dp for dp in dir_path_list if mn in dp][0]
    data_dict = csv_to_dict(dir_path)
    summary_dict[f"{mn}_cal"] += data_dict["cal_are"]
    summary_dict[f"{mn}_val"] += data_dict["val_are"]

dict_to_stdout(summary_dict)
dict_to_csv(summary_dict, "results/all_errors.csv")
