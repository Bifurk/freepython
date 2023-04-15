import csv
import pandas as pd
import os
import re
from datetime import date


# ***************************** spojí všechny log soubory z daného dne do 1 souboru measurements

# Define the folder path and today's date
folder_path = '/storage/emulated/0/PythonScripts/'
today = date.today().strftime('%Y-%m-%d')


# Define the output file name
output_file = '/storage/emulated/0/PythonScripts/measurements.csv'

# Define the regular expression pattern to match the date string in the file name
pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})\s.*\.csv$')

# Find all CSV files in the folder that match today's date
matching_files = [file for file in os.listdir(folder_path) if re.match(pattern, file) and pattern.match(file).group(1) == today]

# If there are no matching files, print an error message and exit
if not matching_files:
    print(f"No CSV files found in folder {folder_path} with today's date ({today})")
    exit()

# Sort the list of matching files by name
matching_files.sort()

# Open the output file for writing with UTF-8 encoding
with open(output_file, 'w', newline='', encoding='utf-8') as output_csv:
    writer = csv.writer(output_csv)

    # Loop over the matching files
    for i, file_name in enumerate(matching_files):
        # Open the file for reading with UTF-8 encoding
        with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as input_csv:
            reader = csv.reader(input_csv)

            # Skip the header row for all files except the first one
            if i > 0:
                next(reader)

            # Loop over the rows in the input file and write them to the output file
            for row in reader:
                writer.writerow(row)

measurements_file = "/storage/emulated/0/PythonScripts/measurements.csv"
orli_file = "/storage/emulated/0/PythonScripts/ORLI.csv"
output_file = "/storage/emulated/0/PythonScripts/output.csv"

# ***************************** výběr záznamů z log souborů, které obsahují deviceUuid 

# replace "deviceUuid" with the actual column name for device UUID in your measurements CSV file
device_uuid_column = "deviceUuid"

# replace "deviceUuid" with the actual column name for device UUID in your ORLI CSV file
orli_device_uuid_column = "deviceUuid"
orli_idpoly_column = "idPoly"
orli_device_note_column = "deviceNote"

# create dictionaries to store the idPoly and deviceNote values for each deviceUuid
device_idpoly = {}
device_note = {}

# read in the ORLI CSV file and populate the dictionaries
with open(orli_file, newline="", encoding="utf-8") as f_orli:
    reader_orli = csv.DictReader(f_orli)
    for row in reader_orli:
        device_idpoly[row[orli_device_uuid_column]] = row[orli_idpoly_column]
        device_note[row[orli_device_uuid_column]] = row[orli_device_note_column]

# read in the measurements CSV file and write out the filtered results with the idPoly and deviceNote columns added
with open(measurements_file, newline="", encoding="utf-8") as f_in, \
     open(output_file, "w", newline="", encoding="utf-8") as f_out:
    reader = csv.DictReader(f_in)
    fieldnames = reader.fieldnames + [orli_idpoly_column, orli_device_note_column]
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        if row[device_uuid_column]:
            row[orli_idpoly_column] = device_idpoly.get(row[device_uuid_column], "")
            row[orli_device_note_column] = device_note.get(row[device_uuid_column], "")
            writer.writerow(row)


# ***************************** vytvoření seznamu tunelů, kde byly zaznamenány log soubory

# Load the output.csv file into a pandas dataframe
filename = '/storage/emulated/0/PythonScripts/output.csv'
df = pd.read_csv(filename)

# Create a new dataframe with only the deviceNote column
unique_device_notes = df['deviceNote'].unique()
tunnel_list = pd.DataFrame(unique_device_notes, columns=['deviceNote'])


# Save the dataframe to a new file tunnellist.csv in the C:\k folder
output_filename = '/storage/emulated/0/PythonScripts/tunnellist.csv'
tunnel_list.to_csv(output_filename, index=False)


# *************************** výběr tunelů, které chce uživatel zahnout do analýzy

# read the tunnellist.csv file and extract the deviceNote values
with open('/storage/emulated/0/PythonScripts/tunnellist.csv', 'r') as infile:
    reader = csv.DictReader(infile)
    device_notes = set([row['deviceNote'] for row in reader])

# prompt the user to select one or more device notes
print('Please select one or more device notes:')
print('0: All')
for i, note in sorted(enumerate(device_notes, start=1), key=lambda x: (x[0], x[1])):
    print(f'{i}: {note}')
user_selection = input('Enter selection(s), separated by commas: ')

# create a set of the selected device notes
if user_selection == '0':
    selected_notes = device_notes
else:
    selected_indices = [int(x) for x in user_selection.split(',')]
    selected_notes = set([list(device_notes)[i-1] for i in selected_indices])

# read the tunnellist.csv file again and filter based on the selected device notes
with open('/storage/emulated/0/PythonScripts/tunnellist.csv', 'r') as infile, open('/storage/emulated/0/PythonScripts/tunnellist_selected.csv', 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        if row['deviceNote'] in selected_notes:
            writer.writerow(row)

# *************************** vytvoření dočasného souboru Orli, který obsahuje jen referenční záznamy z vybraných tunelů, kde byl zaznamenán log

# Load the tunnellist.csv file into a pandas dataframe
tunnel_list_filename = '/storage/emulated/0/PythonScripts/tunnellist_selected.csv'
tunnel_list_df = pd.read_csv(tunnel_list_filename)

# Get the unique deviceNote values from the tunnel_list dataframe
device_notes = tunnel_list_df['deviceNote'].unique()

# Load the ORLI.csv file into a pandas dataframe
orli_filename = '/storage/emulated/0/PythonScripts/ORLI.csv'
orli_df = pd.read_csv(orli_filename)

# Filter the ORLI dataframe to only include records with deviceNote values in the tunnel_list dataframe
filtered_orli_df = orli_df[orli_df['deviceNote'].isin(device_notes)]

# Save the filtered ORLI dataframe to a new file Orli_inter.csv in the C:\k folder
output_filename = '/storage/emulated/0/PythonScripts/Orli_inter.csv'
filtered_orli_df.to_csv(output_filename, index=False)




# ************************************** výběr záznamů z Orli, které nejsou v Log souboru




# Load the output.csv file into a pandas dataframe
filename = '/storage/emulated/0/PythonScripts/output.csv'
output_df = pd.read_csv(filename)

# Get the unique deviceUuid values from the output dataframe
device_uuids = output_df['deviceUuid'].unique()

# Load the Orli_inter.csv file into a pandas dataframe
orli_inter_filename = '/storage/emulated/0/PythonScripts/Orli_inter.csv'
orli_inter_df = pd.read_csv(orli_inter_filename)

# Filter the Orli_inter dataframe to only include records with deviceUuid values in the output dataframe
filtered_orli_inter_df = orli_inter_df[~orli_inter_df['deviceUuid'].isin(device_uuids)]

# Keep only the deviceUuid, idPoly, and deviceNote columns in the filtered dataframe
columns_to_keep = ['deviceUuid', 'idPoly', 'deviceNote']
filtered_orli_inter_df = filtered_orli_inter_df[columns_to_keep]

# Sort the records according to idPoly in ascending order
filtered_orli_inter_df = filtered_orli_inter_df.sort_values(by='idPoly', ascending=True)

# Save the filtered dataframe to a new file Beacon_noresponse.csv in the C:\k folder
output_filename = '/storage/emulated/0/PythonScripts/Beacon_noresponse.csv'
filtered_orli_inter_df.to_csv(output_filename, index=False)

# Set the cwd to 'C:\k'
os.chdir('/storage/emulated/0/PythonScripts/')
os.remove('output.csv')
os.remove('tunnellist.csv')
os.remove('tunnellist_selected.csv')
os.remove('Orli_inter.csv')
os.remove('measurements.csv')



