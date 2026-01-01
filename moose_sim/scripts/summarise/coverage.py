"""
 Title:         Coverage
 Description:   Checks the coverage of the reorientation trajectories
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += ["../.."]
from moose_sim.helper.io import csv_to_dict
from moose_sim.helper.general import transpose
from moose_sim.analyse.plotter import save_plot
from moose_sim.analyse.pole_figure import IPF, get_lattice

# Constants
SMP_PATH = "617_s3_sampled.csv"
EXP_PATH = "../data/617_s3_20um_exp.csv"
NUM_DATA = 32 # per simulation

# Read experimental and simulation data
exp_dict = csv_to_dict("../data/617_s3_20um_exp.csv")
smp_dict = csv_to_dict(SMP_PATH)
total_data = len(list(smp_dict.values())[0])
indexes_list = [list(range(total_data))[i:i+NUM_DATA] for i in range(0, total_data, NUM_DATA)]

# Define reorientation trajectory information
grain_ids = [int(key.replace("g","").replace("_phi_1","")) for key in smp_dict.keys() if "phi_1" in key]
get_trajectory = lambda dict, grain_id : transpose([dict[f"g{grain_id}_{phi}"] for phi in ["phi_1", "Phi", "phi_2"]])

# Plot coverage of grain reorientations
for grain_id in grain_ids:
    
    # Initialise IPF plotter
    ipf = IPF(get_lattice("fcc"))
    direction = [1,0,0]

    # Plot simulation trajectory
    smp_trajectory = get_trajectory(smp_dict, grain_id)
    ipf.plot_ipf_trajectory([smp_trajectory], direction, "scatter", {"color": "blue", "s": 8**2})

    # Plot experimental trajectory
    exp_trajectory = get_trajectory(exp_dict, grain_id)
    ipf.plot_ipf_trajectory([exp_trajectory], direction, "plot", {"color": "red", "linewidth": 2})

    # Save
    save_plot(f"results/ipf_g{grain_id}")
