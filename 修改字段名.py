# -*- coding: utf-8 -*-
# python3
import logging
import os,argparse
from osgeo import ogr
from tqdm import tqdm

# parser = argparse.ArgumentParser()
# parser.add_argument('-i','--indir',default='None',type=str,help='input dir')
# parser.add_argument('-o','--old_field',default='[]',type=str,help='old field list,input[]')
# parser.add_argument('-n','--new_field',default='[]',type=str,help='new field list,input[]')
#
# args = parser.parse_args()
# indir = args.indir
# old_field = eval(args.old_field)
# new_field = eval(args.new_field)

indir = r"E:\data\ch\DK_SAR"
old_field = ['crop_2101', 'crop_2102', 'crop_2103', 'crop_2104', 'crop_2105',
             'crop_2106', 'crop_2107', 'crop_2108', 'crop_2109', 'crop_2110',
             'crop_2111', 'crop_2112']
# new_field = ['crop_r01', 'crop_r02', 'crop_r03', 'crop_r04', 'crop_r05',
#              'crop_r06', 'crop_r07', 'crop_r08', 'crop_r09', 'crop_r10',
#              'crop_r11', 'crop_r12',
#              'crop_l07', 'crop_l08', 'crop_l09', 'crop_l10', 'crop_l11',
#              'crop_l12', 'crop_n01', 'crop_n02', 'crop_n03', 'crop_n04',
#              'crop_n05', 'crop_n06']

new_field=['cm_l07', 'cm_l08', 'cm_l09', 'cm_l10', 'cm_l11',
           'cm_l12', 'cm_r01', 'cm_r02', 'cm_r03', 'cm_r04',
           'cm_r05', 'cm_r06', 'cm_r07', 'cm_r08', 'cm_r09',
           'cm_r10', 'cm_r11', 'cm_r12', 'cm_n01', 'cm_n02',
           'cm_n03', 'cm_n04', 'cm_n05', 'cm_n06']


def create_field(layer, field_name):
    fieldIndex = layer.GetLayerDefn().GetFieldIndex(field_name)
    if fieldIndex < 0:
        # 添加字段
        fieldDefn = ogr.FieldDefn(field_name, ogr.OFTString)  # 添加字段名及设置其类型,Real为字符串
        fieldDefn.SetWidth(10)  # 字符串设定宽度
        layer.CreateField(fieldDefn, 1)
        if fieldIndex > 0:
            print("字段创建成功：", field_name)
    else:
        print(field_name + "字段已存在，无需创建！")

if __name__ == '__main__':

    inlist = []
    # for root,dirs,files in os.walk(indir):
    #     for shp in files:
    #         if shp.endswith(".shp"):
    #             inlist.append(os.path.join(root,shp))
    for file in os.listdir(indir):
        if file.endswith(".shp"):
                    inlist.append(os.path.join(indir, file))

    for inshp in tqdm(inlist):
        try:
            ds = ogr.Open(inshp,1)
            layer = ds.GetLayer(0)
            layerdef = layer.GetLayerDefn()
            for i in range(len(new_field)):
                create_field(layer, new_field[i])
                # if i >= 12:
                #     create_field(layer, new_field[i])
                # else:
                #     index = layerdef.GetFieldIndex(old_field[i])
                #     defn = layerdef.GetFieldDefn(index)
                #     fld_defn = ogr.FieldDefn(new_field[i], defn.GetType())
                #     layer.AlterFieldDefn(index, fld_defn, ogr.ALTER_NAME_FLAG)
            ds = None
        except:
            print(inshp)
            continue
