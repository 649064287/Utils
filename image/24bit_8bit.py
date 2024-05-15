#读取整个bacepath文件夹下的文件并且转换为8位保存到savepath
import os
import cv2
bacepath = r"Z:\sys\data\JYZ_train\all\road\lab_1024"
savepath = r'Z:\sys\data\JYZ_train\all\road\lab_1024_8'
f_n = os.listdir(bacepath)
for n in f_n:
    imdir = bacepath + '\\' + n
    print(n)
    size = os.path.getsize(imdir)  # 根据尺寸判断
    print(size)
    # if size > 2048:
    img = cv2.imread(imdir)

    cropped = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ret, cropped = cv2.threshold(cropped, 0.1, 255, cv2.THRESH_BINARY)
    cv2.imwrite(savepath + '\\' + n.split('.')[0] + '.tif', cropped)  # NOT CAHNGE THE TYPE