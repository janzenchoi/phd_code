# Libraries
import sys; sys.path += [".."]
from osfem.general import csv_to_dict, flatten
from osfem.boxplot import plot_boxplots

# Define model
# RESULTS_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/opt_all/2025-10-05 theta/params_fit.csv"
# OPT_INDEX = 2
# RESULTS_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/opt_all/2025-10-05 theta_ox/params_fit.csv"
# OPT_INDEX = 4
# RESULTS_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/opt_all/2025-10-04 omega/params_fit.csv"
# OPT_INDEX = 0
# RESULTS_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/opt_all/2025-10-04 omega_ox/params_fit.csv"
# OPT_INDEX = 3
# RESULTS_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/opt_all/2025-10-08 phi/params_fit.csv"
# OPT_INDEX = 4
RESULTS_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/opt_all/2025-10-08 phi_ox/params_fit.csv"
OPT_INDEX = 2
params_dict = csv_to_dict(RESULTS_PATH)

# Parameter names
# param_names = flatten([[f"{pn}{i+1}" for pn in ["a", "b", "c", "d"]] for i in range(4)])
# chunk_list = lambda lst, size : [lst[i:i + size] for i in range(0, len(lst), size)]
# sub_param_names_list = chunk_list(param_names, 6)
sub_param_names_list = ["a1", "n1", "q1", "a2"], ["n2", "q2", "a3", "n3"], ["q3", "a4", "n4", "q4"]

for i, sub_param_names in enumerate(sub_param_names_list):

    # label_list = [f"${spn[0]}_{spn[1]},TP$" for spn in sub_param_names]
    # label_list = ["$" + str(spn[0]) + "_{" + str(spn[1]) + "‚TP}$" for spn in sub_param_names]
    # label_list = ["$" + str(spn[0]) + "_{" + str(spn[1]) + "‚Om}$" for spn in sub_param_names]
    label_list = ["$" + str(spn[0]) + "_{" + str(spn[1]) + "‚Ph}$" for spn in sub_param_names]
    values_list = [params_dict[spn] for spn in sub_param_names]
    # limits_list = [(-100,100), (-200,200), (-100,100), (-200,200)]
    # limits_list = [(-50,50), (-100,100), (-50,50), (-100,100)]
    # limits_list = [(-100,100) if spn.startswith("a") or spn.startswith("c") else (-200,200) for spn in sub_param_names]
    # limits_list = [(0,100) if spn.startswith("a") or spn.startswith("q") else (0,1) for spn in sub_param_names]
    limits_list = [(0,1000) if spn.startswith("a") or spn.startswith("q") else (0,10) for spn in sub_param_names]

    plot_boxplots(
        label_list  = label_list,
        values_list = values_list,
        limits_list = limits_list,
        opt_index   = OPT_INDEX,
        output_path = f"results/boxplots_{i+1}",
        # max_size    = 6,
        max_size    = 4,
    )
