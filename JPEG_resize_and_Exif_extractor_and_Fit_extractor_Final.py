# written by Ondřej Pavlík from CEDA Maps a.s.  mailto: pavlik@ceda.cz
# This is a Python script that resizes and organizes images in a directory.
# The script starts by asking the user to input the path to the folder containing the images.
# The user has three attempts to provide a valid folder path.
# If the user fails to provide a valid folder path after three attempts, the script exits.
# The script then creates an output folder located at "C:\CEDA_MML\FOTO".
# If the folder does not already exist, the script creates it.
# The script then loops through all the image files (with ".jpg" or ".jpeg" extension)
# in the input folder and its subdirectories and resizes them to half their original size.
# The script extracts the creation time of each image file and uses it to create a subfolder
# in the output folder with the format "YYYY_MM_DD".
# The resized image is then saved in this subfolder with a filename in the format "YYYY_MM_DD_HH_MM_SS_XX.jpeg",
# where "XX" is a two-digit number that is incremented if there is another image with the same creation time.
# The EXIF data of each image is also preserved in the resized image.

# Second part of the code is extracting metadata from JPEG images
# and processing it to extract GPS coordinates and then writing those coordinates to a shapefile.
# The code uses the os module to traverse the directory and its subdirectories to get all files.
# The exifread module is used to extract the metadata from the image files.
# The metadata is then processed to extract GPS coordinates and store them in a dictionary.
# If the GPS coordinates already exist in the dictionary, the image file is marked for deletion.
# The final step is to write the extracted GPS coordinates to a shapefile using the geopandas module.

# Third part of the code is is converting FIT format files from Garmin Virb into ESRI shapefile

import time
import datetime
import sys
import os
from pyproj import CRS

# Try to import necessary libraries
try:
    import fitparse
except ImportError:
    print("fitparse library is not installed. Please install it with 'pip install fitparse'")

try:
    import pyproj
except ImportError:
    print("pyproj library is not installed. Please install it with 'pip install pyproj'")

try:
    import shapely.geometry
except ImportError:
    print("shapely library is not installed. Please install it with 'pip install shapely'")

try:
    from PIL import Image
except ImportError:
    print("Pillow library is missing. Please install it using 'pip install pillow' ")
    sys.exit()
try:
    import piexif
except ImportError:
    print("piexif library is missing. Please install it using 'pip install piexif' ")
    sys.exit()
try:
    import exifread
except ImportError:
    print("exifread library is missing. Please install it using 'pip install exifread'")
    sys.exit()
try:
    import pandas as pd
except ImportError:
    print("pandas library is missing. Please install it using 'pip install pandas'")
    sys.exit()
try:
    import geopandas as gpd
except ImportError:
    print("geopandas library is missing. Please install it using 'pip install geopandas'")
    sys.exit()


start_time = time.time()
input_folder = ""
output_folder= r"C:\CEDA_MML\FOTO"
attempts = 0
total_size = 0

while not os.path.isdir(input_folder) and attempts < 3:
    input_folder = input("""Please enter disc name where Virb camera is connected to e.g. D:\ 
    >>> """)
    attempts += 1
    if not os.path.isdir(input_folder):
        print(f"Error: '{input_folder}' is not a valid folder.")

if not os.path.isdir(input_folder):
    print("Too many attempts, exiting...")
    sys.exit()

# preventing user input path mistake
input_folder = input_folder.upper()[0]+":/"

# output_folder = os.path.join(input_folder, "CEDA_MML", "FOTO")
output_folder = os.path.join(output_folder)
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

files = []
for dirpath, dirnames, filenames in os.walk(input_folder):
    for filename in filenames:
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
            file_path = os.path.join(dirpath, filename)
            files.append(file_path)

files.sort(key=lambda x: os.path.getmtime(x))

counter = {}
for file_path in files:
    img = Image.open(file_path)
    total_size += os.path.getsize(file_path)
    exif_dict = piexif.load(img.info.get("exif", b''))
    try:
        creation_time = datetime.datetime.strptime(exif_dict["Exif"][36867].decode("utf-8"),'%Y:%m:%d %H:%M:%S')
    except (KeyError, ValueError):
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))

    creation_time_str = creation_time.strftime("%Y_%m_%d")
    date_folder = os.path.join(output_folder, creation_time_str)
    if not os.path.exists(date_folder):
        os.makedirs(date_folder)

    if creation_time_str in counter:
        counter[creation_time_str] += 1
    else:
        counter[creation_time_str] = 1
    index = str(counter[creation_time_str]).zfill(2)
    original_filename, extension = os.path.splitext(os.path.basename(file_path))
    new_filename = f"{creation_time_str}_{creation_time.strftime('%H_%M_%S')}_{index}{extension}"

    # new_filename = f"{creation_time_str}_{index}{extension}"
    new_file_path = os.path.join(date_folder, new_filename)
    width, height = img.size
    new_width = int(width * 0.5)
    new_height = int(height * 0.5)
    img = img.resize((new_width, new_height))
    exif_bytes = piexif.dump(exif_dict)
    img.save(new_file_path, "JPEG", exif=exif_bytes)




# Second part of the code extracting coordinates from Exif metadata into shapefile
# Function to get all files in a folder and its subfolders
def get_all_files(folder_entry):
    for root, dirs, files in os.walk(folder_entry):
        for filename in files:
            yield os.path.join(root, filename)



folder_entry = "C:/CEDA_MML"


# Set the output shapefile path
# output_shp = os.path.join(input_folder, 'output.shp')
output_shp = 'C:/CEDA_MML/SHAPEFILE'
if not os.path.exists(output_shp):
    os.makedirs(output_shp)

# Create an empty list to store the GPS coordinates
gps_coords = []

# Counter to keep track of how many images are deleted
counter = 0
counter1 = 0
counter2 = 0
counter3= 0
counter4= 0

# Create a dictionary to store the latitude and longitude information of the images
coordinate_dict = {}
files_for_deletion = list()
total_size = 0

# Loop through each file in the input folder and its subfolders
for file_path in get_all_files(folder_entry):
  # Check if the file is a JPEG image
  if file_path.lower().endswith(".jpeg") or file_path.lower().endswith(".jpg") :
    filename = os.path.basename(file_path)
    # Open the file and extract the metadata
    with open(file_path, 'rb') as f:
      tags = exifread.process_file(f)

      # Check if the image has GPS coordinates
      if 'GPS GPSLatitude' in tags and 'GPS GPSLatitudeRef' in tags and 'GPS GPSLongitude' in tags and 'GPS GPSLongitudeRef' in tags:
        # Extract the latitude and longitude coordinates
        lat = tags['GPS GPSLatitude'].values
        lat_ref = tags['GPS GPSLatitudeRef'].values
        lon = tags['GPS GPSLongitude'].values
        lon_ref = tags['GPS GPSLongitudeRef'].values

        # Convert the latitude and longitude to decimal degrees
        try:
         lat_deg = (lat[0].num / lat[0].den + lat[1].num / lat[1].den / 60 + lat[2].num / lat[2].den / 3600)
        except ZeroDivisionError:
          counter3 += 1

        if lat_ref == 'S':
          lat_deg = -lat_deg
        try:
          lon_deg = (lon[0].num / lon[0].den + lon[1].num / lon[1].den / 60 + lon[2].num / lon[2].den / 3600)
        except ZeroDivisionError:
          counter4 += 1

        if lon_ref == 'W':
          lon_deg = -lon_deg

          # Store the GPS coordinates as a tuple in the dictionary
        coordinate_tuple = (lat_deg, lon_deg)

          # Check if the coordinate tuple already exists in the dictionary
        if coordinate_tuple in coordinate_dict:
          # If the coordinate tuple already exists, delete the image
          file_path_new = file_path.replace('\\', '/')
          files_for_deletion.append(file_path_new)
          counter1 += 1
        else:

            # If the coordinate tuple does not exist, add it to the dictionary
          coordinate_dict[coordinate_tuple] = 1

        # Store the GPS coordinates
          gps_coords.append([lon_deg, lat_deg, filename, file_path])
      else:
        # If the image does not have GPS coordinates, delete it
        file_path_new = file_path.replace('\\', '/')
        files_for_deletion.append(file_path_new)
        counter += 1

# Create a GeoDataFrame
df = pd.DataFrame(gps_coords, columns=['Longitude', 'Latitude', 'Image', 'Path'])
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']))

gdf=gdf.set_crs('epsg:4326')

# Write the GeoDataFrame to a shapefile
gdf.to_file(output_shp, driver='ESRI Shapefile')


for removal in files_for_deletion:
    total_size += os.path.getsize(removal)
    os.remove(removal)

total_size_kb = total_size / 1024




# Third part of the code is is converting FIT format files from Garmin Virb into ESRI shapefile

# Define the folder containing the FIT files
folder_path = input_folder.upper()[0]+":/GMetrix"


# Define the folder to save the tracklogs
shapefile_folder = "C:/CEDA_MML/TRACKLOG/"
if not os.path.exists(shapefile_folder):
    os.makedirs(shapefile_folder)

# Create a dictionary to store the points for each group of FIT files
groups = {}

# Loop through all the files in the folder
for file_name in os.listdir(folder_path):
    # Check if the file is a FIT file
    if file_name.endswith(".fit"):
        # Get the first 10 characters of the file name
        group_key = file_name[:10]

        # If the group key does not exist in the dictionary, create a new list of points
        if group_key not in groups:
            groups[group_key] = []

        # Open the FIT file and parse the data
        fitfile = fitparse.FitFile(os.path.join(folder_path, file_name))
        fitfile.parse()

        # Loop through all the data messages and extract the latitude and longitude fields
        for record in fitfile.get_messages("record"):
            # Check if the latitude and longitude fields are not null
            if record.get_value("position_lat") is not None and record.get_value("position_long") is not None:
                # Get the latitude and longitude fields in semicircles
                latitude = record.get_value("position_lat")
                longitude = record.get_value("position_long")

                # Convert the latitude and longitude values from semicircles to degrees
                y = latitude * (180 / 2**31)
                x = longitude * (180 / 2**31)

                # Add the latitude and longitude values to the list of points for the group
                groups[group_key].append((x, y))

# Loop through all the groups and create a shapefile for each group
for group_key, points in groups.items():
    # Check if there are any points in the list
    if len(points) > 0:
        # Convert the list of points to a GeoDataFrame
        gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy(*zip(*points)))
        gdf.crs = CRS('EPSG:4326')

        # Get the name for the shapefile based on the group key
        shapefile_name = os.path.join(shapefile_folder, "{}.shp".format(group_key.replace("-", "_")))

        # Create the shapefile
        try:
            gdf.to_file(shapefile_name)
        except IOError:
            print("Could not save shapefile. Please make sure the folder exists and you have write permission.")

end_time = time.time()
complete_processing_time = end_time - start_time
complete_processing_time = complete_processing_time / 60

print(f'Celkem smazáno {counter} fotek bez souřadnic a {counter1} duplitních fotek o velikosti '+'{:.2f} kilobytes'.format(total_size_kb))
print(f"Celkem {counter2} záznamů, které nešlo převést na decimal degrees")
print(f"Celkem {counter3} záznamů, kde nelze latitude dělit 0")
print(f"Celkem {counter4} záznamů, kde nelze longitude dělit 0\n\n")
print('Výstupní soubory jsou umístěny zde: C:/CEDA_MML/')
print("Celkový čas: {:.2f} minut".format(complete_processing_time))