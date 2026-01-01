
# Libraries
import os, math
import pandas as pd

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
    
    # Return
    return csv_dict

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

# Initialise
xlsx_files = [file for file in os.listdir() if file.endswith(".xlsx")]
condition_list = []

# Iterate through XLSX files
for xlsx_file in xlsx_files:

    # Extract data from file name
    file_list   = xlsx_file.split("_")
    specimen    = file_list[0]
    strain_rate = file_list[1]
    
    # Read time/strain values
    data = pd.read_excel(io=xlsx_file, sheet_name="Sheet1")
    time_list = data.iloc[:, 0].values.tolist() # A1..
    strain_list = data.iloc[:, 11].values.tolist() # A1..
    stress_list = data.iloc[:, 12].values.tolist() # A1..
    
    # Removes all 0 strain values
    keep_indexes = []
    for i in range(len(strain_list)):
        if strain_list[i] != 0:
            keep_indexes.append(i)
    
    # Create CSV
    csv_dict = {}
    csv_dict["time"]        = [time_list[i] / 3600 for i in range(len(time_list)) if i in keep_indexes]
    csv_dict["strain"]      = [strain_list[i] for i in range(len(strain_list)) if i in keep_indexes]
    csv_dict["stress"]      = [stress_list[i] for i in range(len(stress_list)) if i in keep_indexes]
    csv_dict["temperature"] = 25
    csv_dict["type"]        = "tensile"
    csv_dict["medium"]      = "air"
    csv_dict["strain_rate"] = float(strain_rate) * 3600
    csv_dict["youngs"]      = 211000
    csv_dict["poissons"]    = 0.30
    
    # Reduce lists
    for header in ["time", "strain", "stress"]:
        csv_dict[header] = get_thinned_list(csv_dict[header], LIST_DENSITY)
    
    # Convert to new CSV file
    csv_path = "AirBase" + xlsx_file.split(".")[0] + ".csv"
    dict_to_csv(csv_dict, csv_path)

    # Print progress
    print(f"{xlsx_file} >> {csv_path}")
