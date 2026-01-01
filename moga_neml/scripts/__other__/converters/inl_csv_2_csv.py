
# Libraries
import os

# Get CSV files and iterate through them
csv_files = [file for file in os.listdir() if file.endswith(".csv")]
for csv_file in csv_files:

    # Extract data from file name
    file_list = csv_file.split("_")
    title = file_list[2]
    temp = int(file_list[3][:-1])
    stress = int(file_list[4][:-7])

    # Open files for reading and writing
    new_fp = open(f"{temp}_{stress}_{title}.csv", "w+")
    old_fp = open(csv_file, "r")

    # Write header
    new_fp.write("x,y,temp,stress,type,title\n")
    new_fp.write(f"0,0,{temp},{stress},creep,{title}\n")

    # Transfer x and y
    for line in old_fp.readlines()[1:]:
        line_list = line.replace("\n", "").split(",")
        if len(line_list) >= 2:
            new_fp.write(f"{line_list[0]},{line_list[1]},,,\n")

    # Close
    new_fp.close()
    old_fp.close()