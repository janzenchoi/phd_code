"""
 Title:         617_s3
 Description:   Runs a mini CPFEM model once
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += [".."]
from moose_sim.interface import Interface
from moose_sim.helper.general import round_sf

# Define the mesh and orientations
itf = Interface(input_path="data/test/tiny")
itf.define_mesh("mesh.e", "element_stats.csv", degrees=False, active=False)
dimensions = itf.get_dimensions()

# Defines the material parameters
itf.define_material(
    material_path   = "deer/cvp_ae_lh",
    material_params = {

        # Crystal Plasticity Parameters
        "cp_tau_0":   107,
        "cp_lh_0":    2000, # latent hardening (off diagonal)
        "cp_lh_1":    4000, # self-hardening (main diagonal)
        "cp_gamma_0": round_sf(1e-4/3, 5),
        "cp_n":       4.5,

        # Viscoplastic Parameters
        "vp_s0":      95.121,
        "vp_R":       559.17,
        "vp_d":       1.3763,
        "vp_n":       4.2967,
        "vp_eta":     2385.9,
    },
    c_11     = 250000,
    c_12     = 151000,
    c_44     = 123000,
    youngs   = 211000.0,
    poissons = 0.30,
)

# Defines the simulation parameters
itf.define_simulation(
    simulation_path = "deer/1to1_ui",
    end_time   = 2,
    end_strain = 2,
)

# Runs the model and saves results
num_processors = int(sys.argv[1]) if len(sys.argv)>1 else 8
itf.export_params()
# itf.simulate("~/moose/moose/modules/solid_mechanics/solid_mechanics-opt", num_processors, 100000)
itf.simulate("~/moose/deer/deer-opt", num_processors, 100000)

# # Conduct post processing
# itf.compress_csv(sf=5, exclude=["x", "y", "z"])
# itf.post_process(grain_map_path="data/tiny/grain_map.csv")
# itf.remove_files(["mesh.e", "element_stats.csv", "results"])
