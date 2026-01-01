import os, math
import numpy as np

# Constants
LIST_DENSITY = 100

# Computes the derivative of two lists of values
def compute_derivative(x_values, y_values, window_size=5):
    y_smoothed = np.convolve(y_values, np.ones(window_size)/window_size, mode='valid')
    derivatives = np.gradient(y_smoothed, x_values[:len(y_smoothed)], edge_order=2)
    return derivatives

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

# Initialise
min_strain_rate_list = []

# Iterate through files
dir_path = "../../data/creep/inl_1"
for file_name in os.listdir(dir_path):
    data_dict = csv_to_dict(f"{dir_path}/{file_name}")
    strain_rate = compute_derivative(data_dict["time"], data_dict["strain"])
    strain_rate = [sr for sr in strain_rate if not str(sr) == "nan" and sr > 0]
    min_strain_rate_list.append(min(strain_rate))

# Print results
print(f"Min: {min(min_strain_rate_list)}")
print(f"Max: {max(min_strain_rate_list)}")
