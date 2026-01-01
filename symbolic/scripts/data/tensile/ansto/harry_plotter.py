# Libraries
import os, math
import matplotlib.pyplot as plt

# Constants
LIST_DENSITY = 1000

# Tries to float cast a value
def try_float_cast(value:str) -> float:
    try:
        return float(value)
    except:
        return value

# Returns a thinned list
def get_thinned_list(unthinned_list:list, density:int) -> list:
    src_data_size = len(unthinned_list)
    step_size = src_data_size / density
    thin_indexes = [math.floor(step_size*i) for i in range(1, density - 1)]
    thin_indexes = [0] + thin_indexes + [src_data_size - 1]
    return [unthinned_list[i] for i in thin_indexes]

# Converts a header file into a dict of lists
def csv_to_dict(csv_path:str, delimeter:str=",") -> dict:

    # Read all data from CSV (assume that file is not too big)
    csv_fh = open(csv_path, "r")
    csv_lines = csv_fh.readlines()
    csv_fh.close()

    # Initialisation for conversion
    csv_dict = {}
    headers = csv_lines[0].replace("\n", "").split(delimeter)
    csv_lines = csv_lines[1:]
    for header in headers:
        csv_dict[header] = []

    # Start conversion to dict
    for csv_line in csv_lines:
        csv_line_list = csv_line.replace("\n", "").split(delimeter)
        for i in range(len(headers)):
            value = csv_line_list[i]
            if value == "":
                continue
            value = try_float_cast(value)
            csv_dict[headers[i]].append(value)
    
    # Convert single item lists to items and things multi-item lists
    for header in headers:
        if len(csv_dict[header]) == 1:
            csv_dict[header] = csv_dict[header][0]
        else:
            csv_dict[header] = get_thinned_list(csv_dict[header], LIST_DENSITY)
    
    # Return
    return csv_dict

colour_dict = {"1E-2": "red", "1E-3": "blue", "1E-4": "green"}

# Get CSV files and iterate through them
csv_files = [file for file in os.listdir() if file.endswith(".csv")]
for csv_file in csv_files:

    # Extract data from file name
    file_list = csv_file.split("_")
    strain_rate = file_list[1]

    # Read data
    csv_dict = csv_to_dict(csv_file)

    # Plot
    plt.plot(csv_dict["strain"], csv_dict["stress"], c=colour_dict[strain_rate], label=strain_rate)

# Save plot
plt.legend()
plt.xlabel("strain (mm/mm)")
plt.ylabel("stress (MPa)")
plt.savefig("plot")
plt.clf()