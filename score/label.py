import os

import numpy as np
from osgeo import ogr, osr, gdalconst
from tqdm import tqdm
from osgeo import gdal_array

def create_field(layer, field_name):
    fieldIndex = layer.GetLayerDefn().GetFieldIndex(field_name)
    if fieldIndex < 0:
        # 添加字段
        fieldDefn = ogr.FieldDefn(field_name, ogr.OFTInteger)  # 添加字段名及设置其类型,Real为字符串
        # fieldDefn.SetWidth(10)  # 字符串设定宽度
        layer.CreateField(fieldDefn, 1)
        if fieldIndex > 0:
            print("字段创建成功：", field_name)
    else:
        print(field_name + "字段已存在，无需创建！")

def set_label(shapefile):
    """添加value字段，值设为255"""
    driver = ogr.GetDriverByName('ESRI Shapefile')
    phase_ds = driver.Open(shapefile, 1)
    layer = phase_ds.GetLayer(0)

    create_field(layer, 'value')
    for feat in tqdm(layer):
        feat.SetField('value', 255)
        layer.SetFeature(feat)

    del layer


from osgeo import ogr, gdal


def get_tif_meta(tif_path):
    dataset = gdal.Open(tif_path)
    # 栅格矩阵的列数
    width = dataset.RasterXSize
    # 栅格矩阵的行数
    height = dataset.RasterYSize
    # 获取仿射矩阵信息
    geotrans = dataset.GetGeoTransform()
    # 获取投影信息
    proj = dataset.GetProjection()
    return width, height, geotrans, proj


def shp2tif(shp_path, refer_tif_path, target_tif_path, attribute_field, nodata_value=0):
    width, height, geotrans, proj = get_tif_meta(refer_tif_path)
    # 读取shp文件
    shp_file = ogr.Open(shp_path)
    # 获取图层文件对象
    shp_layer = shp_file.GetLayer()
    # 创建栅格
    target_ds = gdal.GetDriverByName('GTiff').Create(
        utf8_path=target_tif_path,  # 栅格地址
        xsize=width,  # 栅格宽
        ysize=height,  # 栅格高
        bands=1,  # 栅格波段数
        eType=gdal.GDT_Byte  # 栅格数据类型
    )
    # 将参考栅格的仿射变换信息设置为结果栅格仿射变换信息
    target_ds.SetGeoTransform(geotrans)
    # 设置投影坐标信息
    target_ds.SetProjection(proj)
    band = target_ds.GetRasterBand(1)
    # 设置背景nodata数值
    band.SetNoDataValue(nodata_value)
    band.FlushCache()

    # 栅格化函数
    gdal.RasterizeLayer(
        dataset=target_ds,  # 输出的栅格数据集
        bands=[1],  # 输出波段
        layer=shp_layer,  # 输入待转换的矢量图层
        options=[f"ATTRIBUTE={attribute_field}"]  # 指定字段值为栅格值
    )

    del target_ds


def field_value(predict_dir, label_dir, file):
    # 打开矢量文件
    driver = ogr.GetDriverByName('ESRI Shapefile')
    # 构建label文件的完整路径
    label_path = os.path.join(label_dir, file)
    # 打开label文件
    ds1 = driver.Open(label_path, 0)
    # 获取label文件的第一个图层
    layer1 = ds1.GetLayer()

    # 构建predict文件的完整路径
    predict_path = os.path.join(predict_dir, file)
    # 打开predict文件
    ds2 = driver.Open(predict_path, 1)
    # 获取predict文件的第一个图层
    layer2 = ds2.GetLayer()

    print(label_path)
    print(predict_path)
    # 计算每个layer1矢量与layer2相交的最大面积
    for feat1 in layer1:
        if feat1.GetField('value') == 0:
            geom1 = feat1.GetGeometryRef()
            max_area = 0
            feat2_id=-1
            for feat2 in layer2:
                geom2 = feat2.GetGeometryRef()
                if geom1.Intersect(geom2):
                    # 相交
                    intersect = geom1.Intersection(geom2)
                    area = intersect.GetArea()
                    # 选取最大相交面积 大于max_area
                    if area > max_area:
                        max_area=area
                        feat2_id=feat2.GetFID()

            # print(feat2_id)
            if feat2_id!=-1:
                # 使用 SQL 语句查询指定 FID 的要素
                layer2.SetAttributeFilter('FID = {}'.format(feat2_id))
                # 获取第一个要素
                feature = layer2.GetNextFeature()
                feature.SetField('value', 0)
                layer2.SetFeature(feature)

                layer2.ResetReading()
                layer2.SetAttributeFilter(None)

    # 关闭数据源
    ds1.Release()
    ds2.Release()

# root=r"E:\data\zhejiang\0209\output_poly"
# target_path=r"E:\data\zhejiang\0209\output_poly_tif"

predict_dir=r"E:\data\ddl\zhejiang\0424(2)\output0424_poly"
label_dir=r"E:\data\zhejiang\train_149\test\lab_poly"
# img_path=r"E:\data\zhejiang\train 149\test\img1"
# target_path=r"E:\data\zhejiang\train 149\test\lab"
#
# if not os.path.exists(target_path):
#     os.makedirs(target_path)

for file in os.listdir(predict_dir):
    if file.endswith('.shp'):
        #第一步，添加value字段
        set_label(os.path.join(predict_dir, file))
        #设置背景值
        field_value(predict_dir, label_dir, file)

#         #第三步，shp转栅格
#         shp = os.path.join(root, file)
#         sp=file.split("_")
#         img_name = sp[0]+'_'+sp[1] + '_poly.tif'
#         img = os.path.join(img_path, img_name)
#         target = os.path.join(target_path, img_name)
#         shp2tif(shp, img, target, 'value')
