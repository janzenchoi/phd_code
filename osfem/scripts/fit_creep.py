import sys; sys.path += [".."]
from osfem.general import transpose, round_sf, dict_to_csv
from osfem.data import get_creep, split_data_list
from osfem.boxplot import plot_boxplots
from osfem.modeller import Modeller
import numpy as np

# Constants
NAME  = sys.argv[1]
ITERS = 1 if len(sys.argv) < 3 else int(sys.argv[2])

# Define modeller
modeller = Modeller(NAME)

# Read data
data_list = get_creep("data")
data_list = [data.update({"stress": data["stress"]/80}) or data for data in data_list]
data_list = [data.update({"temperature": data["temperature"]/1000}) or data for data in data_list]
cal_data_list, val_data_list = split_data_list(data_list)

# Initialise storage
values_list = []
cal_are_list = []
val_are_list = []

# Repeat optimisation
for i in range(ITERS):

    # Optimise
    import time
    start_time = time.time()
    opt_params = modeller.optimise(
        data_list  = cal_data_list,
        # num_gens   = 1000,
        # population = 100,
        # offspring  = 100,
        num_gens   = 500,
        population = 500,
        offspring  = 500,
        crossover  = 0.9,
        mutation   = 0.01,
    )
    print(time.time()-start_time)

    # Scale the parameters
    scale_list = modeller.get_info("scale")
    for j, (opt_param, scale) in enumerate(zip(opt_params, scale_list)):
        opt_params[j] = round_sf(scale(opt_param), 5)

    # Get average relative errors
    cal_are = modeller.get_are(cal_data_list)
    val_are = modeller.get_are(val_data_list)

    # Display results
    print("="*60)
    print(f" Run #:    {i+1}/{ITERS}")
    print(f" Params:   {opt_params}")
    print(f" Cal. ARE: {cal_are}")
    print(f" Val. ARE: {val_are}")
    
    # Append
    values_list.append(opt_params)
    cal_are_list.append(cal_are)
    val_are_list.append(val_are)

    # Plot results
    modeller.plot_1to1(cal_data_list, val_data_list)

# Determine optimal parameters
opt_index = cal_are_list.index(min(cal_are_list))

# Print final message
print("="*60)
print(f" Best Run #:    {opt_index+1}/{ITERS}")
print(f" Best Params:   {values_list[opt_index]}")
print(f" Best Cal. ARE: {cal_are_list[opt_index]}")
print(f" Best Val. ARE: {val_are_list[opt_index]}")
print("="*60)

# Plots the boxplots
param_values_list = transpose(values_list)
plot_boxplots(
    label_list  = modeller.get_info("label"),
    values_list = param_values_list,
    limits_list = modeller.get_info("limits"),
    opt_index   = opt_index,
    output_path = modeller.get_output_path("boxplots.png")
)

# Export erros
error_dict = {}
param_names = modeller.model.get_param_names()
for i, param_name in enumerate(param_names):
    error_dict[param_name] = param_values_list[i]
error_dict["cal_are"] = cal_are_list
error_dict["val_are"] = val_are_list
dict_to_csv(error_dict, modeller.get_output_path("error.csv"))
