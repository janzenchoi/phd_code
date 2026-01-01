"""
 Title:         Helper
 Description:   General helper functions
 Author:        Janzen Choi

"""

# Libraries
import csv, os, subprocess, sys
import math, numpy as np

def get_file_path_writable(file_path:str, extension:str) -> None:
    """
    Appends a number after a path if it exists

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

def get_file_path_exists(file_path:str, extension:str="") -> None:
    """
    Appends a number after a path if it exists

    Parameters:
    * `file_path`: Path to file without the extension
    * `extension`: The extension for the file
    """
    new_file_path = f"{file_path}.{extension}" if extension != "" else file_path
    index = 1
    while os.path.exists(new_file_path):
        new_file_path = f"{file_path} ({index}).{extension}" if extension != "" else f"{file_path} ({index})"
        index += 1
    return new_file_path

def reduce_list(value_list:list, method:str) -> float:
    """
    Reduces a list of values based on a method

    Parameters:
    * `value_list`: A list of values
    * `method`:     The method to reduce the list

    Returns the reduced list
    """
    if value_list == []:
        return 0
    if method == "sum":
        return sum(value_list)
    elif method == "average":
        return np.average(value_list)
    elif method == "square_sum":
        return sum([math.pow(value, 2) for value in value_list])
    elif method == "square_average":
        return sum([math.pow(value, 2) for value in value_list])

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

def quick_write(file_name:str, content:str) -> None:
    """
    For quickly writing to a file

    Parameters:
    * `file_name`: The name of the file
    * `content`:   The content to write to the file
    """
    with open(file_name, "w+") as file:
        file.write(content)
  
def dict_list_to_csv(dictionary_list:list) -> tuple:
    """
    Converts a list of dictionaries to a CSV format

    Parameters:
    * `dictionary_list`: The list of dictionaries

    Returns the headers and data
    """
    headers = list(dictionary_list[0].keys())
    data = [[d[1] for d in dictionary.items()] for dictionary in dictionary_list]
    return headers, data

def write_to_csv(path:str, data:list) -> None:
    """
    For writing to CSV files

    Parameters:
    * `path`: The path to the CSV file
    * `data`: The data to be written to the CSV file
    """
    with open(path, "w+") as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)

def run(command:str, shell:bool=True, check:bool=True) -> None:
    """
    Runs a command using a single thread

    Parameters:
    * `command`: The command to be run
    * `shell`:   Whether to display the output to the shell
    * `check`:   Whether to check the success of the command
    """
    subprocess.run(["OMP_NUM_THREADS=1 " + command], shell=shell, check=check)

def get_matrix_product(matrix_1:list, matrix_2:list) -> list:
    """
    Performs a 3x3 matrix multiplication

    Parameters:
    * `matrix_1`: The first matrix to be multiplied
    * `matrix_2`: The second matrix to be multiplied

    Returns the product of the two matrices
    """
    result = [[0,0,0], [0,0,0], [0,0,0]]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                result[i][j] += matrix_1[i][k] * matrix_2[k][j]
    return result

def get_inverted(matrix:list) -> list:
    """
    Inverts a matrix

    Parameters:
    * `matrix`: The matrix to be inverted

    Returns the inverted matrix
    """
    matrix = np.array(matrix)
    inverted = [list(i) for i in np.linalg.inv(matrix)]
    return inverted

def conjunct(str_list:list, conjunction:list) -> str:
    """
    Inserts a commas and a conjunction into a list of strings

    Parameters:
    * `str_list`:    The list of strings
    * `conjunction`: The conjunction to use to combine the strings

    Returns the conjuncted list of strings as a single string
    """
    if len(str_list) == 1:
        return str_list[0]
    elif len(str_list) == 2:
        return "{} {} {}".format(str_list[0], conjunction, str_list[1])
    conjuncted = ", ".join(str_list[:-1])
    conjuncted += ", {} {}".format(conjunction, str_list[-1])
    return conjuncted

def is_number(variable) -> bool:
    """
    Checks whether a variable is a number

    Parameters:
    * `variable`: The variable

    Returns whether the variable is a number or not
    """
    return isinstance(variable, float) or isinstance(variable, int)

def transpose(list_of_lists:list) -> list:
    """
    Transposes a 2D list of lists

    * `list_of_lists`: The list of lists

    Returns the transposed list of lists
    """
    transposed = np.array(list_of_lists).T.tolist()
    return transposed

class BlockPrint:
    """
    Blocks print messages;
    https://stackoverflow.com/questions/8391411/how-to-block-calls-to-print
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
