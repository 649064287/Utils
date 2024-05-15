import glob
import os

import cv2
import numpy as np


def npz():
    # #图像路径
    # path = r'D:\data\car\train\images\*.png'
    # #项目中存放训练所用的npz文件路径
    # path2 = r'D:\data\car\Synapse\train_npz\\'

    # 图像路径
    path = r'D:\data\car\val\images\*.png'
    # 项目中存放训练所用的npz文件路径
    path2 = r'D:\data\car\Synapse\test_npz\\'

    for i,img_path in enumerate(glob.glob(path)):
    	#读入图像
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        #读入标签
        label_path = img_path.replace('images','labels')
        label = cv2.imread(label_path,flags=0)
		#保存npz
        np.savez(path2+str(i),image=image,label=label)
        print('------------',i)

    # 加载npz文件
    # data = np.load(r'G:\dataset\Unet\Swin-Unet-ori\data\Synapse\train_npz\0.npz', allow_pickle=True)
    # image, label = data['image'], data['label']

    print('ok')


def write_txt(root, txt_path):
    f = open(txt_path, "w")
    for name in os.listdir(root):
        f.write(name[:-4] + '\n')


# npz()
# write_txt(r"D:\data\car\Synapse\train_npz", r"D:\data\car\Synapse\train.txt")
write_txt(r"D:\data\car\Synapse\test_npz", r"D:\data\car\Synapse\test.txt")
