# Script converts Vertex MOMA Json files into csv file
# written by Ondřej Pavlík from CEDA Maps a.s. mailto: pavlik@ceda.cz

# import required modules
import time
import sys
import json
from os import listdir
from os.path import isfile, join
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog

# prompt the user for the input folder containing JSON files using tkinter filedialog
root = tk.Tk()
root.withdraw()
jsonFolder = filedialog.askdirectory(title='Select Input Folder')

# prompt the user for the output filename using tkinter filedialog
outputFile = filedialog.asksaveasfilename(defaultextension=".csv", title="Save Output File As", initialdir=jsonFolder)

# create an empty string to store the output
output = ""

# get a list of all JSON files in the input folder
jsonFiles = [join(jsonFolder, f) for f in listdir(jsonFolder) if isfile(join(jsonFolder, f)) and f.endswith('.json')]

# loop through each JSON file and process its features
for jsonFile in jsonFiles:
    # read the input JSON file and load it as a JSON object
    fileJson = open(jsonFile)   # open the JSON file
    jsonData = json.load(fileJson)   # load the JSON data as a Python object

    # loop through the JSON features and append specific fields to the output string
    for i in jsonData["features"]:
        x = i.get("Longitude")   # get the longitude value from the feature
        y = i.get("Latitude")   # get the latitude value from the feature
        s = i.get("SessionName")   # get the session name value from the feature
        output += s + "," + str(y) + "," + str(x) + "\n"   # append the data to the output string

    # close the input JSON file
    fileJson.close()

# write the output string to the output file
with open(outputFile, "w") as f:
    f.write(output)


print("HOTOVO")   
