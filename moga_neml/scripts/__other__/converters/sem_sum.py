
# Libraries
import os
import pandas as pd

# Constants
NUM_PARAMS = 11
KEY_WORDS = ["800_all", "800_st", "900_all", "900_st"]

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

# Get all directories
current_directory = os.getcwd()
all_directories = [d for d in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, d))]

# Iterate through keywords
for key_word in KEY_WORDS:
    
    # Get relevant directories
    directories = [directory for directory in all_directories if key_word in directory]

    # Initialise dictionary and iterate through dictionaries
    data_dict = {}
    for i in range(len(directories)):

        # Get results file
        results_file = f"{directories[i]}/results.xlsx"
        print(f"Reading {results_file} ...")
        
        # Extract data from file
        data = pd.read_excel(io=results_file, sheet_name="results")
        param_names = list(data.columns[range(NUM_PARAMS)])
        error_name = data.columns[-1]
        params = list(data.iloc[0][range(NUM_PARAMS)])
        error = data.iloc[0][-1]

        # Initialise parameters and error
        if i == 0:
            for param_name in param_names:
                data_dict[param_name] = []
            data_dict[error_name] = []

        # Add parameters and error to dictionary
        for j in range(len(param_names)):
            data_dict[param_names[j]].append(params[j])
        data_dict[error_name].append(error)

    # Save dictionary as CSV
    dict_to_csv(data_dict, f"{current_directory}/summary_{key_word}.csv")
