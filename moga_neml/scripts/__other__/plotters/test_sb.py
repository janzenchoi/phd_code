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
DATA_PATH = "data"
CIRCLE_INTERVAL = 20

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

# Gets the critical work and average work rate from a data dictionary
def get_work_info(curve:dict) -> tuple:
    critical_work = simps(curve["stress"], curve["strain"], axis=-1, even="avg")
    d_curve = differentiate_curve(curve, "time", "strain")
    work_rate_list = [curve["stress"][i] * d_curve["strain"][i] for i in range(len(curve["stress"]))]
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
    average_work_rate_list = [math.log10(awr) for awr in average_work_rate_list]
    return critical_work_list, average_work_rate_list

def get_bounds(c_0:float, c_1:float, t_0:float, t_1:float) -> float:
    wr_0 = -c_1/c_0
    wr_1 = (t_1-c_1) / (c_0-t_0)
    wr_2 = 0
    return wr_0, wr_1, wr_2

def get_wc(wr:float, c_0:float, c_1:float, t_0:float, t_1:float) -> float:
    wr_0, wr_1, wr_2 = get_bounds(c_0, c_1, t_0, t_1)
    if wr <= wr_0 + 1:
        return c_0 * math.exp(wr - wr_0 - 1)
    elif wr_0 + 1 < wr and wr <= wr_1:
        return c_0*wr + c_1
    elif wr_1 and wr <= wr_2:
        return t_0*wr + t_1
    else:
        return 0

def get_wr_list(c_0:float, c_1:float, t_0:float, t_1:float) -> list:
    wr_0, wr_1, wr_2 = get_bounds(c_0, c_1, t_0, t_1)
    interval_size = 32
    wr_list = list(np.linspace(wr_0-5, wr_0+1, interval_size)) +\
              list(np.linspace(wr_0+1, wr_1, interval_size)) +\
              list(np.linspace(wr_1, wr_2, interval_size))
    return wr_list

# Initialise list of CSV files for creep
creep_file_list = [
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_800_60_G32.csv", "time_end": None}, #
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_800_60_G47.csv", "time_end": None},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_800_65_G33.csv", "time_end": None}, #
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_800_65_G43.csv", "time_end": None},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_800_70_G24.csv", "time_end": None},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_800_70_G44.csv", "time_end": None}, #
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_800_80_G25.csv", "time_end": None}, #
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_800_80_G34.csv", "time_end": None},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_900_26_G42.csv", "time_end": 20250000},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_900_26_G59.csv", "time_end": 21490000}, #
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_900_28_G40.csv", "time_end": 16730000},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_900_28_G45.csv", "time_end": None}, #
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_900_31_G21.csv", "time_end": None},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_900_31_G50.csv", "time_end": None}, #
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_900_36_G19.csv", "time_end": None},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_900_36_G22.csv", "time_end": None}, #
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_900_36_G63.csv", "time_end": None},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_1000_11_G39.csv", "time_end": 20610000},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_1000_12_G48.csv", "time_end": 19400000},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_1000_12_G52.csv", "time_end": 20560000},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_1000_13_G30.csv", "time_end": 18500000},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_1000_13_G51.csv", "time_end": 15100000},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_1000_16_G18.csv", "time_end": 8940000},
    {"path": f"{DATA_PATH}/creep/inl_1/AirBase_1000_16_G38.csv", "time_end": 9000000},
]

# Initialise list of CSV files for tensile
tensile_file_list = [
    {"path": f"{DATA_PATH}/tensile/inl/AirBase_20_D5.csv", "time_end": None},
    {"path": f"{DATA_PATH}/tensile/inl/AirBase_650_D8.csv", "time_end": None},
    {"path": f"{DATA_PATH}/tensile/inl/AirBase_700_D4.csv", "time_end": None},
    {"path": f"{DATA_PATH}/tensile/inl/AirBase_750_D6.csv", "time_end": None},
    {"path": f"{DATA_PATH}/tensile/inl/AirBase_800_D7.csv", "time_end": None}, #
    {"path": f"{DATA_PATH}/tensile/inl/AirBase_850_D9.csv", "time_end": None},
    {"path": f"{DATA_PATH}/tensile/inl/AirBase_900_D10.csv", "time_end": None}, #
    {"path": f"{DATA_PATH}/tensile/inl/AirBase_950_D11.csv", "time_end": None},
    {"path": f"{DATA_PATH}/tensile/inl/AirBase_1000_D12.csv", "time_end": None},
]

def get_lobf(cw_list:list, awr_list:list) -> tuple:
    m_value, b_value = np.polyfit(awr_list, cw_list, 1)
    return m_value, b_value

# Fit parameters
c_cw_list, c_awr_list = get_work_info_list(creep_file_list)
t_cw_list, t_awr_list = get_work_info_list(tensile_file_list)
c_0, c_1 = get_lobf(c_cw_list, c_awr_list)
t_0, t_1 = get_lobf(t_cw_list, t_awr_list)
params = c_0, c_1, t_0, t_1

print("Parameters:", *params)
print("X Bounds:", get_bounds(*params))
print("Y Bounds:", [get_wc(wr, *params) for wr in list(get_bounds(*params))])

plt.scatter(c_awr_list + t_awr_list, c_cw_list + t_cw_list, color="blue", label="Experimental")
wr_list = get_wr_list(*params)
wc_list = [get_wc(wr, *params) for wr in wr_list]
plt.plot(wr_list, wc_list, color="red", label="Simulation")
plt.legend()
plt.savefig("plot_sb.png")

