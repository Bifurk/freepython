# Code was written by Ondřej Pavlík from CEDA Maps a.s.
# mail_to: pavlik@ceda.cz

import glob
import csv
import re
import os
import geopandas as gpd
import pandas as pd
import numpy as np
import arcpy
import requests
import zipfile
import shutil
from bs4 import BeautifulSoup
import arcpy
from arcpy import env
import datetime


# Extract automaticaly URL link from web site leading to the zip file with csv files
url = "https://nahlizenidokn.cuzk.cz/StahniAdresniMistaRUIAN.aspx"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

zip_link = soup.find("a", href=lambda x: x and x.endswith(".zip"))["href"]

zip_filename=re.findall(('[0-9]+.+'),zip_link)
response = requests.get(zip_link)
open(f'{zip_filename}', "wb").write(response.content)

path=r"C:\Users\pavlik\PycharmProjects\pythonProject\*.zip"
file=glob.glob(path)



for i in file:
    zip_file = zipfile.ZipFile(i)
    zip_file.extractall("C:\\c\\APT\\RUIAN_WEB\\")
    break



path = r'C:\c\APT\RUIAN_WEB\CSV\*.csv'
files=glob.glob(path)
count=0
counterror=0
line=0
adresy={'ID':[], 'Streetname':[],'Plotnumber':[], 'Separator':[], 'HNR':[],'Admin8':[], 'Kod obvodu Prahy':[], 'Kod ulice':[], 'Nazev obvodu Prahy':[], 'Kod casti obce':[], 'Dlocality':[], 'Typ SO':[], 'PSC':[], 'POC':[], 'Plati Od':[], 'X':[], 'Y':[], 'Scheme':[],'AddressTyp':[]}

# Creating 1 csv file from 6258 csv file on web ČUZK having delimeter "," between columns
for file in files:
 
    # Open the original CSV file for reading
    with open(file, "r",encoding='cp1250') as in_file:
        # Create a new CSV file for writing
        with open('C:\\g\\convert\\original\\new.csv', "a", newline='',encoding='utf-8') as out_file:
            # Create a CSV reader and writer object
            reader = csv.reader(in_file, delimiter=';')
            writer = csv.writer(out_file, delimiter=',')



            # Loop over the rows in the original CSV file accepting just 1 header line in the final csv file
            for row in reader:
                if row[0] == 'Kód ADM' and line==0:
                    # Write the row to the new CSV file
                    writer.writerow(row)
                    line+=1
                elif row[0] != 'Kód ADM' and row[16] != "":
                    # Write the row to the new CSV file
                    writer.writerow(row)                    
                elif row[0] != 'Kód ADM' and row[16] == "":
                    counterror+=1
print(f"Total number of records without coordinates: {counterror}")

# Loop over the rows in the above created CSV file, creating fields/values needed for the final shapefile
with open('C:/g/convert/original/new.csv','r',encoding='utf-8') as handle:

    reader=csv.DictReader(handle)
    for record in reader:

        try:
            adresy['Admin8'].append(record['Název obce'])
            adresy['Y'].append(float('-'+record['Souřadnice X']))
            adresy['X'].append(float('-'+record['Souřadnice Y']))
            if record['Typ SO']=='č.ev.':
                adresy['Plotnumber'].append('č.ev. '+record['Číslo domovní'])
            else:
                adresy['Plotnumber'].append(record['Číslo domovní'])
            adresy['Kod obvodu Prahy'].append(record['Kód obvodu Prahy'])
            adresy['Nazev obvodu Prahy'].append(record['Kód obvodu Prahy'])
            adresy['Kod casti obce'].append(record['Kód části obce'])
            adresy['Dlocality'].append(record['Název části obce'])
            adresy['Kod ulice'].append(record['Kód ulice'])
            adresy['Streetname'].append(record['Název ulice'])
            adresy['Typ SO'].append(record['Typ SO'])
            adresy['PSC'].append(record['PSČ'])
            adresy['Plati Od'].append(record['Platí Od'])
            count+=1
            adresy['ID'].append(count)
            i = (record['Číslo orientační'])
            y = (record['Znak čísla orientačního'])
            yy = i + y
            adresy['HNR'].append(yy)
            if len(yy) > 0:
                adresy['Separator'].append("/")
            else:
                adresy['Separator'].append(" ")

            if len(record['Název ulice']) > 0:
                adresy['Scheme'].append("9")
            else:
                adresy['Scheme'].append("60")
            adresy['AddressTyp'].append("Building")

        except:
            print("Error in new.csv file. Check the file!!!!!")
            








# Rewritting PSČ into xxx xx format (e.g.. 181 00)
for i in adresy['PSC']:
    adresy['POC'].append(i[:3]+' '+i[3:])

# Deleting unnecessary columns from dictionary{adresy}
del adresy['PSC']
del adresy['Kod casti obce']
del adresy['Kod ulice']
del adresy['Plati Od']
del adresy['Nazev obvodu Prahy']
del adresy['Kod obvodu Prahy']
del adresy['Typ SO']



# Find the length of the longest array to avoid traceback
max_len = max([len(v) for v in adresy.values()])

# Pad the shorter arrays with NaN values
for k, v in adresy.items():
    if len(v) < max_len:
        adresy[k] = v + [np.nan for _ in range(max_len - len(v))]

# Write the GeoDataFrame into a new csv file with UTF coding excluding false positives rows
dfx = pd.DataFrame.from_dict(adresy)
filtered_df = dfx[dfx['Plotnumber'].notnull()]
filtered_df.to_csv('C:/g/convert/original/adresy.csv', encoding='utf-8', index=False)

# Read data from above created csv file into a pandas DataFrame forcing to read columns with defined datatype

df = pd.read_csv(r"C:\g\convert\original\adresy.csv",encoding='utf-8')
df['X'] = df['X'].astype(float)
df['Y'] = df['Y'].astype(float)
df['Plotnumber'] = df['Plotnumber'].astype(str)
df['Separator'] = df['Separator'].astype(str)
df['Admin8'] = df['Admin8'].astype(str)


# Convert the DataFrame to a GeoDataFrame

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.X, df.Y))

# Set the coordinate reference system (CRS) for the GeoDataFrame S-JTSK
#gdf.crs = {'init': 'epsg:4326'}
gdf=gdf.set_crs('epsg:5514')

# Write the GeoDataFrame to a shapefile
gdf.to_file("C:/g/convert/original/adresyjtsk.shp", driver='ESRI Shapefile', encoding='utf-8')


# Deleting temporary files that were created during the conversion
file_path1 = r'C:\g\convert\original\new.csv'
file_path2 = r'C:\g\convert\original\adresy.csv'
folder_path1 = r"C:\c\APT\RUIAN_WEB\CSV"
os.remove(file_path1)
os.remove(file_path2)
shutil.rmtree(folder_path1)

# Set the workspace environment
env.workspace = "C:/g/convert/original"

# Set the shapefiles
adresyjtsk = "adresyjtsk.shp"
admin7 = "C:/c/APT/2023_Import/CZE/Reference/admin7.shp"
arcpy.management.CreateFileGDB(env.workspace, "CZE_RUIAN.gdb")

# Set the path for the output geodatabase
out_gdb = "CZE_RUIAN.gdb"

# Perform the spatial join and save the output in the geodatabase
out_join = out_gdb + "/adresyjtsk_joined"
arcpy.analysis.SpatialJoin(adresyjtsk, admin7, out_join, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "INTERSECT")

# Delete the unwanted fields
fields_to_delete = ["Join_Count", "TARGET_FID"]
arcpy.management.DeleteField(out_join, fields_to_delete)

# Create a new field named 'MMName' and copy the values from the 'ON' field
arcpy.management.AddField(out_join, 'MajorMetropolitanArea', 'TEXT')
arcpy.management.CalculateField(out_join, 'MajorMetropolitanArea', '!ON!')
arcpy.management.AddField(out_join, 'Placename', 'TEXT')
arcpy.management.CalculateField(out_join, 'Placename', '!Admin8!')

# Reorder the fields in the geodatabase feature class
reordered_fc = out_gdb + "/adresy"
field_mappings = arcpy.FieldMappings()
desired_order = ['ID', 'Streetname', 'Plotnumber', 'Separator', 'HNR', 'Placename', 'Dlocality', 'MajorMetropolitanArea', 'POC', 'X', 'Y', 'Scheme', 'AddressTyp']

# Iterate through the fields in the desired order and add them to the field_mappings object
for field_name in desired_order:
    field_map = arcpy.FieldMap()
    field_map.addInputField(out_join, field_name)
    field_mappings.addFieldMap(field_map)

# Create a new feature class with the reordered fields
arcpy.conversion.FeatureClassToFeatureClass(out_join, out_gdb, "adresy", field_mapping=field_mappings)  # corrected the argument from 'field_mapping' to 'field_mappingS'

# Delete the original 'ON' field
arcpy.management.DeleteField(reordered_fc, 'ON')

# Delete the original 'adresyjtsk_joined' feature class
arcpy.management.Delete(out_join)

# get the current date and time
now = datetime.datetime.now()

# calculate the last day of the previous month
if now.month == 1:
    # if current month is January, go back to December of the previous year
    last_month = datetime.date(now.year - 1, 12, 1)
else:
    # otherwise, just go back one month
    last_month = datetime.date(now.year, now.month - 1, 1)
last_day_last_month = last_month.replace(day=28) + datetime.timedelta(days=4)
last_day_last_month = last_day_last_month.replace(day=1) - datetime.timedelta(days=1)

# format the date as YYYYMMDD
export_datum = last_day_last_month.strftime('%Y%m%d')

# arcpy reproject feature class adresy from geodatabase into crs 4326 using S_JTSK_To_WGS_1984_1 transformation
out_coor_system = arcpy.SpatialReference(4326)
arcpy.Project_management("CZE_RUIAN.gdb/adresy", f"CZE_RUIAN.gdb/adresy_{export_datum}", out_coor_system, transform_method="S_JTSK_To_WGS_1984_1")


# delete feature class adresy
arcpy.Delete_management("CZE_RUIAN.gdb/adresy")
arcpy.DeleteField_management(f"CZE_RUIAN.gdb/adresy_{export_datum}", "X")
arcpy.DeleteField_management(f"CZE_RUIAN.gdb/adresy_{export_datum}", "Y")
arcpy.AddField_management(f"CZE_RUIAN.gdb/adresy_{export_datum}", "Longitude", "DOUBLE")
arcpy.AddField_management(f"CZE_RUIAN.gdb/adresy_{export_datum}", "Latitude", "DOUBLE")
arcpy.CalculateField_management(f"CZE_RUIAN.gdb/adresy_{export_datum}", "Longitude", "!SHAPE.CENTROID.X!", "PYTHON_9.3")
arcpy.CalculateField_management(f"CZE_RUIAN.gdb/adresy_{export_datum}", "Latitude", "!SHAPE.CENTROID.Y!", "PYTHON_9.3")

remove_file = "C:/g/convert/original/adresyjtsk.shp"
os.remove(remove_file)

# This part of the code updates the 'Streetname' field in a feature class in an ArcGIS geodatabase with values from a reference CSV file,
# using an update cursor and a dictionary to match and update the values.



# set workspace and input feature class
arcpy.env.workspace = r'C:\g\convert\original\CZE_RUIAN.gdb'
feature_class = f'adresy_{export_datum}'

# read reference csv file into a dictionary
csv_path = r'C:\c\APT\2023_Import\CZE\Prevodnik\cze_streetname_list_UTF_8.csv'
ref_dict = {}
with open(csv_path, 'r', encoding='utf-8') as csv_file:
    reader = csv.reader(csv_file)
    next(reader)  # skip header
    for row in reader:
        ref_dict [row[1]] = row[3]


# update feature class with values from csv file
with arcpy.da.UpdateCursor(feature_class, ['Streetname']) as cursor:
    for row in cursor:
        if row[0] and row[0].upper() in ref_dict:
            row[0] = ref_dict[row[0].upper()]
            cursor.updateRow(row)

print(f'Celkem převedeno {count} APTs')







