"""
 Title:         Analyser
 Description:   Analyses the summarised results
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += ["../.."]
from moose_sim.helper.io import csv_to_dict
from moose_sim.helper.general import transpose
from moose_sim.analyse.plotter import save_plot, Plotter
from moose_sim.analyse.pole_figure import IPF, get_lattice

# Constants
SAMPLE_PATH = "617_s3_sampled.csv"
# EXP_PATH    = "../data/617_s3/617_s3_exp.csv"
EXP_PATH    = "../data/617_s3_20um_exp.csv"
# GRAIN_IDS = [164, 173, 265, 213, 207]
GRAIN_IDS = [1, 21, 24, 28, 31] # 20um
# GRAIN_IDS = [5, 34, 37, 50, 47]
NUM_DATA = 32 # per simulation

# Read sampled data
sample_dict = csv_to_dict("617_s3_sampled.csv")
total_data = len(list(sample_dict.values())[0])
indexes_list = [list(range(total_data))[i:i+NUM_DATA] for i in range(0, total_data, NUM_DATA)]

# Initialise IPF
ipf = IPF(get_lattice("fcc"))
direction = [1,0,0]
colour_list = ["red", "blue", "green", "orange", "purple"]*10

# Plot experimental trajectories
exp_data = csv_to_dict(EXP_PATH)
exp_trajectories = [transpose([exp_data[f"g{grain_id}_{phi}"] for phi in ["phi_1", "Phi", "phi_2"]]) for grain_id in GRAIN_IDS]
ipf.plot_ipf_trajectory(exp_trajectories, direction, "plot", {"color": "silver", "linewidth": 2})
ipf.plot_ipf_trajectory(exp_trajectories, direction, "arrow", {"color": "silver", "head_width": 0.01, "head_length": 0.015})
ipf.plot_ipf_trajectory([[et[0]] for et in exp_trajectories], direction, "scatter", {"color": "silver", "s": 8**2})
for exp_trajectory, grain_id in zip(exp_trajectories, GRAIN_IDS):
    ipf.plot_ipf_trajectory([[exp_trajectory[0]]], direction, "text", {"color": "black", "fontsize": 8, "s": grain_id})

# Iterate through grains
for j, index_list in enumerate(indexes_list):
    for grain_id, colour in zip(GRAIN_IDS, colour_list):
        trajectory = [[sample_dict[f"g{grain_id}_{phi}"][i] for phi in ["phi_1", "Phi", "phi_2"]] for i in index_list]
        ipf.plot_ipf_trajectory([trajectory], direction, "plot", {"color": colour, "linewidth": 2})
        ipf.plot_ipf_trajectory([trajectory], direction, "arrow", {"color": colour, "head_width": 0.01, "head_length": 0.015})
        ipf.plot_ipf_trajectory([[trajectory[0]]], direction, "scatter", {"color": colour, "s": 8**2})
    # save_plot(f"plot_rt_{j}.png")
save_plot("plot_rt.png")

# Plot stress-strain response
plotter = Plotter("strain", "stress", "mm/mm", "MPa")
plotter.prep_plot()
for index_list, colour in zip(indexes_list, colour_list):
    strain_list = [sample_dict["average_strain"][i] for i in index_list]
    stress_list = [sample_dict["average_stress"][i] for i in index_list]
    plotter.line_plot({"strain": [0]+strain_list, "stress": [0]+stress_list}, colour)
save_plot("plot_ss.png")
