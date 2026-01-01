# Libraries
import sys; sys.path += [".."]
from osfem.general import csv_to_dict
from osfem.bar import plot_bar
from osfem.plotter import save_plot

# Model information
SUMMARY_PATH = "/mnt/c/Users/janzen/OneDrive - UNSW/H0419460/results/osfem/summary.csv"
# MODELS = ["mcr_arr", "mcr_alt", "mcr_bar", "mcr_sr"]
# NAMES =  ["Norton-\nArrhenius", "Altenbach-\nArrhenius", "Garofalo-\nArrhenius", "Symbolic\nRegression"]
# MODELS = ["ttf_mg",  "ttf_dsm", "ttf_llm", "ttf_sr"]
# NAMES =  ["Monkman-\nGrant", "Dorn-\nShepherd", "Larson-\nMiller", "Symbolic\nRegression"]
# MODELS = ["stf_mmg", "stf_efm", "stf_sfm", "stf_sr"]
# NAMES =  ["Dobes", "Evans", "Soares", "Symbolic\nRegression"]
MODELS = ["strain_omega", "strain_phi", "strain_theta", "strain_sr"]
NAMES =  ["Omega", "Phi", "Theta\nProj.", "Symbolic\nRegression"]
# MODELS = ["ox_omega", "ox_phi", "ox_theta", "ox_sr"]
# NAMES =  ["Omega", "Phi", "Theta\nProj.", "Symbolic\nRegression"]

# Model information 2
# MODELS = ["mcr_arr", "mcr_alt", "mcr_bar", "mcr_2"]
# NAMES =  ["Norton-\nArrhenius", "Altenbach-\nArrhenius", "Garofalo-\nArrhenius", "Symbolic\nRegression"]
# MODELS = ["ttf_mg",  "ttf_dsm", "ttf_llm", "ttf_2"]
# NAMES =  ["Monkman-\nGrant", "Dorn-\nShepherd", "Larson-\nMiller", "Symbolic\nRegression"]
# MODELS = ["stf_mmg", "stf_efm", "stf_sfm", "stf_2"]
# NAMES =  ["Dobes", "Evans", "Soares", "Symbolic\nRegression"]

# SR comparison
# MODELS = ["mcr_sr", "ttf_sr", "stf_sr", "ox_sr"]
# NAMES = ["Minimum\ncreep rate", "Time-to-\nfailure", "Strain-to-\nfailure", "Mechanism-\nshifted\nstrain-time"]
# MODELS = ["mcr_2", "ttf_2", "stf_2", "ox_sr_p1"]
# NAMES = ["Minimum\ncreep rate", "Time-to-\nfailure", "Strain-to-\nfailure", "Mechanism-\nshifted\nstrain-time"]

# Read data
summary_dict = csv_to_dict(SUMMARY_PATH)
are_grid = [summary_dict[model][0:2] for model in MODELS]
cov_grid = [summary_dict[model][2:4] for model in MODELS]

# Plot
plot_bar(are_grid, (0, 80), "Average RE (%)", NAMES)
save_plot("results/are.png")
plot_bar(cov_grid, (0, 40), "Average CV (%)", NAMES)
save_plot("results/cov.png")
