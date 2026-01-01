"""
 Title:         Data
 Description:   Gets data
 Author:        Janzen Choi

"""

# Libraries
from osfem.general import csv_to_dict
from osfem.interpolator import intervaluate
from copy import deepcopy

# Define datas
CAL_ALL = False
DATA_LIST = [
    {"path": "inl_1/AirBase_800_80_G25.csv",  "fit": True,    "tts": 2174580,  "mcr": 23.3e-5/3600, "ox": None},
    {"path": "inl_1/AirBase_800_70_G44.csv",  "fit": True,    "tts": 4951332,  "mcr": 9.03e-5/3600, "ox": None},
    {"path": "inl_1/AirBase_800_65_G33.csv",  "fit": CAL_ALL, "tts": 7927344,  "mcr": 5.04e-5/3600, "ox": None},
    {"path": "inl_1/AirBase_800_60_G32.csv",  "fit": CAL_ALL, "tts": 12509442, "mcr": 2.89e-5/3600, "ox": None},
    {"path": "inl_1/AirBase_900_36_G22.csv",  "fit": True,    "tts": 2484756,  "mcr": 12.2e-5/3600, "ox": None},
    {"path": "inl_1/AirBase_900_31_G50.csv",  "fit": True,    "tts": 5122962,  "mcr": 5.37e-5/3600, "ox": None},
    {"path": "inl_1/AirBase_900_28_G45.csv",  "fit": CAL_ALL, "tts": 6807168,  "mcr": 3.53e-5/3600, "ox": None},
    {"path": "inl_1/AirBase_900_26_G59.csv",  "fit": CAL_ALL, "tts": 10289304, "mcr": 2.19e-5/3600, "ox": 20578608},
    {"path": "inl_1/AirBase_1000_16_G18.csv", "fit": True,    "tts": 3883572,  "mcr": 6.76e-5/3600, "ox": 7767144},
    {"path": "inl_1/AirBase_1000_13_G30.csv", "fit": True,    "tts": 8448138,  "mcr": 2.66e-5/3600, "ox": 16896276},
    {"path": "inl_1/AirBase_1000_12_G48.csv", "fit": CAL_ALL, "tts": 9102942,  "mcr": 0.99e-5/3600, "ox": 18205884},
    {"path": "inl_1/AirBase_1000_11_G39.csv", "fit": CAL_ALL, "tts": 9765990,  "mcr": 1.29e-5/3600, "ox": 19531980},
]

def get_creep(parent_path:str) -> list:
    """
    Creates a summary dictionary of all the creep data
    
    Parameters:
    * `parent_path`: Path to the data file

    Returns a list of dictionaries
    """

    # Initialise storage
    data_list = []

    # Read data
    for data in DATA_LIST:

        # Prepare dictionary
        summary_dict = {}

        # Get path
        data_path = f"{parent_path}/"+data["path"]
        data_dict = csv_to_dict(data_path)

        # Define test conditions
        summary_dict["stress"] = data_dict["stress"]
        summary_dict["temperature"] = data_dict["temperature"]

        # Define minimum creep rate
        summary_dict["mcr"] = data["mcr"]

        # Define time-to-failure
        if data["ox"] == None:
            ttf = max(data_dict["time"])
        else:
            ttf = data["ox"]
        summary_dict["ttf"] = ttf

        # Define strain-to-failure
        if data["ox"] == None:
            stf = max(data_dict["strain"])
        else:
            stf = intervaluate(data_dict["time"], data_dict["strain"], data["ox"])
        summary_dict["stf"] = stf

        # Define oxidation fields
        summary_dict["rttf"] = max(data_dict["time"])
        summary_dict["dttf"] = max(data_dict["time"])-summary_dict["ttf"]

        # Add fitting status
        summary_dict["fit"] = data["fit"]

        # Append
        data_list.append(summary_dict)

    # Returns the data list
    return data_list

def split_data_list(data_list:list) -> tuple:
    """
    Splits the data into calibration and validation datasets

    Parameters:
    * `data_list`: List of data dictionaries

    Returns the calibration and validation data
    as a tuple of list of dictionaries
    """
    cal_data_list, val_data_list = [], []
    for data in data_list:
        if data["fit"]:
            cal_data_list.append(data)
        else:
            val_data_list.append(data)
    return cal_data_list, val_data_list

def remove_data(data_dict:dict, x_value:float, x_label:str, after:bool=True) -> dict:
    """
    Removes data after a specific value of a curve

    Parameters:
    * `data_dict`: The data dictionary to remove the data from
    * `x_value`:   The value to start removing the data
    * `x_label`:   The label corresponding to the value
    * `after`:     Whether to remove before or after

    Returns the curve after data removal
    """

    # Define before or after
    index_list = list(range(len(data_dict[x_label])))
    if after:
        comparator = lambda a, b : a > b
    else:
        comparator = lambda a, b : a < b
        index_list.reverse()

    # Initialise new curve
    new_data_dict = deepcopy(data_dict)
    for header in new_data_dict.keys():
        if isinstance(new_data_dict[header], list) and len(data_dict[header]) == len(data_dict[x_label]):
            new_data_dict[header] = []
            
    # Remove data after specific value
    for i in index_list:
        if comparator(data_dict[x_label][i], x_value):
            break
        for header in new_data_dict.keys():
            if isinstance(new_data_dict[header], list) and len(data_dict[header]) == len(data_dict[x_label]):
                new_data_dict[header].append(data_dict[header][i])
    
    # Return new data
    return new_data_dict
