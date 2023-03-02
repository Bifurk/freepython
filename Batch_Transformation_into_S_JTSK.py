import arcpy
import os
import datetime

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

# Loop through each .shp file found in the input folder
for index, shp_file in enumerate(shp_files):
    # Get the creation date and time from the filename
    creation_datetime_str = shp_file[7:13]
    creation_datetime = datetime.datetime.strptime(creation_datetime_str, '%H%M%S')

    # Set the output filename based on the first 7 characters of the original filename and the index number
    #output_filename = shp_file[:7] + f"{index:02}" + ".shp"
    output_filename = shp_file[:7] + f"{index+1}" + ".shp"


    # Create a spatial reference object for the target EPSG code
    #target_sr = arcpy.SpatialReference(target_epsg)
    out_coordinate_system = arcpy.SpatialReference(5514)

    # Create a new output shapefile with the target spatial reference and point geometry type
    # arcpy.management.CreateFeatureclass(output_folder, output_filename, "POINT",out_coordinate_system)

    # Project the input shapefile to the target spatial reference and save to the new output shapefile
    arcpy.management.Project(shp_file, os.path.join(output_folder, output_filename), out_coordinate_system, transform_method='S_JTSK_To_WGS_1984_1')

    print(f"Converted {shp_file} to {output_filename}")
