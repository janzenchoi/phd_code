
# Libraries
import math, os

# Constants
YOUNGS_617_DICT = {
    850: 153000,
    950: 144000,
}
POISSONS_617_DICT = {
    850: 0.3,
    950: 0.3,
}

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
            if i >= len(csv_line_list):
                continue
            value = csv_line_list[i]
            if value == "":
                continue
            value = try_float_cast(value)
            csv_dict[headers[i]].append(value)
    
    # Convert single item lists to items and things multi-item lists
    for header in headers:
        if len(csv_dict[header]) == 1:
            csv_dict[header] = csv_dict[header][0]
        elif len(csv_dict[header]) > 10000:
            csv_dict[header] = get_thinned_list(csv_dict[header], 10000)
    
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

# Get root files
def get_root_files(root_directory:str):
    root_files = []
    for root, _, files in os.walk(root_directory):
        for file in files:
            root_files.append(os.path.join(root, file))
    return root_files

# Get CSV files
csv_file_list = get_root_files("./")
csv_file_list = [csv_file for csv_file in csv_file_list if csv_file.endswith(".csv")]
csv_file_list = [csv_file for csv_file in csv_file_list if "Cycles" in csv_file]

# Iterate through CSV files
for csv_file in csv_file_list:
    print(csv_file)

    # Extract data from path name
    csv_file_info_list = csv_file.split("/")
    temperature = int(csv_file_info_list[1][:-1])
    strain_rate = float(csv_file_info_list[2].split(" ")[-1])
    
    # Extract data from CSV file
    old_csv_dict = csv_to_dict(csv_file)
    time_list = old_csv_dict['"Elapsed Time Sec"']
    strain_list = old_csv_dict['"Strain"']
    stress_list = old_csv_dict['"Stress Mpa"']
    sample_name = old_csv_dict['"Sample"'][0].replace('"', "")

    # Construct the new dictionary
    new_dict = {}
    new_dict["time"]        = time_list
    new_dict["strain"]      = strain_list
    new_dict["stress"]      = stress_list
    new_dict["temperature"] = temperature
    new_dict["type"]        = "fatigue"
    new_dict["strain_rate"] = strain_rate
    new_dict["max_strain"]  = max([abs(strain) for strain in strain_list])
    new_dict["title"]       = sample_name
    new_dict["youngs"]      = YOUNGS_617_DICT[temperature]
    new_dict["poissons"]    = POISSONS_617_DICT[temperature]

    # Define a suitable name for the new file
    strain_rate_str = f"1E-{str(strain_rate).count('0')}"
    new_csv_file_name = f"AirPlate_{temperature}_{strain_rate_str}_{sample_name}.csv"

    # Write to new CSV and rejoice
    dict_to_csv(new_dict, new_csv_file_name)
