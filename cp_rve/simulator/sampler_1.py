from modules.api import API
import itertools

# Define parameter domains
param_dict = {
    "vsh_ts": [1, 500, 1000, 1500, 2000],
    "vsh_b":  [0.1, 1, 10, 100],
    "vsh_t0": [100, 200, 300, 400, 500],
    "ai_g0":  [round(1e-4/3, 7)],
    "ai_n":   [1, 5, 10, 15, 20],
}

# Get combinations of domains
param_list = list(param_dict.values())
combinations = list(itertools.product(*param_list))
combinations = [list(c) for c in combinations]

# Iterate through the parameters
input_folder = "500/16_s1"
param_names = list(param_dict.keys())
for i in range(len(combinations)):
    
    # Prepare parameters
    param_values = combinations[i]
    param_str = "\n".join([f"{param_names[i]}: {param_values[i]}" for i in range(len(param_values))])

    # Run the simulation
    api = API(f"s1_p{i}", 0)
    api.define_mesh(f"{input_folder}/mesh.e", f"{input_folder}/input_orientations.csv")
    api.define_material("vshai", param_values)
    api.define_simulation("no_czm", [])
    api.write_text(param_str, "params.txt")
    api.simulate("~/moose/deer/deer-opt", 8)
    