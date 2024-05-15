import numpy as np
import cv2
import os
from skimage import morphology

# img_path = r"D:\data\score\fusion\1"
# out_path = r"D:\data\score\fusion\1\dilate"

def get_dilate(img_path, out_path):
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    files = os.listdir(img_path)
    for file in files:
        if file[-4:] == '.png':
            result_name = os.path.join(img_path, file)
            result_img = cv2.imread(result_name, 0)
            save = os.path.join(out_path, file)
            print(save)

            kernel3 = np.ones((3, 3), np.uint8)
            kernel5 = np.ones((5, 5), np.uint8)
            kernel7 = np.ones((7, 7), np.uint8)

            result_dilation = cv2.dilate(result_img, kernel3, iterations=2)
            cv2.imwrite(save, result_dilation)
            cv2.waitKey(0)

def get_erode(img_path, out_path):
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    files = os.listdir(img_path)
    for file in files:
        if file[-4:] == '.png':
            result_name = os.path.join(img_path, file)
            result_img = cv2.imread(result_name, 0)
            save = os.path.join(out_path, file)
            print(save)

            kernel2 = np.ones((2, 2), np.uint8)
            kernel3 = np.ones((3, 3), np.uint8)
            kernel5 = np.ones((5, 5), np.uint8)
            kernel7 = np.ones((7, 7), np.uint8)

            dilation = cv2.dilate(result_img, kernel3, iterations=5)
            erosion = cv2.erode(dilation, kernel3, iterations=5)
            result_mask = cv2.ximgproc.thinning(erosion, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN)

            cv2.imwrite(save, result_mask)
            cv2.waitKey(0)

def remove_small_region(in_path, out_path):
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    files = os.listdir(in_path)
    for file in files:
        if file[-4:] == '.png':
            result_name = os.path.join(in_path, file)
            result_img = cv2.imread(result_name, 0)
            save = os.path.join(out_path, file)
            result_mask = morphology.remove_small_holes(result_img, 10)
            cv2.imwrite(save, result_mask)
            cv2.waitKey(0)

# get_erode(r"D:\data\score\fusion\erode", r"D:\data\score\fusion\out")
# remove_small_region(r"D:\data\score\fusion\erode", r"D:\data\score\fusion\out")

path=r"Z:\lry\data\test_3_lab"
out=r"Z:\lry\data\test_3_dilate"

get_dilate(path, out)