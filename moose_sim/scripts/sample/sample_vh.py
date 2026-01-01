"""
 Title:         Sample 617_s3
 Description:   Runs the CPFEM model using CCD
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += ["../.."]
import math
from moose_sim.interface import Interface
from moose_sim.helper.io import csv_to_dict
from moose_sim.helper.interpolator import intervaluate

# Constants
NUM_PARALLEL   = 4
NUM_PROCESSORS = 48
MAX_DURATION   = 100000
TARGET_DIR     = "../data/617_s3/40um_micro"
PARAMS_PATH    = "params.csv"

# Get CP parameters
params_dict = csv_to_dict(PARAMS_PATH)
param_dict_list = [dict(zip(params_dict.keys(), values)) for values in zip(*params_dict.values())]

# Section CP parameter list for script
sim_id     = int(sys.argv[1])
max_num_sims = math.ceil(len(param_dict_list)/NUM_PARALLEL)
index_list = [NUM_PARALLEL*i+sim_id for i in range(max_num_sims) if NUM_PARALLEL*i+sim_id < len(param_dict_list)]
param_dict_list = [param_dict_list[i] for i in index_list]

# Iterate through CP parameter list
for i, cp_param_dict in enumerate(param_dict_list):

    # Initialise
    index_str = str(i+1).zfill(2)
    itf = Interface(
        title       = f"{sim_id}_{index_str}",
        input_path  = TARGET_DIR,
        output_path = "../results/",
    )

    # Define the mesh
    itf.define_mesh("mesh.e", "element_stats.csv", degrees=False, active=False)
    dimensions = itf.get_dimensions()

    # Defines the material parameters
    itf.define_material(
        material_path   = "deer/cpvh_ae",
        material_params = cp_param_dict,
        c_11            = 250000,
        c_12            = 151000,
        c_44            = 123000,
    )

    # Define end time and strain
    exp_dict = csv_to_dict("../data/617_s3/617_s3_exp.csv")
    end_time = exp_dict["time_intervals"][-1]
    end_strain = (math.exp(exp_dict["strain_intervals"][-1])-1)*dimensions["x"]
    # max_strain = 0.10
    # end_time = intervaluate(exp_dict["strain_intervals"], exp_dict["time_intervals"], max_strain)
    # end_strain = (math.exp(max_strain)-1)*dimensions["x"]
    
    # Defines the simulation parameters
    itf.define_simulation(
        simulation_path = "deer/1to1_ui_cp",
        end_time        = end_time,
        end_strain      = end_strain
    )

    # Runs the model and saves results
    itf.export_params()
    itf.simulate("~/moose/deer/deer-opt", NUM_PROCESSORS, MAX_DURATION)

    # Conduct post processing
    itf.compress_csv(sf=5, exclude=["x", "y", "z"])
    itf.post_process(grain_map_path=f"{TARGET_DIR}/grain_map.csv")
    itf.remove_files(["mesh.e", "element_stats.csv", "results", "simulation_out_cp"])
