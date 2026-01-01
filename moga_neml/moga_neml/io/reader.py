"""
 Title:         Reader
 Description:   For reading experimental data
 Author:        Janzen Choi

"""

# Libraries
from numbers import Number
from moga_neml.helper.data import get_thinned_list, find_tensile_strain_to_failure, remove_data_after
from moga_neml.helper.experiment import DATA_FIELD_DICT, get_min_max_stress

def try_float_cast(value:str) -> float:
    """
    Tries to float cast a value

    Parameters:
    * `value`: A string to be float casted, if possible
    """
    try:
        return float(value)
    except:
        return value

def get_curve_dict(headers:list, data:list, thin_data:bool, num_points:int) -> dict:
    """
    Converts CSV data into a curve dict

    Parameters:
    * `headers`:    A list of strings representing the keys
    * `data`:       A list of lists containing the data
    * `thin_data`:  Whether to thin the data or not
    * `num_points`: How many points to thin the data to
    """

    # Get indexes of data
    list_indexes = [i for i in range(len(data[2])) if data[2][i] != ""]
    info_indexes = [i for i in range(len(data[2])) if data[2][i] == ""]
    
    # Create curve
    curve = {}
    for index in list_indexes:
        value_list = [float(d[index]) for d in data]
        if thin_data:
            value_list = get_thinned_list(value_list, num_points)
        curve[headers[index]] = value_list
    for index in info_indexes:
        curve[headers[index]] = try_float_cast(data[0][index])

    # Return curve
    return curve

def read_exp_data(file_dir:str, file_name:str, thin_data:bool, num_points:int) -> dict:
    """
    Reads the experimental data

    Parameters:
    * `file_dir`:   The path to the folder containing the experimental data files
    * `file_name`:  The name of the file containing the experimental data
    * `thin_data`:  Whether to thin the data or not
    * `num_points`: How many points to thin the data to
    """

    # Read data
    with open(f"{file_dir}/{file_name}", "r") as file:
        headers = file.readline().replace("\n","").split(",")
        data = [line.replace("\n","").split(",") for line in file.readlines()]
    
    # Create, check, and convert curve
    exp_data = get_curve_dict(headers, data, thin_data, num_points)
    exp_data["file_name"] = file_name
    check_exp_data(exp_data)

    # Add additional fields
    if exp_data["type"] == "cyclic":
        exp_data = add_cyclic_fields(exp_data)

    # Remove data of tensile curves after 80% of the UTS
    if exp_data["type"] == "tensile":
        end_index = find_tensile_strain_to_failure(exp_data["stress"])
        end_strain = exp_data["strain"][end_index]
        exp_data = remove_data_after(exp_data, end_strain, "strain")

    # Return curves
    return exp_data

def check_header(exp_data:dict, header:str, type:type) -> None:
    """
    Checks that a header exists and is of a correct type

    Parameters:
    * `exp_data`: The dictionary of experimental data
    * `header`:   A header in the experimental data dictionary
    * `type`:     The type of experimental data
    """
    if not header in exp_data.keys():
        raise ValueError(f"The data at '{exp_data['file_name']}' is missing a '{header}' header!")
    if not isinstance(exp_data[header], type):
        raise ValueError(f"The data at '{exp_data['file_name']}' does not have the correct '{header}' data type!")

def check_lists(exp_data:dict, header_list:list) -> None:
    """
    Checks that two lists in a curve are of correct formats

    Parameters:
    * `exp_data`:    The dictionary of experimental data
    * `header_list`: The list of headers in the dictionary
    """
    if header_list == []:
        return
    list_length = len(exp_data[header_list[0]])
    for header in header_list:
        if len(exp_data[header]) != list_length:
            raise ValueError(f"The '{header}' data at '{exp_data['file_name']}' has unequally sized data!")
        if len(exp_data[header]) <= 5:
            raise ValueError(f"The '{header}' data at '{exp_data['file_name']}' must have more than 5 points!")

def check_exp_data(exp_data:dict) -> None:
    """
    Checks whether the CSV files have sufficient headers and correct values;
    does not check that the 'lists' are all numbers

    Parameters:
    * `exp_data`:    The dictionary of experimental data
    """
    check_header(exp_data, "type", str)
    for data_type in ["common", exp_data["type"]]:
        data_field = DATA_FIELD_DICT[data_type]
        for list_field in data_field["lists"]:
            check_header(exp_data, list_field, list)
        check_lists(exp_data, data_field["lists"])
        for value_field in data_field["values"]:
            check_header(exp_data, value_field, Number)

def add_cyclic_fields(exp_data:dict) -> dict:
    """
    Adds fields to experimental cyclic data

    Parameters:
    * `exp_data`:    The dictionary of experimental data
    
    Returns the new experimental data dictionary
    """
    cycle_list, min_stress_list, max_stress_list = get_min_max_stress(exp_data["time"], exp_data["stress"], 10.0)
    exp_data["cycles"] = cycle_list
    exp_data["min_stress"] = min_stress_list
    exp_data["max_stress"] = max_stress_list
    return exp_data
