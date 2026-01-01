"""
 Title:         Generate LHS
 Description:   For generating parameter values using LHS
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += ["../.."]
from moose_sim.helper.sampler import get_lhs
from moose_sim.helper.io import dict_to_csv

# Constants
OUTPUT_PATH = "params.csv"

# # Get parameters for LH6
# bounds_dict = {
#     "cp_lh_0":    (0, 1000),
#     "cp_lh_1":    (0, 1000),
#     "cp_lh_2":    (0, 1000),
#     "cp_lh_3":    (0, 1000),
#     "cp_lh_4":    (0, 1000),
#     "cp_lh_5":    (0, 1000),
#     "cp_tau_0":   (0, 500),
#     "cp_n":       (1, 20),
#     "cp_gamma_0": (3.25e-5, 3.25e-5),
# }
# param_dict_list = get_lhs(bounds_dict, 72)

# # Get parameters for LH2
# bounds_dict = {
#     "cp_lh_0":    (0, 1000),
#     "cp_lh_1":    (0, 1000),
#     "cp_tau_0":   (0, 500),
#     "cp_n":       (1, 20),
#     "cp_gamma_0": (3.25e-5, 3.25e-5),
# }
# param_dict_list = get_lhs(bounds_dict, 32)

# Get parameters for VH
bounds_dict = {
    "cp_tau_s":   (0, 2000),
    "cp_b":       (0, 20),
    "cp_tau_0":   (0, 500),
    "cp_n":       (1, 20),
    "cp_gamma_0": (3.25e-5, 3.25e-5),
}
param_dict_list = get_lhs(bounds_dict, 8)

# Format parameters, save, and print progress
params_dict = {k: [d[k] for d in param_dict_list] for k in param_dict_list[0]}
dict_to_csv(params_dict, OUTPUT_PATH)
print(f"Generated {len(param_dict_list)} parameters using LHS for {list(param_dict_list[0].keys())}")
