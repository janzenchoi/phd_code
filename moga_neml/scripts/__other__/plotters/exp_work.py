"""
 Title:         Plot Experimental Work
 Description:   Plotter for work done in experimental data
 Author:        Janzen Choi

"""

# Libraries
import matplotlib.pyplot as plt
import numpy as np, math
from copy import deepcopy
from scipy.interpolate import splev, splrep, splder
from scipy.integrate import simps

# Constants
MAX_POINTS = 1000

# The Interpolator Class
class Interpolator:

    # Constructor
    def __init__(self, x_list, y_list, resolution=50, smooth=False):
        x_list = get_thinned_list(x_list, resolution)
        y_list = get_thinned_list(y_list, resolution)
        smooth_amount = resolution if smooth else 0
        self.spl = splrep(x_list, y_list, s=smooth_amount)

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
        if len(value_list) > MAX_POINTS:
            value_list = get_thinned_list(value_list, MAX_POINTS)
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

# Removes data from a curve
def remove_data(curve:dict, label:str, value:float=None) -> dict:

    # If the value is none, then don't remove anything
    if value == None:
        return curve

    # Create a copy of the curve with empty lists
    new_curve = deepcopy(curve)
    for header in new_curve.keys():
        if isinstance(new_curve[header], list) and len(new_curve[header]) == len(curve[label]):
            new_curve[header] = []
            
    # Remove data after specific value
    for i in range(len(curve[label])):
        if curve[label][i] > value:
            break
        for header in new_curve.keys():
            if isinstance(new_curve[header], list) and len(curve[header]) == len(curve[label]):
                new_curve[header].append(curve[header][i])
    
    # Return new data
    return new_curve

# # Gets the critical work and average work rate from a data dictionary
# def get_work_info(curve:dict) -> tuple:
#     critical_work = simps(curve["stress"], curve["strain"], axis=-1, even="avg")
#     d_curve = differentiate_curve(curve, "time", "strain")
#     work_rate_list = [curve["stress"][i] * d_curve["strain"][i] for i in range(len(curve["stress"]))]
#     average_work_rate = np.average(work_rate_list)
#     return critical_work, average_work_rate

# Gets the critical work and average work rate from a data dictionary
def get_work_info(curve:dict) -> tuple:

    # Calculate critical work
    critical_work = simps(curve["stress"], curve["strain"], axis=-1, even="avg")
    
    # Calculate work rate
    if curve["type"] in ["fatigue"]:
        work_rate_list = [abs(curve["stress"][i]) * curve["strain_rate"] for i in range(len(curve["stress"]))]
    elif curve["type"] in ["creep", "tensile"]:
        d_curve = differentiate_curve(curve, "time", "strain")
        work_rate_list = [curve["stress"][i] * d_curve["strain"][i] for i in range(len(curve["stress"]))]

    # Calculate average work rate for tensile / creep
    average_work_rate = np.average(work_rate_list)
    return critical_work, average_work_rate

# Gets the critical work and average work rate for a list of files
def get_work_info_list(file_list:list) -> tuple:
    critical_work_list, average_work_rate_list = [], []
    for file_dict in file_list:
        curve = get_curve(file_dict["path"])
        curve = remove_data(curve, "time", file_dict["time_end"])
        critical_work, average_work_rate = get_work_info(curve)
        critical_work_list.append(critical_work)
        average_work_rate_list.append(average_work_rate)
    return critical_work_list, average_work_rate_list

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

# Initialise list of CSV files for fatigue
fatigue_file_list = [
    {"path": "../../data/fatigue/AirPlate_850_1E-3_4-1-1.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-10.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-11.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-12.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-14.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-15.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-19.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-20.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-21.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-22.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-3.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-4.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-5.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-7.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-8.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_416-9.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_43-13.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_43-18.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_43-22.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_850_1E-3_43-6.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-1_315-7.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-1_43-17.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-1_J-3.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_315-1.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_315-16.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_43-16.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_43-20.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_43-5.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_43-9.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_A-20.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_B-1.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_B-13.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_B-14.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_B-15.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_B-3.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_E-11.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_E-12.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_E-13.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_E-28.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_F-12.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_J-1.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-3_J-5.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-4_43-3.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-4_43-8.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-4_J-2.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-4_J-4.csv", "time_end": None},
    {"path": "../../data/fatigue/AirPlate_950_1E-4_J-6.csv", "time_end": None},
]

# Gets the line of best fit given two lists of data
def get_lobf(cw_list:list, awr_list:list) -> tuple:
    log_awr_list = [math.log10(awr) for awr in awr_list]
    # log_cw_list = [math.log10(cw) for cw in cw_list]
    m_value, b_value = np.polyfit(log_awr_list, cw_list, 1)
    return m_value, b_value

# Prepare calculations and plot
raw_lobf_x_list = list(np.linspace(-1.0e1, 1.0e0, 100))
lobf_x_list = [10**x for x in raw_lobf_x_list]
plt.figure(figsize=(5,5))

# Plot data for creep
creep_cw_list, creep_awr_list = get_work_info_list(creep_file_list)
creep_m, creep_b = get_lobf(creep_cw_list, creep_awr_list)
print("creep", creep_m, creep_b)
creep_lobf_y_list = [creep_m*x + creep_b for x in raw_lobf_x_list]
plt.scatter(creep_awr_list, creep_cw_list, color="green", s=8**2)
plt.plot(lobf_x_list, creep_lobf_y_list, color="green", linewidth=3, linestyle="--")

# Plot data for tensile
tensile_cw_list, tensile_awr_list = get_work_info_list(tensile_file_list)
tensile_m, tensile_b = get_lobf(tensile_cw_list, tensile_awr_list)
print("tensile", tensile_m, tensile_b)
tensile_lobf_y_list = [tensile_m*x + tensile_b for x in raw_lobf_x_list]
plt.scatter(tensile_awr_list, tensile_cw_list, color="red", s=8**2)
plt.plot(lobf_x_list, tensile_lobf_y_list, color="red", linewidth=3, linestyle="--")

# # Plot data for fatigue
# fatigue_cw_list, fatigue_awr_list = get_work_info_list(fatigue_file_list)
# fatigue_m, fatigue_b = get_lobf(fatigue_cw_list, fatigue_awr_list)
# print("fatigue", fatigue_m, fatigue_b)
# fatigue_lobf_y_list = [fatigue_m*x + fatigue_b for x in raw_lobf_x_list]
# plt.scatter(fatigue_awr_list, fatigue_cw_list, color="green", label="Fatigue Data")
# plt.plot(lobf_x_list, fatigue_lobf_y_list, color="green", label="Fatigue LOBF")

# Format and save
# plt.title("Average Work Rate vs Critical Work", fontsize=15, fontweight="bold", y=1.05)
plt.gca().set_position([0.17, 0.12, 0.75, 0.75])
plt.gca().grid(which="major", axis="both", color="SlateGray", linewidth=1, linestyle=":")
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.xscale("log")
# plt.yscale("log")
plt.xlim(1.0e-8, 1.0e0)
plt.ylim(-5.0e1, 3.0e2)

creep = plt.scatter([], [], color="green", label="Creep Data", s=8**2)
tensile = plt.scatter([], [], color="red", label="Tensile Data", s=8**2)
legend = plt.legend(handles=[creep, tensile], framealpha=1, edgecolor="black", fancybox=True, facecolor="white", fontsize=12, loc="upper right")
plt.gca().add_artist(legend)

plt.savefig("exp.png")
