from osgeo import gdal
import os
import numpy as np
import cv2

def reverse(path, out):
    img = cv2.imread(path,flags=0)
    imgInfo = img.shape
    height = imgInfo[0]
    width = imgInfo[1]
    dst = np.zeros((height,width),np.uint8)
    for i in range(height):
        for j in range(width):
            gray = img[i,j]
            dst[i, j] = abs(gray-255)

    outPath=out+"/"+os.path.basename(path)
    cv2.imwrite(outPath, dst)
    cv2.waitKey(0)



if __name__ == "__main__":
    # os.chdir(r'Z:\lry\data\sat')  # 切换路径到待处理图像所在文件夹
    png_path = r"E:\data\dexi\zhejiang\res_png"
    out_png_path = r"E:\data\dexi\zhejiang\res_r"

    if not os.path.exists(out_png_path):
        os.makedirs(out_png_path)

    for file in os.listdir(png_path):
        png = png_path + '/' + file[:-4] + '.png'  # 读取png图像数据
        reverse(png, out_png_path)


