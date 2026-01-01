import sys; sys.path += [".."]
import matplotlib.pyplot as plt
from osfem.data import DATA_LIST, remove_data
from osfem.general import csv_to_dict
from osfem.plotter import prep_plot, save_plot

# Normalisation function
def normalise(value_list):
    max_value = max(value_list)
    value_list = [value/max_value for value in value_list]
    return value_list

# Iterate through paths
data_dict_list = []
for data in DATA_LIST:

    # Read creep data
    data_path = f"data/"+data["path"]
    data_dict = csv_to_dict(data_path)
    
    # Truncate if data contains oxidation effects
    if data["ox"] != None:
        data_dict = remove_data(data_dict, data["ox"], "time", True)

    # Normalise strain-time data
    data_dict["time"]   = normalise(data_dict["time"])
    # data_dict["strain"] = normalise(data_dict["strain"])
    
    # Append
    data_dict_list.append(data_dict)

# Generate plot for each temperature
for temperature in [800, 900, 1000]:
    prep_plot("Time", "Strain")
    handles = []

    # Plot all curves at current temperature
    for data_dict in data_dict_list:
        if data_dict["temperature"] == temperature:
            label = f"{data_dict['stress']}MPa"
            handle = plt.scatter(data_dict["time"], data_dict["strain"], s=8**2, label=label)
            handles.append(handle)
    
    # Add legend and format
    legend = plt.legend(handles=handles, ncol=1, framealpha=1, edgecolor="black", fancybox=True, facecolor="white", fontsize=12, loc="upper left")
    plt.gca().add_artist(legend)
    save_plot(f"results/plot_{temperature}.png")
