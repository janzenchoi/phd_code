"""
 Title:         Helper
 Description:   General helper functions
 References:    https://stackoverflow.com/questions/8391411/how-to-block-calls-to-print
 Author:        Janzen Choi

"""

# Libraries
import math, os, sys
import numpy as np

def integer_to_ordinal(n:int):
    """
    Converts an integer to an ordinal string
    """
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return str(n) + suffix

def transpose(list_of_lists:list) -> list:
    """
    Transposes a 2D list of lists
    
    Parameters:
    * `list_of_lists`: A list of lists (i.e., a 2D grid)
    
    Returns the transposed list of lists
    """
    transposed = np.array(list_of_lists).T.tolist()
    return transposed

def flatten(list_of_lists:list) -> list:
    """
    Flattens a 2D list into a 1D list
    
    Parameters:
    * `list_of_lists`: A list of lists (i.e., a 2D grid)
    
    Returns the flattened list
    """
    return [item for sublist in list_of_lists for item in sublist]

def round_sf(value:float, sf:int) -> float:
    """
    Rounds a float to a number of significant figures

    Parameters:
    * `value`: The value to be rounded; accounts for lists
    * `sf`:    The number of significant figures

    Returns the rounded number
    """
    if isinstance(value, list):
        return [round_sf(v, sf) for v in value]
    format_str = "{:." + str(sf) + "g}"
    rounded_value = float(format_str.format(value))
    return rounded_value

def get_file_path_writable(file_path:str, extension:str):
    """
    Appends a number after a path if it is not writable

    Parameters:
    * `file_path`: Path to file without the extension
    * `extension`: The extension for the file
    """
    new_file_path = f"{file_path}.{extension}"
    if not os.path.exists(new_file_path):
        return new_file_path
    index = 1
    while True:
        try:
            with open(new_file_path, 'a'):
                return new_file_path
        except IOError:
            new_file_path = f"{file_path} ({index}).{extension}"
            index += 1

def get_file_path_exists(file_path:str, extension:str):
    """
    Appends a number after a path if it exists

    Parameters:
    * `file_path`: Path to file without the extension
    * `extension`: The extension for the file
    """
    new_file_path = f"{file_path}.{extension}"
    index = 1
    while os.path.exists(new_file_path):
        new_file_path = f"{file_path} ({index}).{extension}"
        index += 1
    return new_file_path

def safe_mkdir(dir_path:str) -> None:
    """
    For safely making a directory

    Parameters:
    * `dir_path`: The path to the directory
    """
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        pass

def get_thinned_list(unthinned_list:list, density:int) -> list:
    """
    Gets a thinned list

    Parameters:
    * `unthinned_list`: The list before thinning
    * `density`:        The goal density of the thinned list

    Returns the thinned list
    """
    src_data_size = len(unthinned_list)
    step_size = src_data_size / density
    thin_indexes = [math.floor(step_size*i) for i in range(1, density - 1)]
    thin_indexes = [0] + thin_indexes + [src_data_size - 1]
    thinned_list = [unthinned_list[i] for i in thin_indexes]
    return thinned_list

def transpose(list_of_lists:list) -> list:
    """
    Transposes a 2D list of lists
    
    Parameters:
    * `list_of_lists`: A list of lists (i.e., a 2D grid)
    
    Returns the transposed list of lists
    """
    transposed = np.array(list_of_lists).T.tolist()
    return transposed

def quick_spline(x_list:list, y_list:list, x_value:float) -> float:
    """
    Conducts a quick evaluation using spline interpolation without
    conducting the whole interpolation; assumes that the x_value is
    between min(x_list) and max(x_list) and that x_list is sorted

    Parameters:
    * `x_list`:  The list of x values
    * `y_list`:  The list of y values
    * `x_value`: The x value to evaluate
    
    Returns the evaluated y value
    """
    if len(x_list) != len(y_list):
        raise ValueError("Length of lists do not match!")
    for i in range(len(x_list)-1):
        if x_list[i] <= x_value and x_value <= x_list[i+1]:
            gradient = (y_list[i+1]-y_list[i])/(x_list[i+1]-x_list[i])
            y_value = gradient*(x_value - x_list[i]) + y_list[i]
            return y_value
    return None

def csv_to_dict(csv_path:str, delimeter:str=",") -> dict:
    """
    Converts a CSV file into a dictionary
    
    Parameters:
    * `csv_path`:  The path to the CSV file
    * `delimeter`: The separating character
    
    Returns the dictionary
    """

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
            try:
                value = float(value)
            except:
                pass
            csv_dict[headers[i]].append(value)
    
    # Convert single item lists to items and things multi-item lists
    for header in headers:
        if len(csv_dict[header]) == 1:
            csv_dict[header] = csv_dict[header][0]
    
    # Return
    return csv_dict

def dict_to_csv(data_dict:dict, csv_path:str) -> None:
    """
    Converts a dictionary into a CSV file

    Parameters:
    * `data_dict`: Dictionary of data
    * `csv_path`:  Path to the CSV file
    """

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

def dict_to_stdout(data_dict:dict, padding:int=1) -> None:
    """
    Displays the contents of a dictionary

    Parameters:
    * `data_dict`: The dictionary to be displayed
    * `padding`:   Padding to apply between columns
    """

    # Extract headers and identify maximum list size
    headers = data_dict.keys()
    size_list = []
    for header in headers:
        if isinstance(data_dict[header], list):
            size_list.append(len(data_dict[header])) 
    max_size = 1 if size_list == [] else max(size_list)

    # Extract headers and turn all values into lists
    for header in headers:
        if not isinstance(data_dict[header], list):
            data_dict[header] = [data_dict[header]]
        if len(data_dict[header]) < max_size:
            padding_size = max_size - len(data_dict[header])
            data_dict[header] += padding_size*[-1]
    
    # Identify the lengths of each column
    max_lengths = []
    for header in data_dict.keys():
        length_list = [len(str(header))] + [len(str(d)) for d in data_dict[header]]
        max_length = max(length_list)
        max_lengths.append(max_length + padding)

    # Print out the headers
    header_text = ""
    for i, (max_length, header) in enumerate(zip(max_lengths, data_dict.keys())):
        spaces = " " * (max_length - len(str(header)))
        if i == 0:
            header_text += f"| {header}{spaces}|"
        else:
            header_text += f" {header}{spaces}|"
    print("-"*len(header_text))
    print(header_text)
    print("-"*len(header_text))

    # Print out the values
    max_values = max([len(data_dict[header]) for header in data_dict.keys()])
    for i in range(max_values):
        value_text = ""
        for j, (max_length, header) in enumerate(zip(max_lengths, data_dict.keys())):
            value = data_dict[header][i]
            spaces = " " * (max_length - len(str(value)))
            if j == 0:
                value_text += f"| {value}{spaces}|"
            else:
                value_text += f" {value}{spaces}|"
        print(value_text)
    print("-"*len(header_text))

class BlockPrint:
    """
    Blocks print messages
    """

    def __enter__(self) -> None:
        """
        Auxiliary function
        """
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Auxiliary function
        """
        sys.stdout.close()
        sys.stdout = self._original_stdout
