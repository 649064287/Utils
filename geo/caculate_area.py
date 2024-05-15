import json
import logging
import os

# import gdal
import numpy as np
import pandas as pd
from osgeo import ogr, gdal
from tqdm import tqdm
import datetime

import geopandas as gpd
import rasterio as rio
import rasterio.mask
from xpinyin import Pinyin

# gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
gdal.SetConfigOption("SHAPE_ENCODING","GBK")

import sys
import logging
from logging import handlers

# 日志级别关系映射
level_relations = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'crit': logging.CRITICAL
}

def _get_logger(filename, level='info'):
    # 创建日志对象
    log = logging.getLogger(filename)
    # 设置日志级别
    log.setLevel(level_relations.get(level))
    # 日志输出格式
    fmt = logging.Formatter('%(asctime)s %(thread)d %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    # 输出到控制台
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    # 输出到文件
    # 日志文件按天进行保存，每天一个日志文件
    file_handler = handlers.TimedRotatingFileHandler(filename=filename, when='D', backupCount=1, encoding='utf-8')
    # 按照大小自动分割日志文件，一旦达到指定的大小重新生成文件
    # file_handler = handlers.RotatingFileHandler(filename=filename, maxBytes=1*1024*1024*1024, backupCount=1, encoding='utf-8')
    file_handler.setFormatter(fmt)

    log.addHandler(console_handler)
    log.addHandler(file_handler)
    return log

def caculate(gengdi_path, sandiao_path):
    """
    三调、耕地数据均为栅格数据
    :param gengdi_path:
    :param sandiao_path:
    :return:
    """

    gdDS = gdal.Open(gengdi_path)
    cols = gdDS.RasterXSize
    rows = gdDS.RasterYSize
    print(cols, rows)
    geotransform = gdDS.GetGeoTransform()
    projection = gdDS.GetProjection()
    gdData = gdDS.GetRasterBand(1).ReadAsArray().astype(np.float32)
    gdNoData = gdDS.GetRasterBand(1).GetNoDataValue()

    sdDS = gdal.Open(sandiao_path)
    cols_ = sdDS.RasterXSize
    rows_ = sdDS.RasterYSize
    print(cols_, rows_)
    sdData = sdDS.GetRasterBand(1).ReadAsArray().astype(np.float32)
    sdNoData = sdDS.GetRasterBand(1).GetNoDataValue()

    gd_dict={}
    resultData=np.zeros((rows, cols))
    total_area=cols*rows
    correct=0.0
    #以三调数据为准
    for col in range(cols):
        for row in range(rows):
            try:
                if gdData[row, col] != gdNoData and sdData[row, col]==1:
                    #重叠
                    resultData[row,col]=gdData[row, col]
                    correct += 1
                else:
                    resultData[row,col]=gdNoData
            except Exception:
                print(col, row)
                continue

    print(correct/total_area*100.0)
    format = "GTiff"
    resultPath=r"C:\Users\lry\Documents\潼南\潼南\test\result.tif"
    driver = gdal.GetDriverByName(format)
    ds = driver.Create(resultPath, cols, rows, 1, gdal.GDT_Float32)
    ds.SetGeoTransform(geotransform)
    ds.SetProjection(projection)
    ds.GetRasterBand(1).SetNoDataValue(gdNoData)
    ds.GetRasterBand(1).WriteArray(resultData)
    ds = None

def caculate_intersection(ori_path, new_path, old_path):
    """
    :type 0:不是耕地 1：75%耕地 2：50%耕地 3：25%耕地
    :param ori_path: 耕地矢量
    :param new_path: 栅格数据
    :return:
    """
    gdDS = gdal.Open(new_path)
    cols = gdDS.RasterXSize
    rows = gdDS.RasterYSize
    geotransform = gdDS.GetGeoTransform()
    projection = gdDS.GetProjection()
    gdData = gdDS.GetRasterBand(1).ReadAsArray().astype(np.float32)
    gdNoData = gdDS.GetRasterBand(1).GetNoDataValue()

    oldDS = gdal.Open(old_path)
    oldData = oldDS.GetRasterBand(1).ReadAsArray().astype(np.float32)
    oldNoData = oldDS.GetRasterBand(1).GetNoDataValue()

    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds_poly = driver.Open(ori_path, 1)
    layer = ds_poly.GetLayer(0)
    type_dict={1:0,
               2:0,
               3:0,
               0:0,}
    total=0
    for feat in tqdm(layer):
        try:
            id = feat.GetField('id')
            gd_area=np.sum(gdData[gdData==id])
            old_area=np.sum(oldData[oldData==id])
            if old_area:
                percentage=float(gd_area/old_area)*100.0
                if percentage>=75.0:
                    feat.SetField('type', 1)
                    layer.SetFeature(feat)
                    type_dict[1]+=1
                elif percentage<75.0 and percentage>=50.0:
                    feat.SetField('type', 2)
                    layer.SetFeature(feat)
                    type_dict[2] += 1
                elif percentage < 50.0 and percentage >= 25.0:
                    feat.SetField('type', 3)
                    layer.SetFeature(feat)
                    type_dict[3] += 1
                else:
                    feat.SetField('type', 0)
                    layer.SetFeature(feat)
                    type_dict[0] += 1
                total+=1
        except Exception as e:
            print(e)
    layer.ResetReading()  #复位

    del ds_poly
    print("100%~75%耕地: ", type_dict[1]/total)
    print("75%~50%耕地: ", type_dict[2] / total)
    print("50%~25%耕地: ", type_dict[3] / total)
    print("非耕地: ", type_dict[0] / total)


def caculate_xiangzhen(inpath1, inpath2):
    """

    :param inpath1: 乡镇边界矢量
    :param inpath2: calcres
    :return:
    """
    # 打开市行政边界矢量
    city_ds = ogr.Open(inpath1)
    city_layer = city_ds.GetLayer()

    # 打开乡镇矢量
    town_ds = ogr.Open(inpath2, 1)
    town_layer = town_ds.GetLayer()

    # 创建新字段并添加到乡镇矢量
    new_field_name = "xiangzhen"
    new_field_type = ogr.OFTString
    town_layer.CreateField(ogr.FieldDefn(new_field_name, new_field_type))

    # 遍历乡镇矢量的要素
    for town_feature in town_layer:
        town_geometry = town_feature.GetGeometryRef()
        city_name = None  # 初始化城市名称为None

        # 遍历市行政边界矢量的要素
        for city_feature in city_layer:
            city_geometry = city_feature.GetGeometryRef()

            # 判断是否相交
            if town_geometry.Intersect(city_geometry):
                city_name = city_feature.GetField("XZQMC")  # 获取城市名称
                break  # 一旦找到相交的市行政边界，退出循环

        # 将城市名称赋给乡镇矢量的新字段
        if city_name:
            town_feature.SetField(new_field_name, city_name)
            town_layer.SetFeature(town_feature)

    # 保存修改后的乡镇矢量
    town_ds.SyncToDisk()
    town_ds = None  # 释放资源
    city_ds = None  # 释放资源

def change_type(shp):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds_poly = driver.Open(shp, 1)
    layer = ds_poly.GetLayer(0)

    for feat in tqdm(layer):
        try:
            id = feat.GetField('Crop_type')
            if id=='0':
                feat.SetField('Crop_type', '98')
            elif id=='1':
                feat.SetField('Crop_type', '01')
            elif id == '2':
                feat.SetField('Crop_type', '02')
            elif id=='3':
                feat.SetField('Crop_type', '03')
            layer.SetFeature(feat)
        except Exception as e:
            print(e)
    layer.ResetReading()

def caculate_polygon(poly_folder, line_folder, Field_ID):
     # files = os.listdir(poly_folder)
    # for file in files:
    #     if file[-4:] == ".shp":
    # dir, file = os.path.split(poly_folder)
    # print(file)
    # print(datetime.datetime.now())
    # line_path = os.path.join(line_folder, file)
    # # poly_path = os.path.join(poly_folder, file)
    # poly_path = poly_folder
    ds_line = ogr.Open(poly_folder, 1)
    ds_poly = ogr.Open(line_folder, 1)

    # no_type_lyr = ds_line.GetLayer('no_type_lyr')
    # type_lyr = ds_poly.GetLayer('type_lyr')
    no_type_lyr = ds_line.GetLayer(0)
    type_lyr = ds_poly.GetLayer(0)
    # try:
    #     no_type_lyr.GetFeature(0).GetField('DLBM')
    # except:
    #     fld = ogr.FieldDefn('DLBM', ogr.OFTInteger)
    #     no_type_lyr.CreateField(fld)
    for no_type_feat in tqdm(no_type_lyr):
            type_lyr.SetSpatialFilter(no_type_feat.geometry())
            max_area = -1
            for type_feat in type_lyr:
                try:
                    if type_feat.GetField('GRIDCODE')==0:
                        continue
                    intersect = no_type_feat.geometry().Intersection(type_feat.geometry())
                    area = intersect.GetArea()
                    if area > max_area:
                        crop_type = type_feat.GetField('GRIDCODE')
                        no_type_feat.SetField(Field_ID, crop_type)
                        max_area = area
                        print(max_area)
                except:
                    pass

            no_type_lyr.SetFeature(no_type_feat)
            # print(no_type_feat.GetField('Id'), max_DLBM, max_area)
    del ds_line
    del ds_poly

def add_mean_value_field(raster_file, shp_file, out_shp_file):
     """
     计算矢量图斑范围内的栅格均值并增加字段
     :param raster_file: 待计算均值的栅格底图
     :param shp_file: 与栅格数据叠加的矢量掩膜数据
     :param out_shp_file: 增加均值字段后输出的矢量数据，可与shp_file相同，即重写shp_file文件
     :return
     """

     shp_data = gpd.GeoDataFrame.from_file(shp_file)
     raster_data = rio.open(raster_file)
     profile = raster_data.profile
     # 保存投影信息一致
     shp_data = shp_data.to_crs(raster_data.crs)

     out_shp_data = shp_data.copy()
     # print(out_shp_data.index)
     out_shp_data.insert(out_shp_data.shape[1], 'id', range(0, len(out_shp_data)))
     # print(out_shp_data['id'])
     mean_value_field = []

     def publicnum(num, d=0):
         dictnum = {}
         for i in range(len(num)):
             if num[i] in dictnum.keys():
                 dictnum[num[i]] += 1
             else:
                 dictnum.setdefault(num[i], 1)
         maxnum = 0
         maxkey = 0
         for k, v in dictnum.items():
             if v > maxnum:
                 maxnum = v
                 maxkey = k
         return maxkey

     for i in tqdm(range(0, len(shp_data))):
         # 获取矢量数据的features
         geo = shp_data.geometry[i]
         feature = [geo.__geo_interface__]
         # 通过feature裁剪栅格影像
         out_image, out_transform = rio.mask.mask(raster_data, feature, all_touched=True, crop=True,
                                                      nodata=raster_data.nodata)
         # 获取影像Value值，并转化为list
         out_list = out_image.data.tolist()
         # 除去list中的Nodata值
         out_list = out_list[0]
         out_data = []
         for k in range(len(out_list)):
             for j in range(len(out_list[k])):
                 if out_list[k][j] > 0:
                     out_data.append(out_list[k][j])
         # 求数据的平均数
         if len(out_data):
             public = publicnum(out_data)
             # public = np.mean(out_data)
         else:
             public = None
         mean_value_field.append(public)

     # 增加属性字段，并将GeodataFrame导出为shp文件
     out_shp_data.insert(out_shp_data.shape[1], 'Crop_type', mean_value_field)
     # out_shp_data.loc[:,'Crop_type']=mean_value_field
     # out_shp_data.loc[out_shp_data['land_type']!='10000', 'Crop_type'] = 0
     out_shp_data.to_file(out_shp_file)

def compose_time(shapefile1, shapefile2, out_shapefile):
    """

    :param shapefile1: 需要输出的shp
    :param shapefile2: 时序shp
    :return:
    """
    shp_data = gpd.GeoDataFrame.from_file(shapefile1)
    shp_data2 = gpd.GeoDataFrame.from_file(shapefile2)
    out_shp_data = shp_data.copy()
    # print(out_shp_data.index)
    # shp_data2.insert(shp_data2.shape[1], 'id', range(0, len(shp_data2)))
    concat_columns = shp_data2[['LAND_CODE', 'I', 'II', 'R']]
    # print(concat_columns.head())
    out_shp_data=pd.merge(out_shp_data, concat_columns, how='outer', left_on='land_code', right_on='LAND_CODE')
    # print(out_shp_data.head())
    out_shp_data.to_file(out_shapefile)


def shpType2json(shapefile, json_path):
    """
    将矢量地块属性转为json
    :param shp:
    :return:
    """
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds_poly = driver.Open(shapefile, 1)
    layer = ds_poly.GetLayer(0)

    dict = {}
    for feat in tqdm(layer):
        try:
            id = int(feat.GetField('id'))
            DK_dem = feat.GetField('land_dem')
            DK_slope = feat.GetField('land_slope')
            DK_AD = feat.GetField('land_xz')
            DK_phase = feat.GetField('land_phase')
            Crop_type = feat.GetField('Crop_type')
            land_dlbm = feat.GetField('land_dlbm')
            one = feat.GetField('I')
            two = feat.GetField('II')
            r = feat.GetField('R')
            dict.update({id:
                             ({'DK_dem': str(DK_dem),
                               'DK_slope': str(DK_slope),
                               'DK_AD': str(DK_AD),
                               'DK_phase': str(DK_phase),
                               'Crop_type': str(Crop_type),
                               'land_dlbm': str(land_dlbm),
                               'I': str(one),
                               'II': str(two),
                               'R': str(r)
                               })
                         })
        except Exception:
            print(id)
    layer.ResetReading()

    with open(json_path, 'w') as input_json:
        json.dump(dict, input_json, ensure_ascii=False)


def json2shpField(json_path, shp_file, out_shp_file=None):
    """
    将矢量地块属性转为json
    :param shp:
    :return:
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        crop_dict=json.load(f)

    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds_poly = driver.Open(shp_file, 1)
    layer = ds_poly.GetLayer(0)

    # 创建输出矢量数据， 太慢故注释
    # fn_out = out_shp_file
    # gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
    # gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")
    # driver = ogr.GetDriverByName("ESRI Shapefile")
    # datasource_out = driver.CreateDataSource(fn_out)
    # layer_out = datasource_out.CreateLayer("layer_out", srs=layer.GetSpatialRef(), geom_type=ogr.wkbPolygon)
    #
    # layer_in_defn = layer.GetLayerDefn()  # 获取图层的属性表表头信息
    # field_count = layer_in_defn.GetFieldCount()  # 获取属性列数
    #
    # # 给输出图层定义一个属性表,并创建字段
    # for i in range(field_count):
    #     field_defn = layer_in_defn.GetFieldDefn(i)
    #     # field_defn.name.encode("utf-8").decode("ISO-8859-1")
    #     layer_out.CreateField(field_defn)  # 创建字段
    #
    # layer_out_defn = layer_out.GetLayerDefn()
    #
    # # 从输入图层中取出要素，并进行坐标转换，以及创建要素以写入输出图层中
    # feature_in = layer.GetNextFeature()
    # while feature_in:
    #     feature_out = ogr.Feature(layer_out_defn)
    #     geomref_in = feature_in.GetGeometryRef()
    #     feature_out.SetGeometry(geomref_in)  # 复制几何要素
    #     for j in range(field_count):
    #         # field_in_defn = layer_in_defn.GetFieldDefn(j)
    #         field_out_defn = layer_out_defn.GetFieldDefn(j)
    #         name = field_out_defn.name  # 键
    #         field_value = feature_in.GetField(name)  # 值
    #         feature_out.SetField(name, field_value)  # 复制属性
    #     layer_out.CreateFeature(feature_out)
    #     feature_in = layer.GetNextFeature()

    def create_field(layer, field_name):
        fieldIndex = layer.GetLayerDefn().GetFieldIndex(field_name)
        if fieldIndex<0:
            # 添加字段
            fieldDefn = ogr.FieldDefn(field_name, ogr.OFTString)#添加字段名及设置其类型,Real为字符串
            fieldDefn.SetWidth(10)#字符串设定宽度
            layer.CreateField(fieldDefn, 1)
            if fieldIndex > 0:
                print("字段创建成功：", field_name)
        else:
            print(field_name + "字段已存在，无需创建！")

    create_field(layer, 'Crop')

    for feat in tqdm(layer):
        try:
            id = feat.GetField('id')
            crop_prob=feat.GetField('Prob')
            crop_prob_per=crop_prob/100.0 if crop_prob is not None else 0.0
            crop_type=crop_dict[str(id)]

            #概率相乘
            for k in crop_type:
                if crop_type[k] is not None and crop_prob_per != 0:
                    v=float(crop_type[k][:-1])*crop_prob_per
                    crop_type.update({k: v})
                else:
                    crop_type.update({k, 0.0})

            # print(crop_type)
            #选择概率最大的作物
            if max(crop_type.values())==0:
                feat.SetField('Crop', None)
                feat.SetField('Prob', None)
            else:
                max_k = max(crop_type, key=crop_type.get)
                feat.SetField('Crop', max_k)
                feat.SetField('Prob', crop_type[max_k])
            layer.SetFeature(feat)
        except Exception:
            # print(id)
            continue
    layer.ResetReading()

    del ds_poly

def json2shpField2(json_path, shp_file, out_shp_file=None):
    """
    赋值每个月耕地类型
    :param shp:
    :return:
    """
    fields = ['crop_r01', 'crop_r02', 'crop_r03', 'crop_r04', 'crop_r05',
                 'crop_r06', 'crop_r07', 'crop_r08', 'crop_r09', 'crop_r10',
                 'crop_r11', 'crop_r12',
                 'crop_l07', 'crop_l08', 'crop_l09', 'crop_l10', 'crop_l11',
                 'crop_l12', 'crop_n01', 'crop_n02', 'crop_n03', 'crop_n04',
                 'crop_n05', 'crop_n06']

    crop_code = {
        '水稻': '01',
        '玉米': '02',
        '油菜': '03',
        '小麦': '04',
        '马铃薯': '05',
        '红苕': '06',
        '高粱': '07',
        '其他类型': '08'
    }

    with open(json_path, 'r', encoding='utf-8') as f:
        crop_dict=json.load(f)

    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds_poly = driver.Open(shp_file, 1)
    layer = ds_poly.GetLayer(0)

    for feat in tqdm(layer):
        try:
            id = int(feat.GetField('id'))
            for field in fields:
                prob_field = 'cm_' + field[-3:]
                month = field[-2:]
                if feat.GetField('land_type') == '10000':
                    # print(list(crop_dict[str(id)][month].keys())[0])
                    # print(list(crop_dict[str(id)][month].values())[0])
                    if len(list(crop_dict[str(id)][month])):
                        crop=list(crop_dict[str(id)][month].keys())[0]
                        prob=list(crop_dict[str(id)][month].values())[0]
                        prob=round(float(prob[:-1])/100.0, 2)
                        feat.SetField(field, crop_code[crop])
                        feat.SetField(prob_field, str(prob))
                    else:
                        feat.SetField(field, None)
                        feat.SetField(prob_field, None)
                else:
                    feat.SetField(field, None)
                    feat.SetField(prob_field, None)
            layer.SetFeature(feat)
        except Exception:
            continue

    layer.ResetReading()

    del ds_poly

# 舍弃，速度太慢
# def add_phase(shapefile1, shapefile2):
#     """
#
#     :param shapefile1: 时相数据
#     :param shapefile2: 耕地矢量
#     :return:
#     """
#     driver = ogr.GetDriverByName('ESRI Shapefile')
#     phase_ds = driver.Open(shapefile1, 1)
#     phase_lyr = phase_ds.GetLayer(0)
#
#     ds_poly = driver.Open(shapefile2, 1)
#     poly_lyr = ds_poly.GetLayer(0)
#
#     for feat1 in tqdm(poly_lyr):
#         poly_geom = feat1.geometry().Clone()
#         max_area=0
#         time=-1
#         for feat2 in phase_lyr:
#             phase_geom = feat2.geometry().Clone()
#             if poly_geom.Intersection(phase_geom):
#                 intersect = poly_geom.Intersection(phase_geom).GetArea()
#                 if intersect>max_area:
#                     max_area=intersect
#                     time = feat2.Getfeild('phase_1')
#         feat1.SetField('land_phase', time)
#         poly_lyr.SetFeature(feat1)
#
#     del poly_lyr
#     del phase_lyr

def add_phase_raster(raster_file, shp_file, out_shp_file):
    """
    计算矢量图斑范围内的栅格均值并增加字段
    :param raster_file: 待计算均值的栅格底图
    :param shp_file: 与栅格数据叠加的矢量掩膜数据
    :param out_shp_file: 增加均值字段后输出的矢量数据，可与shp_file相同，即重写shp_file文件
    :return
    """

    shp_data = gpd.GeoDataFrame.from_file(shp_file)
    dbf = gpd.read_file(r"E:\BaiduNetdiskDownload\11.8\重庆phase1\phase.tif.vat.dbf")
    # print(dbf['phase_1'])
    dbf_dict=dict(zip(dbf['Value'], dbf['phase_1']))
    raster_data = rio.open(raster_file)
    profile = raster_data.profile
    # 保存投影信息一致
    shp_data = shp_data.to_crs(raster_data.crs)

    out_shp_data = shp_data.copy()
    mean_value_field = []

    def publicnum(num, d=0):
        dictnum = {}
        for i in range(len(num)):
            if num[i] in dictnum.keys():
                dictnum[num[i]] += 1
            else:
                dictnum.setdefault(num[i], 1)
        maxnum = 0
        maxkey = 0
        for k, v in dictnum.items():
            if v > maxnum:
                maxnum = v
                maxkey = k
        return maxkey

    for i in tqdm(range(0, len(shp_data))):
        # 获取矢量数据的features
        geo = shp_data.geometry[i]
        feature = [geo.__geo_interface__]
        # 通过feature裁剪栅格影像
        out_image, out_transform = rio.mask.mask(raster_data, feature, all_touched=True, crop=True,
                                                 nodata=raster_data.nodata)
        # 获取影像Value值，并转化为list
        out_list = out_image.data.tolist()
        # 除去list中的Nodata值
        out_list = out_list[0]
        out_data = []
        for k in range(len(out_list)):
            for j in range(len(out_list[k])):
                if out_list[k][j] > 0:
                    out_data.append(out_list[k][j])
        # 求数据的最大值
        if len(out_data):
            public = publicnum(out_data)
        else:
            public = None
        mean_value_field.append(dbf_dict.get(public))

    # 增加属性字段，并将GeodataFrame导出为shp文件
    # out_shp_data.insert(out_shp_data.shape[1], 'Crop_type', mean_value_field)
    out_shp_data.loc[:, 'land_phase'] = mean_value_field
    out_shp_data.to_file(out_shp_file)


def add_mean_prob(raster_file, shp_file, out_shp_file):
    """
    计算矢量图斑范围内的栅格均值并增加字段
    :param raster_file: 待计算均值的栅格底图
    :param shp_file: 与栅格数据叠加的矢量掩膜数据
    :param out_shp_file: 增加均值字段后输出的矢量数据，可与shp_file相同，即重写shp_file文件
    :return
    """

    shp_data = gpd.GeoDataFrame.from_file(shp_file)
    raster_data = rio.open(raster_file)
    profile = raster_data.profile
    # 保存投影信息一致
    shp_data = shp_data.to_crs(raster_data.crs)

    out_shp_data = shp_data.copy()
    mean_value_field = []

    def publicnum(num, d=0):
        dictnum = {}
        for i in range(len(num)):
            if num[i] in dictnum.keys():
                dictnum[num[i]] += 1
            else:
                dictnum.setdefault(num[i], 1)
        maxnum = 0
        maxkey = 0
        for k, v in dictnum.items():
            if v > maxnum:
                maxnum = v
                maxkey = k
        return maxkey

    for i in tqdm(range(0, len(shp_data))):
        # 获取矢量数据的features
        geo = shp_data.geometry[i]
        feature = [geo.__geo_interface__]
        # 通过feature裁剪栅格影像
        out_image, out_transform = rio.mask.mask(raster_data, feature, all_touched=True, crop=True,
                                                 nodata=raster_data.nodata)
        # 获取影像Value值，并转化为list
        out_list = out_image.data.tolist()
        # 除去list中的Nodata值
        out_list = out_list[0]
        out_data = []
        for k in range(len(out_list)):
            for j in range(len(out_list[k])):
                if out_list[k][j] > 0:
                    out_data.append(out_list[k][j])
        # 求数据的平均数
        if len(out_data):
            # public = publicnum(out_data)
            public = np.mean(out_data)
        else:
            public = None
        mean_value_field.append(public)

    # 增加属性字段，并将GeodataFrame导出为shp文件
    out_shp_data.insert(out_shp_data.shape[1], 'Prob', mean_value_field)
    # out_shp_data.loc[:,'Crop_type']=mean_value_field
    out_shp_data.loc[out_shp_data['land_type'] != '10000', 'Prob'] = 0
    out_shp_data.to_file(out_shp_file)

def duplicate(in_path, out_path):
    crop_dict={
        '水稻': '01',
        '玉米': '02',
        '油菜': '03',
        '小麦': '04',
        '马铃薯': '05',
        '红苕': '06',
        '高粱': '07',
        '其他类型': '08'
    }
    keep_dict=[]
    shp_data = gpd.GeoDataFrame.from_file(in_path, encoding='gbk')
    out_shp_data = shp_data.copy()
    all_cloumns = []
    # for col in out_shp_data.columns:
    #     all_cloumns.append(col)
    # print(all_cloumns)
    # for k in keep_dict:
    #     all_cloumns.remove(k)
    # out_shp_data = out_shp_data.drop(labels=all_cloumns, axis=1)
    for k in crop_dict:
        out_shp_data.replace(k, crop_dict.get(k), inplace=True)
    out_shp_data.to_file(out_path)



if __name__ == "__main__":

    # root=r"Z:\lry\CHsample\train\shp"
    # for shp in os.listdir(root):
    #     if shp.endswith('.shp'):
    #         path=os.path.join(root, shp)
    #         change_type(path)

    #测试单个方法
    # add_mean_value_field(r"Z:\zYX\1\wu\yuyi\2022bishanqu_clip61.tif",
    #                      r"Z:\zYX\1\wu\bianyuan\2022bishanqu_clip61_poly.shp",
    #                      r"Z:\zYX\1\wu\bianyuan\2022out.shp")

    # add_phase_raster(r"Z:\lry\chongqing\重庆phase1\phase.tif",
    #                  r"D:\chongqingxiangmu\DK_merge 11.8\p0865000129_copy.shp",
    #                  r"D:\chongqingxiangmu\DK_merge 11.8\p0865000129_copy.shp")

    # add_mean_prob(r"Z:\lry\chongqing\20_test\11\image\500051\500051_prob.tif",
    #               r"Z:\lry\chongqing\20_test\shp\p0865000051.shp",
    #               r"Z:\lry\chongqing\20_test\shp\p0865000051.shp")
    #
    # json2shpField(r"Z:\lry\chongqing\20_test\output\p0865000051.json",
    #               r"Z:\lry\chongqing\20_test\p0865000051.shp",
    #               r"Z:\lry\chongqing\20_test\p0865000051.shp")

    # 批量赋值
    # img_path = r"D:\chongqingxiangmu\03_partitons_images"
    # shp_path = r"Z:\lry\chongqing\20_test\DK_merge 11.8"
    # out_path = r"E:\data\ch\DK"
    # prob_path=r"Z:\lry\chongqing\20_test\class_prob"
    # json_path = r"E:\data\ch\json"
    # output_json_path = r"E:\data\ch\output_json2"
    # for i in range(500100, 500101):
    #     root = os.path.join(img_path, str(i))
    #     for filename in os.listdir(root):
    #         if filename.endswith('_classes.tif'):
    #             classes_img = os.path.join(root, filename)
    #             print("当前进度:", classes_img)
    #             num = filename[3:6]
    #             shp_ = os.path.join(shp_path, 'p0865000' + num + '.shp')
    #             out_ = os.path.join(out_path, 'p0865000' + num + '.shp')
    #             out_final = os.path.join(out_path, 'p0865000' + num + '_final.shp')
    #             prob_ = os.path.join(root, filename[:6] + '_prob.tif')
    #             json_ = os.path.join(json_path, 'p0865000' + num + '.json')
    #             output_json = os.path.join(output_json_path, 'p0865000' + num + '.json')
    #
    #             if not os.path.exists(out_):
    #                 add_mean_value_field(classes_img, shp_, out_)
    #                 add_phase_raster(r"Z:\lry\chongqing\重庆phase1\phase.tif", out_, out_)
    #                 add_mean_prob(prob_, out_, out_)
    #             if not os.path.exists(json_):
    #                 shpType2json(out_, json_)
    #             if os.path.exists(output_json):
    #                 json2shpField(output_json, out_, out_final)


    # 删除多余的列
    # duplicate(r"E:\data\ch\DK\p0865000419.shp", r"E:\data\ch\DK\p0865000419_copy.shp")

    #测试转json
    # shpType2json(r"E:\data\ch\DK_SAR\p0865000100.shp", r"E:\data\ch\json2\p0865000100.json")

    # 测试合并时序数据
    # compose_time(r"E:\data\ch\DK\p0865000001.shp",
    #              r"E:\data\ch\SAR作物结果\SAR作物结果\p0865000001.shp",
    #              r"E:\data\ch\DK\p0865000001_copy.shp")

    #测试按月份写入shp
    # json2shpField2(r"E:\data\ch\output_json2\p0865000001.json",
    #                r"E:\data\ch\DK_SAR\p0865000100 - 副本.shp")

    #测试替换中文
    # duplicate(r"E:\data\ch\DK_SAR\p0865000001 - 副本.shp",
    #           r"E:\data\ch\DK_SAR\p0865000001 - 副本.shp")

    # 合并时序数据
    # root=r"E:\data\ch\DK"
    # SAR_path=r"E:\data\ch\SAR作物结果\SAR作物结果"
    # output_path=r"E:\data\ch\DK_SAR"
    # json_path=r"E:\data\ch\output_0113"
    # for i in range(5000198, 5000459):
    #     shp_name='p086'+str(i)+'.shp'
    #     print(shp_name)
    #     json_name=shp_name[:-4]+'.json'
    #     # compose_time(os.path.join(root, file),
    #     #              os.path.join(SAR_path, file),
    #     #              os.path.join(output_path, out_name))
    #
    #     # shpType2json(os.path.join(output_path, out_name),
    #     #              os.path.join(json_path, json_name))
    #
    #     #时序作物输出到矢量
    #     json2shpField2(os.path.join(json_path, json_name),
    #                    os.path.join(output_path, shp_name))

        #替换中文
        # duplicate(os.path.join(output_path, out_name),
        #           os.path.join(output_path, out_name))

    caculate_xiangzhen(r"C:\Users\lry\Desktop\regionres\regionres.shp",
                       r"C:\Users\lry\Desktop\calcres\calcres.shp")