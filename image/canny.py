import os
import cv2
import numpy as np

def fillborder(root, result_path):
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    for name in os.listdir(root):
        image = cv2.imread(root+'/'+name)
        gray = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)

        # 80以下为0,210以上为255，中间使用 8-近邻算法确定像素值
        edges = cv2.Canny(gray,80,210)

        # 使用闭运算连接中断的图像前景,迭代运算三次
        result = cv2.morphologyEx(edges,cv2.MORPH_CLOSE,kernel=(3,3),iterations=3)
        # cv2.imwrite(result_path+'/'+name, result)

        cv2.imshow('After Canny',gray)
        cv2.imshow('After Morphology Close',result)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()


fillborder(r"E:\Python\Road-Extraction-master_linux\data_anhui\fusion_ske\anhui",
           r"D:\data\score\fill")