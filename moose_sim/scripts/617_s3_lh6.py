"""
 Title:         617_s3 latent hardening
 Description:   Runs the CPFEM model once with the latent hardening model
 References:    https://asmedigitalcollection.asme.org/pressurevesseltech/article/135/2/021502/378322/Synchrotron-Radiation-Study-on-Alloy-617-and-Alloy
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += [".."]
import math
from moose_sim.interface import Interface
from moose_sim.helper.io import csv_to_dict

# Define paths
# MESH_PATH = "data/617_s3/40um"
MESH_PATH = "data/617_s3/10um"
EXP_PATH  = "data/617_s3/617_s3_exp.csv"

# Simulation constants
ADD_EXODUS = True
EXODUS_PREFIX = "simulation_exodus"

# Define the mesh and orientations
itf = Interface(input_path=MESH_PATH)
itf.define_mesh("mesh.e", "element_stats.csv", degrees=False, active=False)
dimensions = itf.get_dimensions()

# Define crystal plasticity parameters
param_names  = [f"cp_lh_{i}" for i in range(6)] + ["cp_tau_0", "cp_n", "cp_gamma_0"]
param_values = [0.020429, 4.4225e-07, 772.66, 490.21, 176.81, 777.1, 81.697, 3.2664, 3.25e-05]
cp_params = dict(zip(param_names, param_values))

# Defines the material parameters
itf.define_material(
    material_path   = "deer/cplh6_ae",
    material_params = cp_params,
    c_11            = 250000,
    c_12            = 151000,
    c_44            = 123000,
)

# Defines the simulation parameters
exp_dict = csv_to_dict(EXP_PATH)
eng_strain = math.exp(exp_dict["strain_intervals"][-1])-1
itf.define_simulation(
    simulation_path = "deer/1to1_di_cp_x",
    time_intervals  = exp_dict["time_intervals"],
    end_strain      = eng_strain*dimensions["x"],
    add_exodus      = ADD_EXODUS
)

# Runs the model and saves results
num_processors = int(sys.argv[1]) if len(sys.argv)>1 else 8
itf.export_params()
itf.simulate("~/moose/deer/deer-opt", num_processors, 1000000)

# Conduct post processing
itf.compress_csv(sf=5, exclude=["x", "y", "z"])
itf.post_process(grain_map_path=f"{MESH_PATH}/grain_map.csv", exodus_prefix=EXODUS_PREFIX if ADD_EXODUS else "")
itf.remove_files(["mesh.e", "element_stats.csv", "results", "simulation_out_cp"])
