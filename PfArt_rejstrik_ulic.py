import geopandas as gpd
import os
from osgeo import ogr
import pandas as pd
import re
import csv


# Set the working directory
os.chdir("C:\\i\\PfArt\\python_sit\\Test")

# Read the shapefile and CSV file
output = gpd.read_file("Test1_Export_road_ON_Identity.shp")
admin = gpd.read_file("Admin8.csv", encoding='utf-8')
city = "Brno"

# Perform the join operation
output = output.merge(admin[["OC_ADMIN8", "Obec"]], on="OC_ADMIN8", how="left")

output['Obec'] = output['Obec'].astype(str)
output['OC_ADMIN8'] = output['OC_ADMIN8'].astype(str)

# Convert geometry column to GeoSeries
output = gpd.GeoDataFrame(output, geometry=output.geometry.name, crs=output.crs)

# Write the updated shapefile to disk
output.to_file("output_updated.shp", encoding='utf-8')



# Read the shapefile
output = gpd.read_file("output_updated.shp")

# Group the records and aggregate the values
grouped = output.groupby(["ON", "Obec"])["rejstrik"].apply(lambda x: ",".join(set(x)))

# Convert the GroupBy object to a DataFrame and reset the index
df = grouped.to_frame().reset_index()

# Rename the column
df.rename(columns={"rejstrik": "index"}, inplace=True)

# Write the DataFrame to a txt file
df.to_csv("input_index.csv", sep=";", index=False)




# Open the input file
with open('input_index.csv', 'r', encoding='utf-8') as f:
    # Read the file contents into a list of lines
    lines = f.readlines()

# Parse the input lines and extract the index lists
input_lists = []
for line in lines[1:]:
    parts = line.strip().split(';')
    input_list = parts[2].split(',')
    input_list.sort(key=lambda x: (x.isdigit(), x))
    input_lists.append(input_list)

# Process each input list and generate the output
output_lists = []
for input_list in input_lists:
    output_list = []
    current_range = []

    for index, item in enumerate(input_list):
        if index == 0:
            current_range.append(item)
        else:
            prev_item = input_list[index - 1]
            if prev_item[0] == item[0] and int(prev_item[1:]) + 1 == int(item[1:]):
                current_range.append(item)
            else:
                if len(current_range) > 1:
                    output_list.append(current_range[0] + '-' + current_range[-1][1:])
                else:
                    output_list.append(current_range[0])
                current_range = [item]

    if len(current_range) > 1:
        output_list.append(current_range[0] + '-' + current_range[-1][1:])
    else:
        output_list.append(current_range[0])

    output_lists.append(output_list)

# Write the output to a CSV file
with open('output_index.csv', 'w', newline='',encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ON', 'Obec', 'index'])
    for i, line in enumerate(lines[1:]):
        parts = line.strip().split(';')
        writer.writerow([parts[0], parts[1], ' '.join(output_lists[i])])

# Creating csv file with sorted columns Obec, ON in ascending order
with open('output_index.csv', encoding='utf-8') as f:
    lines = f.readlines()

# Parse the input and sort the values
output_lists = []
for line in lines[1:]:
    parts = line.strip().split(',')
    output_lists.append((parts[1], parts[0], ';'.join(parts[2:])))
output_lists = sorted(output_lists)

# Write the final output to a CSV file
with open('PfArt_index.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ON', 'Obec', 'index'])
    for i, (obec, on, index) in enumerate(output_lists):
        writer.writerow([on, obec, index])

#  Process the data further to add brackets around Obec column and exclude main city name from the list

output_lists = []
with open('PfArt_index.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # Skip the header row
    for on, obec, index in reader:
        if obec == city:
            obec = ""  # Set the Obec to empty string if it matches the city
        else:
            obec = f"({obec})"  # Append brackets around obec name
        index = index.replace(' ', ',')
        output_lists.append((on, obec, index))

# Write the final output to a CSV file
output_filename = f"PfArt_index_{city}.csv"
with open(output_filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=' ')
    writer.writerow(['ON', 'Obec', 'index'])
    for on, obec, index in output_lists:
        writer.writerow([on, obec, index])

# Remove double quotes from the output file
with open(output_filename, 'r', encoding='utf-8') as f:
    output_text = f.read()
output_text = output_text.replace('"', '')
with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(output_text)





