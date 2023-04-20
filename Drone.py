import os
import shutil
import tkinter as tk
from tkinter import filedialog

# Create a tkinter root window (hidden)
root = tk.Tk()
root.withdraw()

# Use the file dialog to get the folder path from the user
folder_path = filedialog.askdirectory()
files = os.listdir(folder_path)

# Create output folder
output_folder = os.path.join(folder_path, "output")
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Loop through files and create copy with new filename if the filename ends with '_Timestamp.MRK'
for file in files:
    if file.endswith("_Timestamp.MRK"):
        # Get new filename by removing '_Timestamp.MRK' and adding '.txt'
        new_filename = file.replace("_Timestamp.MRK", ".txt")
        
        # Get full paths for old and new files
        old_path = os.path.join(folder_path, file)
        new_path = os.path.join(output_folder, new_filename)
        
        # Copy file to output folder with new filename
        shutil.copy2(old_path, new_path)
        print(f"Copied '{file}' to '{new_filename}' in '{output_folder}'.")

# Get list of txt files in the output folder
txt_files = [f for f in os.listdir(output_folder) if f.endswith(".txt")]

# Create list to store rows for drone.txt
drone_rows = []

# Loop through txt files and extract columns
for txt_file in txt_files:
    with open(os.path.join(output_folder, txt_file), "r") as f:
        # Get filename without extension
        filename = os.path.splitext(txt_file)[0]
        # Reset index for new txt file
        row_num = 1
        # Loop through lines in txt file and extract other columns
        for line in f:
            split_line = line.strip().replace(",", " ").split()
            col_2 = split_line[9]
            col_3 = split_line[11]
            col_4 = split_line[13]
            col_5 = split_line[15]
            col_6 = split_line[16]
            col_7 = split_line[17]
            # Combine columns into a row for drone.txt
            first_col = f"{filename}_{row_num:04}"
            drone_row = f"{first_col}\t{col_2}\t{col_3}\t{col_4}\t{col_5}\t{col_6}\t{col_7}"
            drone_rows.append(drone_row)
            # Increment index for next row
            row_num += 1

# Write rows to drone.txt
with open(os.path.join(folder_path, "drone.txt"), "w") as f:
    for row in drone_rows:
        f.write(row + "\n")

shutil.rmtree(output_folder)

