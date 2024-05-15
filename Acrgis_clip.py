# Name: Clip_Example2.py
# Description: Clip major roads that fall within the study area.

# Import system modules
import arcpy
from arcpy import env
import os

# Set workspace
env.workspace = r"Z:\lry\chongqing\sample1\shp"

in_features = "0865000451.shp"
for j in range(1,16):
    clip_features = r"Z:\lry\chongqing\sample1\image\500451\clip\500451_clip"+ str(j) +".shp"
    out_feature_class = r"Z:\lry\chongqing\sample1\image\500451\clip\output\500451_clip"+str(j)+".shp"
    xy_tolerance = ""
    # Execute Clip
    arcpy.Clip_analysis(in_features, clip_features, out_feature_class, xy_tolerance)
