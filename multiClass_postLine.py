import datetime

import cv2
import os

from osgeo import gdal
import numpy as np
from skimage import morphology


def postLine(line, area_threshold):
    kernel = np.ones((3, 3), np.uint8)
    # opening = cv2.morphologyEx(line, cv2.MORPH_OPEN, kernel, iterations=2)
    # dilate = cv2.dilate(line, kernel, iterations=1)
    contours, hierarchy = cv2.findContours(line, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        area_ori = cv2.contourArea(c)
        print(area_ori)
        # Calculated area
        if area_ori < area_threshold:
            # cv2.fillPoly(line, c, 0)
            cv2.drawContours(line, [c], -1, 255, thickness=-1)
    temp = line
    ret, thresh = cv2.threshold(line, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # ret, temp = cv2.threshold(thresh, 100, 255, cv2.THRESH_BINARY)
    skeleton = morphology.skeletonize(thresh)

    ske = np.multiply(thresh, skeleton)

    ret, thresh = cv2.threshold(ske, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh, temp


if __name__ == '__main__':
    img_folder = r'E:\Python\Road-Extraction-master_linux\data_anhui\fusion_ske\anhui'
    save_folder = img_folder + "_ske_900"
    label_class = 7
    area_threshold = 200
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)
    files = os.listdir(img_folder)
    for file in files:
        if file[-4:] == ".tif":
            print(file)
            print(datetime.datetime.now())
            img_path = os.path.join(img_folder, file)
            save_path = os.path.join(save_folder, file)
            datasetname = gdal.Open(img_path, gdal.GA_ReadOnly)
            im_geotrans = datasetname.GetGeoTransform()  # 仿射矩阵
            im_proj = datasetname.GetProjection()  # 地图投影信息
            if datasetname is None:
                print('Could not open %s' % img_path)
            # img_width = datasetname.RasterXSize
            # img_height = datasetname.RasterYSize
            nBand = datasetname.RasterCount
            if nBand != 1:
                print('process first Band!')
            line = np.array(datasetname.GetRasterBand(1).ReadAsArray())
            res_img, temp = postLine(line, area_threshold)
            cv2.imwrite(save_path, res_img)
            dataset2 = gdal.Open(save_path, 1)
            dataset2.SetGeoTransform(im_geotrans)
            dataset2.SetProjection(im_proj)
            # temp_path = save_path.replace(".tif", "_temp.tif")
            # cv2.imwrite(temp_path, temp)
            # dataset1 = gdal.Open(temp_path, 1)
            # dataset1.SetGeoTransform(im_geotrans)
            # dataset1.SetProjection(im_proj)
