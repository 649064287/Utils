import os

import os
import numpy as np
from osgeo import gdal


def read_img(filename):
    dataset = gdal.Open(filename)

    im_width = dataset.RasterXSize
    im_height = dataset.RasterYSize

    im_geotrans = dataset.GetGeoTransform()
    im_proj = dataset.GetProjection()
    im_data = dataset.ReadAsArray(0, 0, im_width, im_height)

    del dataset
    return im_proj, im_geotrans, im_width, im_height, im_data


def write_img(filename, im_proj, im_geotrans, im_data):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape

    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)

    dataset.SetGeoTransform(im_geotrans)
    dataset.SetProjection(im_proj)

    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(im_data)
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i + 1).WriteArray(im_data[i])

    del dataset


def write_img_(filename, im_proj, im_geotrans, im_data):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape

    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(filename, im_width, im_height, im_bands, gdal.GDT_Byte)

    dataset.SetGeoTransform(im_geotrans)
    dataset.SetProjection(im_proj)

    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(im_data)
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i + 1).WriteArray(im_data[i])

    del dataset


def stretch_n(bands, img_min, img_max, lower_percent=0, higher_percent=100):
    out = np.zeros_like(bands).astype(np.float32)
    # a = 0
    # b = 65535
    a = img_min
    b = img_max
    # print(a, b)
    c = np.percentile(bands[:, :], lower_percent)
    d = np.percentile(bands[:, :], higher_percent)
    # x = d-c
    # if (x==0).any():
    #     t = 0
    # else:
    t = a + (bands[:, :] - c) * (b - a) / (d - c)
    t[t < a] = a
    t[t > b] = b
    out[:, :] = t
    return out


def getTifSize(tif):
    dataSet = gdal.Open(tif)
    width = dataSet.RasterXSize
    height = dataSet.RasterYSize
    bands = dataSet.RasterCount
    geoTrans = dataSet.GetGeoTransform()
    proj = dataSet.GetProjection()
    return width, height, bands, geoTrans, proj


def partDivisionForBoundary(tif1, divisionSize, tempPath):
    width, height, bands, geoTrans, proj = getTifSize(tif1)
    partWidth = partHeight = divisionSize

    if width % partWidth > 0:
        widthNum = width // partWidth + 1
    else:
        widthNum = width // partWidth
    if height % partHeight > 0:
        heightNum = height // partHeight + 1
    else:
        heightNum = height // partHeight

    realName = os.path.split(tif1)[1].split(".")[0]

    tif1 = gdal.Open(tif1)
    im_data = tif1.ReadAsArray(0, 0, width, height)
    min_16bit = np.min(im_data)
    max_16bit = np.max(im_data)
    for i in range(heightNum):
        for j in range(widthNum):

            startX = partWidth * j
            startY = partHeight * i

            if startX + partWidth <= width and startY + partHeight <= height:
                realPartWidth = partWidth
                realPartHeight = partHeight
            elif startX + partWidth > width and startY + partHeight <= height:
                realPartWidth = width - startX
                realPartHeight = partHeight
            elif startX + partWidth <= width and startY + partHeight > height:
                realPartWidth = partWidth
                realPartHeight = height - startY
            elif startX + partWidth > width and startY + partHeight > height:
                realPartWidth = width - startX
                realPartHeight = height - startY

            outName = realName + str(i) + str(j) + ".tif"
            outPath = os.path.join(tempPath, outName)

            if not os.path.exists(outPath):

                driver = gdal.GetDriverByName("GTiff")
                outTif = driver.Create(outPath, realPartWidth, realPartHeight, bands, gdal.GDT_Byte)
                outTif.SetGeoTransform(geoTrans)
                outTif.SetProjection(proj)

                data1 = tif1.ReadAsArray(startX, startY, realPartWidth, realPartHeight)
                # type 1
                image_8bit = np.array(np.rint(255 * ((data1 - min_16bit) / (max_16bit - min_16bit))), dtype=np.uint8)
                # type 2
                # image_8bit = int8(data1*256/65536)

                if bands == 1:
                    outTif.GetRasterBand(1).WriteArray(image_8bit[0])
                elif bands == 4:
                    outTif.GetRasterBand(1).WriteArray(image_8bit[0])
                    outTif.GetRasterBand(2).WriteArray(image_8bit[1])
                    outTif.GetRasterBand(3).WriteArray(image_8bit[2])
                    outTif.GetRasterBand(4).WriteArray(image_8bit[3])
    return 1


def partStretch(tif1, divisionSize, outStratchPath, tempPath):
    width, height, bands, geoTrans, proj = getTifSize(tif1)
    # bands = 1
    partWidth = partHeight = divisionSize

    if width % partWidth > 0:
        widthNum = width // partWidth + 1
    else:
        widthNum = width // partWidth
    if height % partHeight > 0:
        heightNum = height // partHeight + 1
    else:
        heightNum = height // partHeight

    realName = os.path.split(tif1)[1].split(".")[0]

    driver = gdal.GetDriverByName("GTiff")
    outTif = driver.Create(outStratchPath, width, height, bands, gdal.GDT_Byte)
    if outTif != None:
        outTif.SetGeoTransform(geoTrans)
        outTif.SetProjection(proj)
    for i in range(heightNum):
        for j in range(widthNum):

            startX = partWidth * j
            startY = partHeight * i

            if startX + partWidth <= width and startY + partHeight <= height:
                realPartWidth = partWidth
                realPartHeight = partHeight
            elif startX + partWidth > width and startY + partHeight <= height:
                realPartWidth = width - startX
                realPartHeight = partHeight
            elif startX + partWidth <= width and startY + partHeight > height:
                realPartWidth = partWidth
                realPartHeight = height - startY
            elif startX + partWidth > width and startY + partHeight > height:
                realPartWidth = width - startX
                realPartHeight = height - startY

            partTifName = realName + str(i) + str(j) + ".tif"
            partTifPath = os.path.join(tempPath, partTifName)
            divisionImg = gdal.Open(partTifPath)
            # if bands == 1:
            #     data1 = divisionImg.GetRasterBand(1).ReadAsArray(0,0,realPartWidth,realPartHeight)
            #     outPartBand = outTif.GetRasterBand(1)
            #     outPartBand.WriteArray(data1,startX,startY)
            for k in range(bands):
                data1 = divisionImg.GetRasterBand(k + 1).ReadAsArray(0, 0, realPartWidth, realPartHeight)
                outPartBand = outTif.GetRasterBand(k + 1)
                outPartBand.WriteArray(data1, startX, startY)


if __name__ == "__main__":
    ylbit_path = r"Z:\lry\chongqing\20_test\8\images\500355\500355.tif"
    bbit_path = r"Z:\lry\chongqing\20_test\8\images\500355\500355_8.tif"
    temp = r"Z:\lry\chongqing\20_test\8\images\500355"
    partDivisionForBoundary(ylbit_path, 2000, temp)
    partStretch(ylbit_path, 2000, bbit_path, temp)
