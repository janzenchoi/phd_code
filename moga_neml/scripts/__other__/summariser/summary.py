"""
 Title:         Plot Experimental Work
 Description:   Plotter for work done in experimental data
 Author:        Janzen Choi

"""

# Libraries
import numpy as np, math
from copy import deepcopy
from scipy.interpolate import splev, splrep, splder

# The Interpolator Class
class Interpolator:

    # Constructor
    def __init__(self, x_list, y_list, resolution=50, smooth=False):
        thin_x_list = get_thinned_list(x_list, resolution)
        thin_y_list = get_thinned_list(y_list, resolution)
        smooth_amount = resolution if smooth else 0
        self.spl = splrep(thin_x_list, thin_y_list, s=smooth_amount)
    
    # Convert to derivative
    def differentiate(self):
        self.spl = splder(self.spl)

    # Evaluate
    def evaluate(self, x_list):
        return list(splev(x_list, self.spl))

# For differentiating a curve
def differentiate_curve(curve, x_label, y_label):
    curve = deepcopy(curve)
    interpolator = Interpolator(curve[x_label], curve[y_label])
    interpolator.differentiate()
    curve[y_label] = interpolator.evaluate(curve[x_label])
    return curve

# Returns a thinned list
def get_thinned_list(unthinned_list:list, density:int) -> list:
    src_data_size = len(unthinned_list)
    step_size = src_data_size / density
    thin_indexes = [math.floor(step_size*i) for i in range(1, density - 1)]
    thin_indexes = [0] + thin_indexes + [src_data_size - 1]
    return [unthinned_list[i] for i in thin_indexes]

# Tries to float cast a value
def try_float_cast(value:str) -> float:
    try:
        return float(value)
    except:
        return value

# Converts CSV data into a curve dict
def get_curve_dict(headers:list, data:list) -> dict:
    
    # Get indexes of data
    list_indexes = [i for i in range(len(data[2])) if data[2][i] != ""]
    info_indexes = [i for i in range(len(data[2])) if data[2][i] == ""]
    
    # Create curve
    curve = {}
    for index in list_indexes:
        value_list = [float(d[index]) for d in data]
        value_list = get_thinned_list(value_list, 200)
        curve[headers[index]] = value_list
    for index in info_indexes:
        curve[headers[index]] = try_float_cast(data[0][index])

    # Make stress a list for creep curves
    if curve["type"] == "creep":
        curve["stress"] = [curve["stress"]] * len(curve["strain"])

    # Return curve
    return curve

# Gets the curve dict given a file path
def get_curve(file_path:str) -> dict:
    with open(file_path, "r") as file:
        headers = file.readline().replace("\n","").split(",")
        data = [line.replace("\n","").split(",") for line in file.readlines()]
        curve = get_curve_dict(headers, data)
        return curve

# Converts a dictionary into a CSV file
def dict_to_csv(data_dict:dict, csv_path:str) -> None:
    
    # Extract headers and turn all values into lists
    headers = data_dict.keys()
    for header in headers:
        if not isinstance(data_dict[header], list):
            data_dict[header] = [data_dict[header]]
    
    # Open CSV file and write headers
    csv_fh = open(csv_path, "w+")
    csv_fh.write(",".join(headers) + "\n")
    
    # Write data and close
    max_list_size = max([len(data_dict[header]) for header in headers])
    for i in range(max_list_size):
        row_list = [str(data_dict[header][i]) if i < len(data_dict[header]) else "" for header in headers]
        row_str = ",".join(row_list)
        csv_fh.write(row_str + "\n")
    csv_fh.close()

# Initialise list of CSV files for creep
creep_file_list = [
    {"path": "../../data/creep/inl_1/AirBase_800_60_G32.csv", "time_end": None}, #
    # {"path": "../../data/creep/inl_1/AirBase_800_60_G47.csv", "time_end": None},
    {"path": "../../data/creep/inl_1/AirBase_800_65_G33.csv", "time_end": None}, #
    # {"path": "../../data/creep/inl_1/AirBase_800_65_G43.csv", "time_end": None},
    # {"path": "../../data/creep/inl_1/AirBase_800_70_G24.csv", "time_end": None},
    {"path": "../../data/creep/inl_1/AirBase_800_70_G44.csv", "time_end": None}, #
    {"path": "../../data/creep/inl_1/AirBase_800_80_G25.csv", "time_end": None}, #
    # {"path": "../../data/creep/inl_1/AirBase_800_80_G34.csv", "time_end": None},
    # {"path": "../../data/creep/inl_1/AirBase_900_26_G42.csv", "time_end": 20250000},
    {"path": "../../data/creep/inl_1/AirBase_900_26_G59.csv", "time_end": 21490000}, #
    # {"path": "../../data/creep/inl_1/AirBase_900_28_G40.csv", "time_end": 16730000},
    {"path": "../../data/creep/inl_1/AirBase_900_28_G45.csv", "time_end": None}, #
    # {"path": "../../data/creep/inl_1/AirBase_900_31_G21.csv", "time_end": None},
    {"path": "../../data/creep/inl_1/AirBase_900_31_G50.csv", "time_end": None}, #
    # {"path": "../../data/creep/inl_1/AirBase_900_36_G19.csv", "time_end": None},
    {"path": "../../data/creep/inl_1/AirBase_900_36_G22.csv", "time_end": None}, #
    # {"path": "../../data/creep/inl_1/AirBase_900_36_G63.csv", "time_end": None},
    {"path": "../../data/creep/inl_1/AirBase_1000_11_G39.csv", "time_end": 20610000},
    {"path": "../../data/creep/inl_1/AirBase_1000_12_G48.csv", "time_end": 19400000},
    # {"path": "../../data/creep/inl_1/AirBase_1000_12_G52.csv", "time_end": 20560000},
    {"path": "../../data/creep/inl_1/AirBase_1000_13_G30.csv", "time_end": 18500000},
    # {"path": "../../data/creep/inl_1/AirBase_1000_13_G51.csv", "time_end": 15100000},
    {"path": "../../data/creep/inl_1/AirBase_1000_16_G18.csv", "time_end": 8940000},
    # {"path": "../../data/creep/inl_1/AirBase_1000_16_G38.csv", "time_end": 9000000},
]

# Initialise list of CSV files for tensile
tensile_file_list = [
    # {"path": "../../data/tensile/inl/AirBase_20_D5.csv", "time_end": None},
    # {"path": "../../data/tensile/inl/AirBase_650_D8.csv", "time_end": None},
    # {"path": "../../data/tensile/inl/AirBase_700_D4.csv", "time_end": None},
    # {"path": "../../data/tensile/inl/AirBase_750_D6.csv", "time_end": None},
    {"path": "../../data/tensile/inl/AirBase_800_D7.csv", "time_end": None}, #
    # {"path": "../../data/tensile/inl/AirBase_850_D9.csv", "time_end": None},
    {"path": "../../data/tensile/inl/AirBase_900_D10.csv", "time_end": None}, #
    # {"path": "../../data/tensile/inl/AirBase_950_D11.csv", "time_end": None},
    {"path": "../../data/tensile/inl/AirBase_1000_D12.csv", "time_end": None}, #
]

# Helper functions
sf_3 = lambda x : float("{:0.3}".format(float(x)))
sf_5 = lambda x : float("{:0.5}".format(float(x)))
get_pos_last = lambda x_list : [x for x in x_list if x > 0][-1]

# Summarise creep data
creep_dict = {}
for header in ["title", "temperature", "stress", "mcr", "strain_tf", "time_tf", "oxidation"]:
    creep_dict[header] = []
for file_dict in creep_file_list:
    curve = get_curve(file_dict["path"])
    creep_dict["title"].append(curve["title"])
    creep_dict["temperature"].append(curve["temperature"])
    creep_dict["stress"].append(curve["stress"][-1])
    cr_list = differentiate_curve(curve, "time", "strain")["strain"]
    creep_dict["mcr"].append(min([cr for cr in cr_list if cr > 0]))
    creep_dict["strain_tf"].append(sf_3(curve["strain"][-1]))
    creep_dict["time_tf"].append(sf_5(curve["time"][-1]/3600))
    if file_dict["time_end"] != None:
        creep_dict["oxidation"].append(sf_5(file_dict["time_end"]/3600))
    else:
        creep_dict["oxidation"].append("None")
dict_to_csv(creep_dict, "creep_summary.csv")

# Summarise tensile data
tensile_dict = {}
for header in ["title", "temperature", "strain_rate", "stress_tf", "strain_tf", "time_tf",]:
    tensile_dict[header] = []
for file_dict in tensile_file_list:
    curve = get_curve(file_dict["path"])
    tensile_dict["title"].append(curve["title"])
    tensile_dict["temperature"].append(curve["temperature"])
    tensile_dict["strain_rate"].append(curve["strain_rate"])
    tensile_dict["stress_tf"].append(sf_3(get_pos_last(curve["stress"])))
    tensile_dict["strain_tf"].append(sf_5(get_pos_last(curve["strain"])))
    tensile_dict["time_tf"].append(sf_5(curve["time"][-1]/3600))
dict_to_csv(tensile_dict, "tensile_summary.csv")
