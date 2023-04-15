import geopandas as gpd
import os
from osgeo import ogr
import pandas as pd
import re
import csv

def process_input_data(ON, Obec, input_list):
    output_list = []

    for sub_list in input_list:
        if len(sub_list) == 1:
            output_list.append([ON, Obec, sub_list[0]])
        else:
            # Check if the second part of the values are equal
            second_parts = [x[1:] for x in sub_list]
            if len(set(second_parts)) != 1:
                output_list.append([ON, Obec] + sub_list)
            else:
                # Check if the first characters are consecutive
                first_chars = [x[0] for x in sub_list]
                first_chars.sort()
                if ord(first_chars[-1]) - ord(first_chars[0]) != len(first_chars) - 1:
                    output_list.append([ON, Obec] + sub_list)
                else:
                    # Combine the first and last characters
                    first = sub_list[0][0]
                    last = sub_list[-1][0]
                    output_list.append([ON, Obec, f"{first}-{last}{second_parts[0]}"])

    return output_list

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
    sorted_list = sorted(input_list, key=lambda x: (x[0], int(x[1:])))
    input_lists.append(sorted_list)



    output_str = ",".join(sorted_list)

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
    writer.writerow(['ON', 'Obec', 'Index'])
    for i, (obec, on, index) in enumerate(output_lists):
        writer.writerow([on, obec, index])

# Indexing based on row character
input_list = []
with open('PfArt_index.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # Skip the header row
    for row in reader:
        ON, Obec, Index = row
        input_list.append((ON, Obec, Index.split()))

output_list = []
for ON, Obec, sub_list in input_list:
    output_list.extend(process_input_data(ON, Obec, [sub_list]))

# Write output to CSV file
with open('PfArt_index_final.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(['ON', 'Obec', 'Index'])
    for row in output_list:
        writer.writerow(row)

# *********************** replacing semicolon in Index field

with open('PfArt_index_final.csv', 'r', newline='',encoding='utf-8') as file_in, open('output.csv', 'w', newline='',encoding='utf-8') as file_out:
    reader = csv.reader(file_in, delimiter=',')
    writer = csv.writer(file_out, delimiter=',')

    # Write the header row as is
    header = next(reader)
    writer.writerow(header)

    # Process each data row
    for row in reader:
        # Replace all semicolons except the first two with spaces
        new_row = [row[0], row[1], row[2].replace(',', ' ', 2)]
        writer.writerow(new_row)

# Rename the output file to the original filename
os.replace('output.csv', 'PfArt_index_final.csv')

# ***********************

#  Process the data further to add brackets around Obec column and exclude main city name from the list

output_lists = []
with open('PfArt_index_final.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # Skip the header row
    for on, obec, index in reader:
        if obec == city:
            obec = ""  # Set the Obec to empty string if it matches the city
        else:
            obec = f"({obec})"  # Append brackets around obec name
        index = index.replace(' ', ',')
        output_lists.append((on, obec, index))

# Write the final output to a CSV file with Tab between Obec Index column
output_filename = f"PfArt_index_{city}.csv"
with open(output_filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(['ON', 'Obec', 'index'])
    for on, obec, index in output_lists:
        writer.writerow([f"{on} {obec}", index])


# Remove double quotes from the output file
with open(output_filename, 'r', encoding='utf-8') as f:
    output_text = f.read()
output_text = output_text.replace('"', '')
with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(output_text)





