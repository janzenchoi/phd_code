# Libraries
import sys; sys.path += [".."]
from osfem.general import transpose, csv_to_dict, dict_to_csv, round_sf, get_file_path_exists
from osfem.data import get_creep, split_data_list
from osfem.boxplot import plot_boxplots
from osfem.modeller import Modeller
import numpy as np

# Define model
RESULTS_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/osfem"
# RESULTS_DIR = "250921223703_mcr_arr"
# RESULTS_DIR = "250921223552_mcr_bar"
# RESULTS_DIR = "250921225625_mcr_alt"
# RESULTS_DIR = "250921230858_ttf_mg"
# RESULTS_DIR = "250922002344_ttf_dsm"
# RESULTS_DIR = "250922004852_ttf_llm"
# RESULTS_DIR = "250921230842_stf_mmg"
# RESULTS_DIR = "250921174944_stf_efm"
# RESULTS_DIR = "250921172053_stf_sfm"

RESULTS_DIR_LIST = [
    # "250921223703_mcr_arr",
    # "250921225625_mcr_alt",
    # "250921223552_mcr_bar",
    # "250921230858_ttf_mg",
    # "250922002344_ttf_dsm",
    # "250922004852_ttf_llm",
    "250921230842_stf_mmg",
    # "250921174944_stf_efm",
    # "250921172053_stf_sfm",
]

summary_dict = {}

for results_dir in RESULTS_DIR_LIST:

    # Read experimental data
    data_list = get_creep("data")
    data_list = [data.update({"stress": data["stress"]/80}) or data for data in data_list]
    data_list = [data.update({"temperature": data["temperature"]/1000}) or data for data in data_list]
    cal_data_list, val_data_list = split_data_list(data_list)

    # Read simulated data
    sim_path = f"{RESULTS_PATH}/{results_dir}/error.csv"
    sim_dict = csv_to_dict(sim_path)

    # Identify optimal simulation
    cal_are = sim_dict["cal_are"]
    val_are = sim_dict["val_are"]
    opt_index = cal_are.index(min(cal_are))

    # Get all parameters
    param_names = list(sim_dict.keys())
    param_names.remove("cal_are")
    param_names.remove("val_are")
    params_list = transpose([sim_dict[pn] for pn in param_names])

    # Initialise model
    model_name = "_".join(results_dir.split("_")[1:])
    modeller = Modeller(model_name, results_path="results")

    # Save results
    modeller.plot_1to1s(cal_data_list, val_data_list, params_list, opt_index)
    # boxplot_path = get_file_path_exists(modeller.get_output_path("boxplots"), "png")
    boxplot_path = modeller.get_output_path("boxplots.png")
    plot_boxplots(
        label_list  = modeller.get_info("label"),
        values_list = transpose(params_list),
        limits_list = modeller.get_info("limits"),
        opt_index   = opt_index,
        output_path = boxplot_path,
        max_size    = 5,
    )

    # Calculate errors and variability and add to dictionary
    avg_cal_are = np.average(cal_are)
    avg_val_are = np.average(val_are)
    avg_cal_cov = modeller.get_cov(cal_data_list, params_list)
    avg_val_cov = modeller.get_cov(val_data_list, params_list)
    summary_dict[model_name] = round_sf([avg_cal_are, avg_val_are, avg_cal_cov, avg_val_cov], 5)

# Save summary
dict_to_csv(summary_dict, "results/summary.csv")
