from tkinter import *
from tkinter import filedialog
import geopandas as gpd
from shapely.geometry import Polygon
from pyproj import Proj, transform

# Create a Tkinter window
root = Tk()
root.title("FishNet generator over Web_Mercator input file")
# Maximize the window
root.state('zoomed')


# Function to prompt user to select input file
def browse_input_file():
    input_file_path = filedialog.askopenfilename(filetypes=[("Shapefiles", "*.shp")])
    input_file_textbox.delete(0, END)
    input_file_textbox.insert(0, input_file_path)


# Function to prompt user to select output file
def browse_output_file():
    output_file_path = filedialog.asksaveasfilename(filetypes=[("Shapefiles", "*.shp")])
    output_file_textbox.delete(0, END)
    output_file_textbox.insert(0, output_file_path)

# Create labels for the text boxes
input_file_label = Label(root, text="Input file:")
rows_label = Label(root, text="Number of rows:")
cols_label = Label(root, text="Number of columns:")
output_file_label = Label(root, text="Output file:")

# Create text boxes for the user to enter the values
input_file_textbox = Entry(root)
rows_textbox = Entry(root)
cols_textbox = Entry(root)
output_file_textbox = Entry(root)

# Add a button to browse for the input file
input_file_button = Button(root, text="Browse...", command=browse_input_file)

# Add a button to browse for the output file
output_file_button = Button(root, text="Browse...", command=browse_output_file)


# Add a button to close the window and run the script
def close_window():
    input_file = input_file_textbox.get()
    num_rows_str = rows_textbox.get()
    num_cols_str = cols_textbox.get()
    output_file = output_file_textbox.get()
    num_rows = int(num_rows_str)
    num_cols = int(num_cols_str)

    # Read input polygon and reproject to Web Mercator
    gdf_poly = gpd.read_file(input_file)
    gdf_poly = gdf_poly.to_crs("EPSG:3857")

    # Get extent of input polygon in meters
    bbox = gdf_poly.total_bounds
    inProj = Proj(gdf_poly.crs)
    outProj = Proj(init='epsg:3857')
    xmin, ymin = transform(inProj, outProj, bbox[0], bbox[1])
    xmax, ymax = transform(inProj, outProj, bbox[2], bbox[3])
    width_m = xmax - xmin
    height_m = ymax - ymin

    # Calculate origin coordinates, cell width, and cell height
    origin_x = xmin
    origin_y = ymax
    cell_width = width_m / num_cols
    cell_height = height_m / num_rows

    # Create fishnet using shapely polygons
    polygons = []
    for i in range(num_rows):
        for j in range(num_cols):
            x_min = origin_x + j * cell_width
            x_max = x_min + cell_width
            y_max = origin_y - i * cell_height
            y_min = y_max - cell_height
            polygons.append(Polygon([(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]))

    # Create GeoDataFrame with fishnet polygons
    crs = gdf_poly.crs
    gdf_fishnet = gpd.GeoDataFrame(geometry=polygons, crs=crs)

    # Add columns for row and column labels
    gdf_fishnet['radek'] = [chr(ord('A') + i) for i in range(num_rows) for _ in range(num_cols)]
    gdf_fishnet['sloupec'] = [j + 1 for i in range(num_rows) for j in range(num_cols)]

    # Add column for row and column labels combined
    gdf_fishnet['rejstrik'] = [f"{row}{col}" for row, col in zip(gdf_fishnet['radek'], gdf_fishnet['sloupec'])]


    # Write GeoDataFrame to output file
    gdf_fishnet.to_file(output_file)

    root.destroy()


button = Button(root, text="OK", command=close_window)

# Add the labels, text boxes, and buttons to the window with padding
input_file_label.grid(row=0, column=0, pady=10, padx=10)
input_file_textbox.grid(row=0, column=1, pady=10, padx=10)
input_file_button.grid(row=0, column=2, pady=10, padx=10)
rows_label.grid(row=1, column=0, pady=10, padx=10)
rows_textbox.grid(row=1, column=1, pady=10, padx=10)
cols_label.grid(row=2, column=0, pady=10, padx=10)
cols_textbox.grid(row=2, column=1, pady=10, padx=10)
output_file_label.grid(row=3, column=0, pady=10, padx=10)
output_file_textbox.grid(row=3, column=1, pady=10, padx=10)
output_file_button.grid(row=3, column=2, pady=10, padx=10)
button.grid(row=4, column=1, pady=10, padx=10)

# Run the window
root.mainloop()
