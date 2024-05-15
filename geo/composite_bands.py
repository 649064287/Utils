import os
import arcpy

work_path = r"E:\data\yancheng\LC081190372023012002T1-SC20230914101938\merge"
if not os.path.exists(work_path):
    os.makedirs(work_path)

arcpy.env.workspace = work_path

##Compose multi types of single band raster datasets to a TIFF format raster dataset
root = r"E:\data\yancheng\LC081190372023012002T1-SC20230914101938"

# bands = ['_B01.jp2','_B02.jp2', '_B03.jp2', '_B04.jp2', '_B05.jp2','_B06.jp2', '_B07.jp2', '_B08.jp2', '_B09.jp2','_B10.jp2', '_B11.jp2', '_B12.jp2']

# bands = ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF', 'B7.TIF', 'B8.TIF', 'B9.TIF', 'B10.TIF', 'B11.TIF']
bands = ['B2.tif', 'B3.tif', 'B4.tif']

for file in os.listdir(root):
    for band in bands:
        if file.endswith(band):
            bands[bands.index(band)] = file

for i in bands:
    print i

arcpy.CompositeBands_management(root+"\\"+bands[0]+";"
                                +root+"\\"+bands[1]+";"
                                +root+"\\"+bands[2]+";",
                                bands[0][:-8]+"_3bands.tif")

# arcpy.CompositeBands_management(root+"\\"+bands[0]+";"
#                                 +root+"\\"+bands[1]+";"
#                                 +root+"\\"+bands[2]+";"
#                                 +root+"\\"+bands[3]+";"
#                                 +root+"\\"+bands[4]+";"
#                                 +root+"\\"+bands[5]+";"
#                                 +root+"\\"+bands[6]+";"
#                                 +root+"\\"+bands[7]+";"
#                                 +root+"\\"+bands[8]+";"
#                                 +root+"\\"+bands[9]+";"
#                                 +root+"\\"+bands[10]+";",
#                                 bands[0][:-8]+"_11bands.tif")

# arcpy.CompositeBands_management(root+"\\"+bands[0]+";"
#                                 +root+"\\"+bands[1]+";"
#                                 +root+"\\"+bands[2]+";"
#                                 +root+"\\"+bands[3]+";"
#                                 +root+"\\"+bands[4]+";"
#                                 +root+"\\"+bands[5]+";"
#                                 +root+"\\"+bands[6]+";"
#                                 +root+"\\"+bands[7]+";"
#                                 +root+"\\"+bands[8]+";"
#                                 +root+"\\"+bands[9]+";"
#                                 +root+"\\"+bands[10]+";"
#                                 +root+"\\"+bands[11]+";",
#                                 bands[0][:-8]+"_12bands.tif")

