import os

import arcpy
from arcpy import env
env.workspace = "c:/data"
poly_folder = r'E:\Python\Road-Extraction-master_linux\data_anhui\fusion_ske\anhui'
save_folder = poly_folder + '_lineShp'

if not os.path.exists(save_folder):
    os.makedirs(save_folder)
files = os.listdir(poly_folder)

for file in files:
 if file[-4:] == ".png":
    poly_path = os.path.join(poly_folder, file)
    print poly_path
    # save_path = os.path.join(save_folder, file.split(".")[0] + ".shp")
    save_path = os.path.join(save_folder, file.replace('.tif', '.shp'))
    print save_path
    # arcpy.RasterToPolyline_conversion(poly_path, save_path, "ZERO", 20, "NO_SIMPLIFY")
    arcpy.RasterToPolyline_conversion(poly_path, save_path, "ZERO", 20, "SIMPLIFY")
