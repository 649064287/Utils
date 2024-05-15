import cv2
import os
def tif_greytif(img_folder):
    files = os.listdir(img_folder)
    save_folder = img_folder + '_grey'
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    for file in files:
        if file[-4:] == ".tif":
            save_path = os.path.join(save_folder, file)
            img = cv2.imread(os.path.join(img_folder, file), 0)  # 读取图片
            ret, dst = cv2.threshold(img, 255, 255,cv2.THRESH_BINARY)
            cv2.imwrite(save_path, dst)
img_folder = r'D:\data\sample_farm2\sg\kuang'
tif_greytif(img_folder)