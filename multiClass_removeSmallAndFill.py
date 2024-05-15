import cv2
import os
import numpy as np


def decide_spots(img, label_class, area_threshold):
    """
    过滤斑点，并将斑点
    :param img: 待处理图像
    :param label_class: 图像中存在的类别数目
    :param area_threshold: 过滤斑点的面积阈值
    :return: 返回处理后图像
    """
    # 获取面积低于阈值区域
    spots_contour = []
    # 找到0类别
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(img, contours, -1, 255, 1)
    for c in contours:
        area_ori = cv2.contourArea(c)
        print(area_ori)
        # Calculated area
        if area_ori < area_threshold:
            spots_contour.append(c)
            cv2.drawContours(img, [c], -1, 0, thickness=-1)  # 先抹去小区域，等待处理是否写回
    # 找到其他类别
    for i_class in range(1, label_class + 1):  # 依次获取每个类别的斑点
        thresholdImgData = img.copy()
        thresholdImgData[thresholdImgData != i_class] = 0
        labelContours, labelHierarchy = cv2.findContours(thresholdImgData, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for j_contour in labelContours:
            area = cv2.contourArea(j_contour)
            print(area)
            if area < area_threshold:
                spots_contour.append(j_contour)
                cv2.drawContours(img, [j_contour], -1, 0, thickness=-1)  # 先抹去小区域，等待处理是否写回

    # 处理斑点区域
    for spot in spots_contour:
        spot_edge_mask = np.zeros_like(img)
        cv2.drawContours(spot_edge_mask, [spot], -1, 1, thickness=3)
        temp_img = img * spot_edge_mask
        pixel_count = np.bincount(temp_img.flatten())
        # 如果不全未0，则填充临近值
        if pixel_count.shape[0] > 1:
            fill_value = (np.argmax(pixel_count[1:]) + 1)
            cv2.drawContours(img, [spot], -1, int(fill_value), thickness=-1)  # 写回临近值
    return img


if __name__ == '__main__':
    img_folder = r'F:\chunan\chunan_sample\select0526\tif_my_DinkNet34_3plus_FocalLoss_open'
    save_folder = r'F:\chunan\chunan_sample\select0526\tif_my_DinkNet34_3plus_FocalLoss_open_remove'
    label_class = 10
    area_threshold = 600
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)
    files = os.listdir(img_folder)
    for file in files:
        if file[-4:] == ".tif":
            img_path = os.path.join(img_folder, file)
            save_path = os.path.join(save_folder, file)
            line = cv2.imread(img_path, 0)
            res_img = decide_spots(line, label_class, area_threshold)
            cv2.imwrite(save_path, res_img)
