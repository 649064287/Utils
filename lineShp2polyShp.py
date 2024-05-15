# Name: FeatureToPolygon_Example2.py
# Description: Use FeatureToPolygon function to construct habitat areas
#              from park boundaries and rivers.
# Author: ESRI

# import system modules
import os

import arcpy
from arcpy import env

# Set environment settings
env.workspace = "C:/data"
poly_folder = r'E:\Python\Road-Extraction-master_linux\data_anhui\fusion_ske\anhui_lineShp'
save_folder = poly_folder + '_polyShp'

if not os.path.exists(save_folder):
    os.makedirs(save_folder)
files = os.listdir(poly_folder)

for file in files:
    if file[-4:] == ".shp":
        poly_path = os.path.join(poly_folder, file)
        print poly_path
        save_path = os.path.join(save_folder, file)
        print save_path
        # Set local parameters
        inFeatures = poly_path
        outFeatureClass = save_path
        clusTol = "0.05 Meters"

        # Use the FeatureToPolygon function to form new areas
        arcpy.FeatureToPolygon_management(inFeatures, outFeatureClass, clusTol,
                                          "NO_ATTRIBUTES", "")

    # arcpy.FeatureToPolygon_management(["mainroads.shp","streets.shp"],
    #                                   "c:/output/output.gdb/streetblocks",
    #                                   "", "NO_ATTRIBUTES", "")
