# -*- coding: utf-8 -*-
import cv2
import numpy as np
from skimage import morphology
import os
# img_path = r'F:\Mi\Project_Data\qingyuan\qingyuan_predict001_tif\qingyuan_predict_cut_tif\qingyuan_predict.tif'
# save_path = r'F:\Mi\Project_Data\qingyuan\qingyuan_predict001_tif\qingyuan_predict_cut_tif\qingyuan_predict_ske.tif'

img_folder = r'Z:\sys\data\JYZ_train\all\road\lab_1024_8'
# save_folder = r'E:\remote_img\jiuzhaigou\rcf\300_res_100_ske'
save_folder = img_folder + '_ske'
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

files = os.listdir(img_folder)
for file in files:
    if file[-4:] == ".tif":
        img_path = os.path.join(img_folder, file)
        save_path = os.path.join(save_folder, file)
        print(img_path)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        # img = cv2.imread(img_path)
        ret, img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
        print(img)
        ret, thresh = cv2.threshold(img, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # ret, temp = cv2.threshold(thresh, 100, 255, cv2.THRESH_BINARY)
        skeleton = morphology.skeletonize(thresh)

        ske = np.multiply(thresh, skeleton)

        ret, thresh = cv2.threshold(ske, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        cv2.imwrite(save_path, thresh)
        # filename = os.path.splitext(file)[0]
        # out_name = os.path.join(save_folder, filename + '.tif')
        # os.rename(save_path, out_name)

        cv2.waitKey(0)

def get_line_ske(img):
    ret, img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
    # print(img)
    ret, thresh = cv2.threshold(img, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # ret, temp = cv2.threshold(thresh, 100, 255, cv2.THRESH_BINARY)
    skeleton = morphology.skeletonize(thresh)

    # ske = np.multiply(thresh, skeleton)
    #
    # ret, thresh = cv2.threshold(ske, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    #
    # cv2.imwrite(save_path, thresh)
    # filename = os.path.splitext(file)[0]
    # out_name = os.path.join(save_folder, filename + '.tif')
    # os.rename(save_path, out_name)

    # cv2.waitKey(0)
    return img