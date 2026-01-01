"""
 Title:         Reader
 Description:   For reading experimental data
 Author:        Janzen Choi

"""

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

def get_curve_dict(headers:list, data:list) -> dict:
    """
    Converts CSV data into a curve dict

    Parameters:
    * `headers`: A list of strings representing the keys
    * `data`:    A list of lists containing the data
    """

    # Get indexes of data
    list_indexes = [i for i in range(len(data[2])) if data[2][i] != ""]
    info_indexes = [i for i in range(len(data[2])) if data[2][i] == ""]
    
    # Create curve
    curve = {}
    for index in list_indexes:
        value_list = [float(d[index]) for d in data if d[index] != ""]
        curve[headers[index]] = value_list
    for index in info_indexes:
        curve[headers[index]] = try_float_cast(data[0][index])

    # Return curve
    return curve

def read_exp_data(file_dir:str, file_name:str) -> dict:
    """
    Reads the experimental data

    Parameters:
    * `file_dir`:   The path to the folder containing the experimental data files
    * `file_name`:  The name of the file containing the experimental data
    """

    # Read data
    with open(f"{file_dir}/{file_name}", "r") as file:
        headers = file.readline().replace("\n","").split(",")
        data = [line.replace("\n","").split(",") for line in file.readlines()]
    
    # Create, check, and convert curve
    exp_data = get_curve_dict(headers, data)
    exp_data["file_name"] = file_name

    # Return curves
    return exp_data
