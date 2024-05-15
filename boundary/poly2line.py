# Name: FeatureToLine_Example2.py
# Description: Use FeatureToLine function to combine features from two
#                  street feature classes into a single feature class,
#                  then determine an area of impact around all streets
#                  by buffering

# import system modules
import arcpy
from arcpy import env
import os

def get_line(poly_path, line_path):
    # Set environment settings
    env.workspace = "C:/data"

    for poly in os.listdir(poly_path):
        if poly.endswith('.shp'):
            #  Set local variables
            oldStreets = poly_path + '/' + poly
            # newStreets = "D:\data\sample_farm2\sg\line"
            uptodateStreets = line_path + '/' + poly

            # Use FeatureToLine function to combine features into single feature class
            arcpy.FeatureToLine_management(oldStreets, uptodateStreets,
                                           "0.001 Meters", "ATTRIBUTES")
            print(poly)
            # Use Buffer function to determine area of impact around streets
            # roadsBuffer = "c:/output/output.gdb/buffer_output"
            # arcpy.Buffer_analysis(uptodateStreets, roadsBuffer, "50 Feet",
            #                       "FULL", "ROUND", "ALL")

poly_path = r'D:\data\sample_farm2\xy\kuang_grey_proj_poly'
line_path = r'D:\data\sample_farm2\xy\line'
get_line(poly_path, line_path)