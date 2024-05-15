import arcpy
import os
from arcpy import env
env.workspace = "C:/data"
poly_folder = r'Z:\sys\data\dior\images_1024\test'
save_folder = r'Z:\sys\data\dior\images_1024\shp'

if not os.path.exists(save_folder):
    os.makedirs(save_folder)
files = os.listdir(poly_folder)

for file in files:
    if file[-4:] == '.png':
        poly_path = os.path.join(poly_folder, file)
        print poly_path
        save_path = os.path.join(save_folder, file.split(".")[0] + ".shp")
        print save_path

        inRaster = poly_path
        outPolygons = save_path
        field = "VALUE"
        # arcpy.RasterToPolygon_conversion(inRaster, outPolygons, "NO_SIMPLIFY", field)
        arcpy.RasterToPolygon_conversion(inRaster, outPolygons, "SIMPLIFY", field)
