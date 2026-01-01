
# Libraries
import os
import pandas as pd

# Initialise
xlsx_files = [file for file in os.listdir() if file.endswith(".xlsx")]
condition_list = []

# Iterate through XLSX files
for xlsx_file in xlsx_files:
    print(xlsx_file)

    # Extract data from file name
    file_list   = xlsx_file.split("_")
    file_start  = file_list[0]
    medium      = "Air" if file_start.startswith("Air") else "He"
    file_info   = file_start.replace("Air", "").replace("He", "").replace("MPa", "").split("C")
    temp        = int(file_info[0])
    stress      = int(file_info[1])

    # Read test conditions
    data    = pd.read_excel(io=xlsx_file, sheet_name="Data")
    state   = data.iloc[20,4] # E22
    form    = data.iloc[32,4] # E34
    process = data.iloc[40,4].split(" ")[0] # E42
    
    # Identify sheet with data
    xl = pd.ExcelFile(xlsx_file)
    sheet_name = [sheet for sheet in xl.sheet_names if sheet.startswith("CreepStrainvsTime")][0]
    
    # Read time/strain values
    data = pd.read_excel(io=xlsx_file, sheet_name=sheet_name)
    x_list = data.iloc[7:, 2].values.tolist() # C9..
    y_list = data.iloc[7:, 3].values.tolist() # D9..

    # Create new file name
    condition = f"{medium}{process}_{temp}_{stress}"
    test_id   = condition_list.count(condition)
    new_file  = f"{condition}_{chr(ord('a')+test_id)}"
    condition_list.append(condition)

    # Open file and write header
    new_fp = open(f"{new_file}.csv", "w+")
    new_fp.write("x,y,temp,stress,type,state,form,process,medium,title\n")
    new_fp.write(f"0,0,{temp},{stress},creep,{state},{form},{process},{medium},{new_file}\n")

    # Check and transform values
    if len(y_list) == 0:
        new_fp.close()
        continue
    if y_list[-1] > 1:
        y_list = [y/100 for y in y_list]

    # Transfer x and y
    for i in range(len(x_list)):
        new_fp.write(f"{x_list[i]},{y_list[i]},,,\n")

    # Close
    new_fp.close()