
# Libraries
import math, numpy as np, os
import matplotlib.pyplot as plt
import scipy.interpolate as inter
import scipy.optimize as opt

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
    
    # Add file name and return
    csv_dict["file_name"] = csv_path
    return csv_dict

# Gets the elastic modulus
def get_elastic_modulus(strain_list:list, stress_list:list, e_stress:float) -> float:
    new_strain_list, new_stress_list = [], []
    for i in range(len(strain_list)):
        if stress_list[i] < e_stress:
            new_strain_list.append(strain_list[i])
            new_stress_list.append(stress_list[i])
    print(len(new_strain_list))
    polynomial = np.polyfit(new_strain_list, new_stress_list, 1)
    return polynomial[0]

# Gets the yield point
def get_yield(strain_list:list, stress_list:list, youngs:float) -> tuple:
    sfn = inter.interp1d(strain_list, stress_list, bounds_error=False, fill_value=0)
    tfn = lambda e: youngs * (e - 0.002)
    yield_strain = opt.brentq(lambda e: sfn(e) - tfn(e), 0.0, np.max(strain_list))
    yield_stress = float(tfn(yield_strain))
    return yield_strain, yield_stress

# Read through CSV files
csv_files = [file for file in os.listdir() if file.endswith(".csv")]
csv_dict_list = [csv_to_dict(csv_file) for csv_file in csv_files]

# Plot curves
for csv_dict in csv_dict_list:
    plt.scatter(csv_dict["strain"], csv_dict["stress"], c="gray")

# Plot yield points
e_stress_dict = {1e-2: 300, 1e-3: 200, 1e-4: 100}
for csv_dict in csv_dict_list:
    # e_stress = e_stress_dict[float("{:0.1}".format(csv_dict["strain_rate"] / 3600))]
    e_stress = 100
    elastic_modulus = get_elastic_modulus(csv_dict["strain"], csv_dict["stress"], e_stress)
    print(csv_dict["file_name"], "\t", elastic_modulus)
    # yield_strain, yield_stress = get_yield(csv_dict["strain"], csv_dict["stress"], elastic_modulus)
    # plt.scatter(yield_strain, yield_stress, c="red")

plt.savefig("plot")
# csv_dict_dict = {}
# strain_rate = csv_dict["strain_rate"]
# if strain_rate in csv_dict_dict.keys():
#     csv_dict_dict[strain_rate].append(csv_dict)
# else:
#     csv_dict_dict[strain_rate] = [csv_dict]
# Create a curve for each strain rate
    