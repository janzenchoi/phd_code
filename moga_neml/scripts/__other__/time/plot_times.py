"""
 Title:         Time
 Description:   Creates a plot for evaluation times
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += ["../../../"]
from moga_neml.drivers.driver import Driver
from moga_neml.optimise.curve import Curve
from moga_neml.models.evp import Model as EVP
from moga_neml.models.evpcd import Model as EVPCD
from moga_neml.models.evpwdb import Model as EVPWD
from params import EVP_PARAMS, EVPCD_PARAMS, EVPWD_PARAMS
import numpy as np
import time

# Constants
DATA_PATH        = "../../data"
MODEL_LIST       = [EVP(""), EVPCD(""), EVPWD("")]
PARAMS_STR_LISTS = [EVP_PARAMS, EVPCD_PARAMS, EVPWD_PARAMS]

# Experimental data
EXP_PATH_LISTS = [[
    f"{DATA_PATH}/creep/inl_1/AirBase_800_60_G32.csv",        
    f"{DATA_PATH}/creep/inl_1/AirBase_800_65_G33.csv",        
    f"{DATA_PATH}/creep/inl_1/AirBase_800_70_G44.csv",        
    f"{DATA_PATH}/creep/inl_1/AirBase_800_80_G25.csv",
    f"{DATA_PATH}/tensile/inl/AirBase_800_D7.csv"
], [
    f"{DATA_PATH}/creep/inl_1/AirBase_900_26_G59.csv",        
    f"{DATA_PATH}/creep/inl_1/AirBase_900_28_G45.csv",        
    f"{DATA_PATH}/creep/inl_1/AirBase_900_31_G50.csv",        
    f"{DATA_PATH}/creep/inl_1/AirBase_900_36_G22.csv",
    f"{DATA_PATH}/tensile/inl/AirBase_900_D10.csv"
], [
    f"{DATA_PATH}/creep/inl_1/AirBase_1000_11_G39.csv",        
    f"{DATA_PATH}/creep/inl_1/AirBase_1000_12_G48.csv",        
    f"{DATA_PATH}/creep/inl_1/AirBase_1000_13_G30.csv",        
    f"{DATA_PATH}/creep/inl_1/AirBase_1000_16_G18.csv",
    f"{DATA_PATH}/tensile/inl/AirBase_1000_D12.csv"
]]

# Tries to float cast a value
def try_float_cast(value:str) -> float:
    try:
        return float(value)
    except:
        return value

# Converts CSV data into a curve dict
def get_exp_data_dict(headers:list, data:list) -> dict:
    
    # Get indexes of data
    list_indexes = [i for i in range(len(data[2])) if data[2][i] != ""]
    info_indexes = [i for i in range(len(data[2])) if data[2][i] == ""]
    
    # Create curve
    curve = {}
    for index in list_indexes:
        value_list = [float(d[index]) for d in data]
        curve[headers[index]] = value_list
    for index in info_indexes:
        curve[headers[index]] = try_float_cast(data[0][index])

    # Return curve
    return curve

# Gets the curve dict given a file path
def get_exp_data(file_path:str) -> dict:
    with open(file_path, "r") as file:
        headers = file.readline().replace("\n","").split(",")
        data = [line.replace("\n","").split(",") for line in file.readlines()]
        exp_data = get_exp_data_dict(headers, data)
        return exp_data

# Runs the model and returns the time
def run_model(model, exp_path:str, params:list):
    exp_data = get_exp_data(exp_path)
    curve = Curve(exp_data, model)
    model.set_exp_data(exp_data)
    calibrated_model = model.calibrate_model(*params)
    driver = Driver(curve, calibrated_model)
    start_time = time.time()
    driver.run()
    elapsed_time = (time.time() - start_time) * 1000
    return elapsed_time

# Iterate through and record time
for i in range(len(MODEL_LIST)):
    evaluation_times = []
    for params_str_list in PARAMS_STR_LISTS[i]:
        params_list = [list(map(float, line.split())) for line in params_str_list.strip().split("\n")]
        for params in params_list:
            for exp_path_list in EXP_PATH_LISTS:
                for exp_path in exp_path_list:
                    evaluation_time = run_model(MODEL_LIST[i], exp_path, params)
                    evaluation_times.append(evaluation_time)
                    break
    print(np.average(evaluation_times))
