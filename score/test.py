# import cv2
# import numpy as np
# import os
# from time import time
#
#
# start = time()
# predict_path = r"E:\data\BDCN\zhejiang\output_line"
# label_path = r"E:\data\zhejiang\train 149\test\lab"
#
# files = os.listdir(label_path)
# list1 = []
#
# #lab
# for file in files:
#     if file[-4:] == '.tif':
#         result_name = os.path.join(label_path,file)
#         list1.append(result_name)
#
# files = os.listdir(predict_path)
# list2 = []
# print("lable_len:",len(list1))
# #res
# for file in files:
#     if file[-4:] == '.tif':
#         result_name = os.path.join(predict_path,file)
#         list2.append(result_name)
#
# list1.sort()
# list2.sort()
# print("predict_len:",len(list2))
# Recall = 0
# Precision = 0
# F1 = 0
# IOU=0
# ker = [3, 5, 7]
# for i in range(len(list1)):
#     TP = 0
#     FP = 0
#     FN = 0
#     TN = 0
#     img_lable = cv2.imread(list1[i],0)
#     img_predict = cv2.imread(list2[i],0)
#
#     kernel5 = np.ones((ker[1], ker[1]), np.uint8)  # 膨胀
#     img_predict = cv2.dilate(img_predict, kernel5)
#     img_lable = cv2.dilate(img_lable, kernel5)
#
#     print(list1[i])
#     print(list2[i]+'\n')
#     x = np.array(img_lable)
#     #太慢了
#     # for j in range(x.shape[0]):
#     #     for k in range(x.shape[1]):
#     #         if (img_lable[j][k] == 255 and img_predict[j][k] == 255):
#     #             TP += 1
#     #         elif (img_lable[j][k] == 255 and img_predict[j][k] == 0):
#     #             FN += 1
#     #         elif (img_lable[j][k] == 0 and img_predict[j][k] == 255):
#     #             FP += 1
#     #         elif (img_lable[j][k] == 0 and img_predict[j][k] == 0):
#     #             TN += 1
#     for j in range(x.shape[0]):
#         index = np.arange(0, x.shape[1])
#         a = index[img_lable[j]==img_predict[j]]
#         for k in range(len(a)):
#             if img_lable[j][a[k]] >= 127:
#                 TP += 1
#             else:
#                 TN += 1
#         b = index[img_lable[j] != img_predict[j]]
#         for k in range(len(b)):
#             if img_lable[j][b[k]] >= 127:
#                 FN += 1
#             else:
#                 FP += 1
#     # print(TP,TN,FN,FP)
#     if TP+FP != 0:
#         Precision += TP/(TP+FP)
#     else:
#         Precision += 1
#     if TP+FN != 0:
#         Recall += TP/(TP+FN)
#     else:
#         Recall += 1
#     if TP+FP != 0 and TP+FN != 0 and TP != 0:
#         F1 += (2 * (TP/(TP+FP)) * (TP/(TP+FN))/((TP/(TP+FP)) + (TP/(TP+FN))))
#     else:
#         F1 += 1
#     if TP + FP + FN != 0:
#         IOU += (TP / (TP + FP + FN))
#     # print("第",i+1,"次计算完成")
# end = time()
# print('running time is :%f'%(end-start))
# print("Precision:" ,Precision/len(files),"Recall:",Recall/len(files),"F1:",F1/len(files), "IOU:", IOU/len(files))
#
#

import cv2
import numpy as np
import os
from time import time


start = time()
predict_path = r"E:\data\ddl\zhejiang\0424(2)\output0424_line"
label_path = r"E:\data\zhejiang\train_149\test\lab"

files = os.listdir(label_path)
list1 = []

#lab
for file in files:
    if file[-4:] == '.tif':
        result_name = os.path.join(label_path,file)
        list1.append(result_name)

files = os.listdir(predict_path)
list2 = []
print("lable_len:",len(list1))
#res
for file in files:
    if file[-4:] == '.tif':
        result_name = os.path.join(predict_path,file)
        list2.append(result_name)

list1.sort()
list2.sort()
print("predict_len:",len(list2))
Recall = 0
Precision = 0
F1 = 0
IOU=0
ker = [3, 5, 7]
log_file_name = os.path.join(r"C:\App\Python\utils\score", f"result_log_{time()}.txt")
with open(log_file_name, "w") as log_file:
    for i in range(len(list1)):
        TP = 0
        FP = 0
        FN = 0
        TN = 0
        img_lable = cv2.imread(list1[i],0)
        img_predict = cv2.imread(list2[i],0)

        kernel5 = np.ones((ker[1], ker[1]), np.uint8)  # 膨胀
        img_predict = cv2.dilate(img_predict, kernel5)
        img_lable = cv2.dilate(img_lable, kernel5)

        log_file.write(f"{list1[i]}\n")
        log_file.write(f"{list2[i]}\n")
        x = np.array(img_lable)
        for j in range(x.shape[0]):
            index = np.arange(0, x.shape[1])
            a = index[img_lable[j]==img_predict[j]]
            for k in range(len(a)):
                if img_lable[j][a[k]] >= 127:
                    TP += 1
                else:
                    TN += 1
            b = index[img_lable[j] != img_predict[j]]
            for k in range(len(b)):
                if img_lable[j][b[k]] >= 127:
                    FN += 1
                else:
                    FP += 1
        if TP+FP != 0:
            Precision += TP/(TP+FP)
        else:
            Precision += 1
        if TP+FN != 0:
            Recall += TP/(TP+FN)
        else:
            Recall += 1
        if TP+FP != 0 and TP+FN != 0 and TP != 0:
            F1 += (2 * (TP/(TP+FP)) * (TP/(TP+FN))/((TP/(TP+FP)) + (TP/(TP+FN))))
        else:
            F1 += 1
        if TP + FP + FN != 0:
            IOU += (TP / (TP + FP + FN))
    end = time()
    log_file.write(f'running time is :{end-start}\n')
    log_file.write(f"Precision:{Precision/len(files)}, Recall:{Recall/len(files)}, F1:{F1/len(files)}, IOU:{IOU/len(files)}\n")

print("日志文件已生成:", log_file_name)
