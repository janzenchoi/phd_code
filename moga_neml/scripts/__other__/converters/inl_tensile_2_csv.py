
# Libraries
import os
from math import log

def get_bfd(x_list, y_list):
    new_x_list, dy_list = [], []
    for i in range(1,len(x_list)):
        if x_list[i] > x_list[i-1]:
            new_x_list.append(x_list[i])
            dy_list.append((y_list[i]-y_list[i-1])/(x_list[i]-x_list[i-1]))
    return new_x_list, dy_list

def get_summary_data(test_name):
    summary_file = "Alloy617TensileSummaryData.csv"
    with open(summary_file, "r") as fp:
        all_lines = fp.readlines()
    header = all_lines[0].replace("\n","").split(",")
    test_name_index = header.index("Specimen_Name")
    temperature_index = header.index("Nominal_Temperature_C")
    medium_index = header.index("Test_Environment")
    test_names = [line.replace("\n","").split(",")[test_name_index] for line in all_lines]
    test_index = test_names.index(test_name)
    data = all_lines[test_index].replace("\n","").split(",")
    return data[temperature_index], data[medium_index]

def truify_stress_strain(eng_stress, eng_strain):
    true_stress = eng_stress * (1 + eng_strain)
    true_strain = log(1 + eng_strain)
    return true_stress, true_strain

# Get CSV files and iterate through them
csv_files = [file for file in os.listdir() if file.endswith(".csv")]
for csv_file in csv_files:

    # Extract test from file name
    file_list = csv_file.split("_")
    if len(file_list) == 1:
        continue
    test_name = file_list[1].replace(".csv","")
    print(csv_file)

    # Read file
    fp = open(csv_file, "r")
    all_lines = fp.readlines()
    fp.close()

    # Read header
    header = all_lines[0].replace("\n","").split(",")
    stress_index = header.index("Stress_MPa")
    strain_index = header.index("Strain")
    time_index = header.index("Elapsed_Time_Sec")

    # Read data
    stress_list, strain_list = [], []
    for line in all_lines[1:]:
        line_list = line.replace("\n","").split(",")
        stress = float(line_list[stress_index])
        strain = float(line_list[strain_index])
        stress, strain = truify_stress_strain(stress, strain)
        stress_list.append(stress)
        strain_list.append(strain)

    # Get strain rate
    time_list = [line.replace("\n","").split(",")[time_index] for line in all_lines[1:]]
    time_list = [float(time)/3600 for time in time_list]
    strain_rate = (strain_list[-1]-strain_list[0])/(time_list[-1]-time_list[0])

    # Prepare to write data
    temp, medium = get_summary_data(test_name)
    title = test_name.replace('-','')
    new_file_name = f"{medium}Base_{temp}_{title}.csv"
    
    # Write data
    new_fp = open(new_file_name, "w+")
    new_fp.write("x,y,temp,type,title,medium,strain_rate\n")
    new_fp.write(f"0,0,{temp},tensile,{title},{medium},{strain_rate}\n")

    # Write new x and y
    for i in range(len(strain_list)):
        new_fp.write(f"{strain_list[i]},{stress_list[i]},,,,,\n")
    new_fp.close()