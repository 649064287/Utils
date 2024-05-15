import os
from datetime import datetime

import numpy as np
from osgeo import ogr
import logging

# 定义两个矢量文件夹的路径
predict_dir = r"E:\data\ddl\zhejiang\0424(2)\output0424_poly"

label_dir =  r"E:\data\zhejiang\train_149\test\lab_poly"

# 配置logging
# 获取当前时间，用于生成log文件名
now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
# 拼接log文件名
log_file_name = f'log_{now}.txt'
# 拼接log文件的完整路径
log_file_path = os.path.join(os.getcwd(), log_file_name)

# 打开log文件并写入内容
with open(log_file_path, 'w') as f:
    logging.basicConfig(filename=log_file_name, filemode='w', level=logging.INFO)
    logging.info(predict_dir)
# 打开矢量文件
driver = ogr.GetDriverByName('ESRI Shapefile')

sum_IOU = 0
sum_precision=0
sum_recall=0
sum_f1=0
num_files = 0

# 遍历label文件夹中的所有矢量
for label_file in os.listdir(label_dir):
    # 创建字典来存储每个矢量与layer2相交的最大面积
    max_intersect_area = {}
    max_union_area = {}
    layer1_area={}
    layer2_area={}

    if label_file.endswith('.shp'):
        num_files += 1
        # 构建label文件的完整路径
        label_path = os.path.join(label_dir, label_file)
        # 打开label文件
        ds1 = driver.Open(label_path, 0)
        # 获取label文件的第一个图层
        layer1 = ds1.GetLayer()

        # 构建predict文件的完整路径
        predict_path = os.path.join(predict_dir, label_file)
        # 打开predict文件
        ds2 = driver.Open(predict_path, 0)
        # 获取predict文件的第一个图层
        layer2 = ds2.GetLayer()

        # 计算每个layer1矢量与layer2相交的最大面积
        for feat1 in layer1:
            if feat1.GetField('value') == 0:
                continue
            geom1 = feat1.GetGeometryRef()
            max_area = 0
            m_union_area=0
            total_area_intersect = 0
            total_union_area = 0
            max_predict_area = 0

            for feat2 in layer2:
                geom2 = feat2.GetGeometryRef()
                if geom1.Intersect(geom2):
                    intersect = geom1.Intersection(geom2)
                    unionGeom = geom1.Union(geom2)
                    area = intersect.GetArea()
                    union_area = unionGeom.GetArea()
                    if union_area>geom1.GetArea()*10:
                        continue
                    if area > max_area:
                        max_area = area
                        m_union_area = union_area
                        max_predict_area = geom2.GetArea()

            max_intersect_area[feat1.GetFID()] = max_area
            max_union_area[feat1.GetFID()] = m_union_area
            layer1_area[feat1.GetFID()] = geom1.GetArea()# FN+TP
            layer2_area[feat1.GetFID()] = max_predict_area# FP+TP

        # 计算所有矢量的 IOU 并打印结果
        intersect = [val for val in max_intersect_area.values() if isinstance(val, float)]
        # print(intersect)
        union = [val for val in max_union_area.values() if isinstance(val, float)]
        layer1 = [val for val in layer1_area.values() if isinstance(val, float)]
        layer2 = [val for val in layer2_area.values() if isinstance(val, float)]

        if len(union)==0:
            IOU=precision=recall=f1=0
        else:
            IOU = np.sum(intersect)/np.sum(union)
            precision = np.sum(intersect)/np.sum(layer2)
            recall = np.sum(intersect)/np.sum(layer1)
            # f1 = int(TP)*2/(int(TP)*2+int(FN)+int(FP))
            f1=np.sum(intersect)*2/(np.sum(intersect)+np.sum(layer1)+np.sum(layer2))

        logging.info(f"File: {label_file}, IOU: {IOU}")
        logging.info(f"File: {label_file}, precision: {precision}")
        logging.info(f"File: {label_file}, recall: {recall}")
        logging.info(f"File: {label_file}, f1: {f1}")

        sum_IOU += IOU
        sum_precision+=precision
        sum_recall+=recall
        sum_f1+=f1

        # 关闭数据集和图层
        layer1 = None
        layer2 = None
        ds1 = None
        ds2 = None

mIOU = sum_IOU/num_files
m_precision=sum_precision/num_files
m_recall=sum_recall/num_files
m_f1=sum_f1/num_files

logging.info(f"mIOU: {mIOU}")
logging.info(f"m_precision: {m_precision}")
logging.info(f"m_recall: {m_recall}")
logging.info(f"m_f1: {m_f1}")

print("计算完成，结果已写入log文件")
