import cv2
import numpy as np
# from skimage import morphology
import os

img_folder = r"E:\data\yantian\train\lab\tif_1000"
save_folder = r"E:\data\yantian\train\lab\tif_1000_"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

files = os.listdir(img_folder)
for file in files:
    if file[-4:] == ".tif":
        img_path = os.path.join(img_folder, file)
        save_path = os.path.join(save_folder, file)
        print(img_path)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        ret, img = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)
        # ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
        # img = cv2.ximgproc.thinning(img, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN)
        # print(ret)

        cv2.imwrite(save_path, img)
        # filename = os.path.splitext(file)[0]
        # out_name = os.path.join(save_folder, filename + '.tif')
        # os.rename(save_path, out_name)

        cv2.waitKey(0)

