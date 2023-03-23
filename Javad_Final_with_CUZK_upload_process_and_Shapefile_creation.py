import csv
import math
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# User input folder path
user_input_folder = input(r"Zadej složku: ")

# read data from CSV file
data = []
with open(f'{user_input_folder}\\points.txt', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile,fieldnames=['ID','Latitude','Longitude','Height','DLat','Dlong','Heightround','Comment','Empty','Fix','Value1','Value2','Value3','GNSS','Height2','TimeStamp1','TimeStamp2','Value4','Value5','Value6','Value7','Value8','Value9','Value10','Value11','Value12','Value13'])
    for row in reader:
        data.append(row)

# group records by ID
groups = {}
for row in data:
    id = row['ID'][:-1]  # remove last character from ID
    if id not in groups:
        groups[id] = []
    groups[id].append(row)

# keep only 2 records for each group that resemble each other the most
for group in groups.values():
    if len(group) > 2:
        distances = []
        for i in range(len(group)):
            for j in range(i+1, len(group)):
                lat1, lon1 = float(group[i]['Latitude']), float(group[i]['Longitude'])
                lat2, lon2 = float(group[j]['Latitude']), float(group[j]['Longitude'])
                # compute distance between (lat1, lon1) and (lat2, lon2) using Haversine formula
                dlat = (lat2 - lat1) * math.pi / 180
                dlon = (lon2 - lon1) * math.pi / 180
                a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * math.sin(dlon/2) * math.sin(dlon/2)
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = c * 6371  # multiply by Earth radius to get distance in km
                distances.append((i, j, distance))
        # sort distances in ascending order
        distances.sort(key=lambda x: x[2])
        # keep only the 2 records that resemble each other the most
        indices_to_keep = set()
        for d in distances:
            if len(indices_to_keep) == 2:
                break
            indices_to_keep.add(d[0])
            indices_to_keep.add(d[1])
        # update group with only the 2 records to keep
        group_to_keep = [group[i] for i in indices_to_keep]
        group.clear()
        group.extend(group_to_keep)

# calculate the average latitude and longitude for each group
result = []
for group in groups.values():
    id = group[0]['ID'][:-1]  # remove last character from ID
    lat_sum = sum(float(d['Latitude']) for d in group)
    lon_sum = sum(float(d['Longitude']) for d in group)
    height_sum = sum(float(d['Height']) for d in group)
    count = len(group)
    lat_avg = lat_sum / count
    lon_avg = lon_sum / count
    height_avg = height_sum / count
    row = {'ID': id, 'Latitude': lat_avg, 'Longitude': lon_avg, 'Height': height_avg}
    for key, value in group[0].items():
        if key not in row:
            row[key] = value
    result.append(row)

# write the result to a CSV file
fieldnames = result[0].keys()

with open(f'{user_input_folder}\\output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(result)

# Second part of the code is formating csv file into columns separated by space

with open(f'{user_input_folder}\\output.csv', 'r', encoding='utf-8') as infile, open(f'{user_input_folder}\\new_data.csv', 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    fieldnames = ['ID', 'Latitude', 'Longitude', 'Height']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=' ')
    writer.writeheader()
    for row in reader:
        writer.writerow({'ID': row['ID'], 'Latitude': row['Latitude'], 'Longitude': row['Longitude'], 'Height': row['Height']})

with open(f'{user_input_folder}\\output.csv', 'r', encoding='utf-8') as infile, open(f'{user_input_folder}\\CPT_ETRS89.csv', 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    fieldnames = ['ID', 'Latitude', 'Longitude', 'Height']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames,)
    writer.writeheader()
    for row in reader:
        writer.writerow({'ID': row['ID'], 'Latitude': row['Latitude'], 'Longitude': row['Longitude'], 'Height': row['Height']})

# In this first part of the code the transformation on ČÚZK website generates txt file in S-JTSK coordinate system from ETRS-89

from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
import shutil
import time



# Open the webpage in a new browser window
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://geoportal.cuzk.cz/(S(4va4ozlzdpixcfnbptmhqic5))/Default.aspx?head_tab=sekce-01-gp&mode=TextMeta&text=wcts&menu=19")

# Locate the file input element and send the file path to it
file_input = driver.find_element(By.ID, "wcts_file1")
# file_input = driver.find_element_by_id("wcts_file1")
file_input.send_keys(f'{user_input_folder}\\new_data.csv')

# Select the desired option from the source dropdown list
source_select_element = driver.find_element(By.ID, "wcts_trans2_source")
source_select_element.click()
source_option_element = driver.find_element(By.XPATH,"/html/body/div[1]/div[5]/div[2]/div[2]/div[2]/div/div[2]/select[1]/option[2]")
source_option_element.click()

# Select the desired option from the target dropdown list
target_select_element = driver.find_element(By.ID, "wcts_trans2_target")
target_select_element.click()
target_option_element = driver.find_element(By.XPATH,"/html/body/div[1]/div[5]/div[2]/div[2]/div[2]/div/div[2]/select[2]/option[6]")
target_option_element.click()

# Locate the submit button and click it
submit_button = driver.find_element(By.ID,"wcts_submit2")
submit_button.click()

time.sleep(2)

# Close the browser window
driver.quit()



# In this second part of the code the newly created TXT file in Download folder is moved to user input folder



# Download folder path (default download folder for Chrome)
download_folder = r"C:\Users\pavlik\Downloads"


# Get a list of all .txt files in the download folder
txt_files = [f for f in os.listdir(download_folder) if f.endswith('.txt')]

# Sort the list of .txt files by Date Modified (newest first)
txt_files.sort(key=lambda f: os.path.getmtime(os.path.join(download_folder, f)), reverse=True)

# Get the path of the newest .txt file
newest_txt_path = os.path.join(download_folder, txt_files[0])

# Move the newest .txt file to the user input folder
shutil.move(newest_txt_path, os.path.join(user_input_folder, txt_files[0]))

# Deleting intermediates csv file before ČÚZK transformation
os.remove(os.path.join(user_input_folder, 'new_data.csv'))



# Overall, this 3rd script part can be useful to quickly convert txt files from ČUZK transformation into shapefile


# Get folder name
folder_name = os.path.basename(os.path.normpath(user_input_folder))

# Get list of files in the folder
file_list = os.listdir(user_input_folder)

# Filter files that start with "Transformed" and end with ".txt"
txt_files = [f for f in file_list if f.startswith("Transformed") and f.endswith(".txt")]

# Loop through txt files and convert whitespaces and tabulators to comma separated values,
# strip away newline characters, strip away the last whitespace in each row, and add a header to the csv file
for txt_file in txt_files:
    # Open the txt file and read its contents
    with open(os.path.join(user_input_folder, txt_file), "r") as f:
        contents = f.readlines()

    # Remove newline characters and strip away the last whitespace in each row
    contents = [line.strip().rstrip() for line in contents]

    # Replace whitespaces and tabulators with commas
    contents = [line.replace(" ", ",") for line in contents]
    contents = [line.replace("\t", ",") for line in contents]

    # Create a new list with the fixed header and the converted contents
    new_contents = ["Id,CPT,Longitude,Latitude,Height"]
    for i, line in enumerate(contents):
        row = f"{i+1},{line}"
        new_contents.append(row)

    # Join the lines back into a single string with newline characters
    contents = "\n".join(new_contents)

    # Create a new csv file with the same name as the txt file
    csv_file = os.path.splitext(txt_file)[0] + ".csv"
    csv_path = os.path.join(user_input_folder, csv_file)

    # Write the converted contents to the csv file
    with open(csv_path, "w") as f:
        f.write(contents)

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_path)

    # Convert the DataFrame into a GeoDataFrame
    # geometry = gpd.points_from_xy(df.Longitude, df.Latitude)
    # Point Z shapefile
    geometry = [Point(x, y, z) for x, y, z in zip(df.Longitude, df.Latitude, df.Height)]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)

    # Set the CRS of the GeoDataFrame to EPSG:5514
    gdf.set_crs(epsg=5514, inplace=True)

    # Export the GeoDataFrame to a shapefile
    shp_file = f"{folder_name}.shp"
    shp_path = os.path.join(user_input_folder, shp_file)
    gdf.to_file(shp_path)