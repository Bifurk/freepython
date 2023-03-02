# script was written by Ondřej Pavlík from CEDA Maps a.s. mailto: pavlik@ceda.cz
# Script was developed for batch conversion of shapefiles from WGS84 --> S-JTSK giving
# special naming format according to the creation date and time of the given Riegl trajectory

import arcpy
import os

# Get input folder path from user
input_folder = input("Please enter the path to the input folder: ")

# Set the output folder to be the same as the input folder
output_folder = input_folder

# Set the target EPSG code to 5514
#target_epsg = 5514

# Set the workspace environment to the input folder
arcpy.env.workspace = input_folder

# Get a list of all .shp files in the input folder
shp_files = arcpy.ListFeatureClasses("*.shp")

prev_creation_datetime = None
index = 0

for  shp_file in shp_files:
    # Get the creation date and time from the filename
    creation_datetime = shp_file[:7]


    # Check if the creation datetime has changed
    if prev_creation_datetime is not None and creation_datetime != prev_creation_datetime:
        # Reset the index
        index = 0

    # Set the output filename based on the first 7 characters of the original filename and the index number
    output_filename = "20" + shp_file[:7] + f"{index+1}" + ".shp"

    # Update the previous creation datetime
    prev_creation_datetime = creation_datetime

    # Increment the index
    index += 1

    # Create a spatial reference object for the target EPSG code

    out_coordinate_system = arcpy.SpatialReference(5514)

    # Project the input shapefile to the target spatial reference and save to the new output shapefile
    arcpy.management.Project(shp_file, os.path.join(output_folder, output_filename), out_coordinate_system, transform_method='S_JTSK_To_WGS_1984_1')


# Merge newly created S-JTSK shapefiles into 1 overview giving the filename of the input folder
shp_files = [f for f in arcpy.ListFeatureClasses("*.shp") if len(os.path.basename(f)[:-4]) <= 11]

# Combine shapefiles into output file with name of input folder
output_name = os.path.basename(input_folder)
output_path = os.path.join(input_folder, output_name + ".shp")
arcpy.management.Merge(shp_files, output_path,)