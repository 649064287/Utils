
import sys
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import jinja2
import pandas as pd
from win32com import client as wc
import ogr
import gdal


def round_2(num):
    return '%.2f' % round(float(str(num)[1:-1]), 2)

def read_shp(fn):
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
    gdal.SetConfigOption("SHAPE_ENCODING", "GBK")
    SYHY_WZ_ = []
    SYHY_JZ_ = []
    TRBC_WZ_ = []
    TRBC_JZ_ = []
    HSTX_WZ_ = []
    HSTX_JZ_ = []
    GT_WZ_ = []
    GT_JZ_ = []
    SY_WZ_ = []
    SY_JZ_ = []
    QHTJ_WZ_ = []
    QHTJ_JZ_ = []
    KQJH_WZ_ = []
    KQJH_JZ_ = []
    SHJJH_WZ_ = []
    SHJJH_JZ_ = []
    FYLZ_WZ_ = []
    FYLZ_JZ_ = []
    TJFW_JZ_ = []
    NONG_JZ_ = []
    LING_JZ_ = []
    MU_JZ_ = []
    YU_JZ_ = []
    GONGJI_JZ_ = []
    ZLDWMC_ = []
    area_ = []

    ds = ogr.Open(fn, 0)
    if ds is None:
        sys.exit('Could not open {0}.'.format(fn))
    lyr = ds.GetLayer(0)
    for feat in lyr:
        SYHY_WZ = feat.GetField('SYHY_WZ')
        SYHY_JZ = feat.GetField('SYHY_JZ')
        TRBC_WZ = feat.GetField('TRBC_WZ')
        TRBC_JZ = feat.GetField('TRBC_JZ')
        HSTX_WZ = feat.GetField('HSTX_WZ')
        HSTX_JZ = feat.GetField('HSTX_JZ')
        GT_WZ = feat.GetField('GT_WZ')
        GT_JZ = feat.GetField('GT_JZ')
        SY_WZ = feat.GetField('SY_WZ')
        SY_JZ = feat.GetField('SY_JZ')
        QHTJ_WZ = feat.GetField('QHTJ_WZ')
        QHTJ_JZ = feat.GetField('QHTJ_JZ')
        KQJH_WZ = feat.GetField('KQJH_WZ')
        KQJH_JZ = feat.GetField('KQJH_JZ')
        SHJJH_WZ = feat.GetField('SHJJH_WZ')
        SHJJH_JZ = feat.GetField('SHJJH_JZ')
        FYLZ_WZ = feat.GetField('FYLZ_WZ')
        FYLZ_JZ = feat.GetField('FYLZ_JZ')
        TJFW_JZ = feat.GetField('TJFW_JZ')
        NONG_JZ = feat.GetField('NONG_JZ')
        LING_JZ = feat.GetField('LING_JZ')
        MU_JZ = feat.GetField('MU_JZ')
        YU_JZ = feat.GetField('YU_JZ')
        GONGJI_JZ = feat.GetField('GONGJI_JZ')
        ZLDWMC = feat.GetField('ZLDWMC')
        area = feat.GetField('area')

        SYHY_WZ_.append(SYHY_WZ)
        SYHY_JZ_.append(SYHY_JZ)
        TRBC_WZ_.append(TRBC_WZ)
        TRBC_JZ_.append(TRBC_JZ)
        HSTX_WZ_.append(HSTX_WZ)
        HSTX_JZ_.append(HSTX_JZ)
        GT_WZ_.append(GT_WZ)
        GT_JZ_.append(GT_JZ)
        SY_WZ_.append(SY_WZ)
        SY_JZ_.append(SY_JZ)
        QHTJ_WZ_.append(QHTJ_WZ)
        QHTJ_JZ_.append(QHTJ_JZ)
        KQJH_WZ_.append(KQJH_WZ)
        KQJH_JZ_.append(KQJH_JZ)
        SHJJH_WZ_.append(SHJJH_WZ)
        SHJJH_JZ_.append(SHJJH_JZ)
        FYLZ_WZ_.append(FYLZ_WZ)
        FYLZ_JZ_.append(FYLZ_JZ)
        TJFW_JZ_.append(TJFW_JZ)
        NONG_JZ_.append(NONG_JZ)
        LING_JZ_.append(LING_JZ)
        MU_JZ_.append(MU_JZ)
        YU_JZ_.append(YU_JZ)
        GONGJI_JZ_.append(GONGJI_JZ)
        ZLDWMC_.append(ZLDWMC)
        area_.append(area)

    data = {
        'SYHY_WZ_':SYHY_WZ_,
        'SYHY_JZ_':SYHY_JZ_,
        'TRBC_WZ_':TRBC_WZ_,
        'TRBC_JZ_':TRBC_JZ_,
        'HSTX_WZ_':HSTX_WZ_,
        'HSTX_JZ_':HSTX_JZ_,
        'GT_WZ_':GT_WZ_,
        'GT_JZ_':GT_JZ_,
        'SY_WZ_':SY_WZ_,
        'SY_JZ_':SY_JZ_,
        'QHTJ_WZ_':QHTJ_WZ_,
        'QHTJ_JZ_':QHTJ_JZ_,
        'KQJH_WZ_':KQJH_WZ_,
        'KQJH_JZ_':KQJH_JZ_,
        'SHJJH_WZ_':SHJJH_WZ_,
        'SHJJH_JZ_':SHJJH_JZ_,
        'FYLZ_WZ_':FYLZ_WZ_,
        'FYLZ_JZ_':FYLZ_JZ_,
        'TJFW_JZ_':TJFW_JZ_,
        'NONG_JZ_':NONG_JZ_,
        'LING_JZ_':LING_JZ_,
        'MU_JZ_':MU_JZ_,
        'YU_JZ_':YU_JZ_,
        'GONGJI_JZ_':GONGJI_JZ_,
        'ZLDWMC_':ZLDWMC_,
        'area_': area_,
    }

    df = pd.DataFrame(data)
    # 计算单位价值
    df['syhy_dw_'] = df['SYHY_WZ_'] / df['area_']
    df['trbc_dw_'] = df['TRBC_WZ_'] / df['area_']
    df['hstx_dw_'] = df['HSTX_WZ_'] / df['area_']
    df['shjjh_dw_'] = df['SHJJH_WZ_'] / df['area_']
    df['kqjh_dw_'] = df['KQJH_WZ_'] / df['area_']
    df['gt_dw_'] = df['GT_WZ_'] / df['area_']
    df['sy_dw_'] = df['SY_WZ_'] / df['area_']
    df['qhtj_dw_'] = df['QHTJ_WZ_'] / df['area_']
    df['fylz_dw_'] = df['FYLZ_WZ_'] / df['area_']

    # 按总值排序
    df_syhy = df.sort_values(by=['SYHY_WZ_'], ascending=[False]).reset_index(drop=True)
    df_trbc = df.sort_values(by=['TRBC_WZ_'], ascending=[False]).reset_index(drop=True)
    df_hstx = df.sort_values(by=['HSTX_WZ_'], ascending=[False]).reset_index(drop=True)
    df_shjjh = df.sort_values(by=['SHJJH_WZ_'], ascending=[False]).reset_index(drop=True)
    df_kqjh = df.sort_values(by=['KQJH_WZ_'], ascending=[False]).reset_index(drop=True)
    df_gt = df.sort_values(by=['GT_WZ_'], ascending=[False]).reset_index(drop=True)
    df_sy = df.sort_values(by=['SY_WZ_'], ascending=[False]).reset_index(drop=True)
    df_qhtj = df.sort_values(by=['QHTJ_WZ_'], ascending=[False]).reset_index(drop=True)
    df_fylz = df.sort_values(by=['FYLZ_WZ_'], ascending=[False]).reset_index(drop=True)
    # df_wzby = df.sort_values(by=['_WZ_'], ascending=[False])

    syhy_1 = df_syhy.loc[[0], 'ZLDWMC_'].values
    syhy_1_gnl = df_syhy.loc[[0], 'SYHY_WZ_'].values
    syhy_1_jz = df_syhy.loc[[0], 'SYHY_JZ_'].values
    syhy_2 = df_syhy.loc[[1], 'ZLDWMC_'].values
    syhy_2_gnl = df_syhy.loc[[1], 'SYHY_WZ_'].values
    syhy_2_jz = df_syhy.loc[[1], 'SYHY_JZ_'].values
    syhy_1 = str(syhy_1)[2:-2]
    syhy_1_gnl = round_2(syhy_1_gnl)
    syhy_1_jz = round_2(syhy_1_jz)
    syhy_2 = str(syhy_2)[2:-2]
    syhy_2_gnl = round_2(syhy_2_gnl)
    syhy_2_jz = round_2(syhy_2_jz)

    trbc_1 = df_trbc.loc[[0], 'ZLDWMC_'].values
    trbc_1_gnl = df_trbc.loc[[0], 'TRBC_WZ_'].values
    trbc_1_jz = df_trbc.loc[[0], 'TRBC_JZ_'].values
    trbc_2 = df_trbc.loc[[1], 'ZLDWMC_'].values
    trbc_2_gnl = df_trbc.loc[[1], 'TRBC_WZ_'].values
    trbc_2_jz = df_trbc.loc[[1], 'TRBC_JZ_'].values
    trbc_1 = str(trbc_1)[2:-2]
    trbc_1_gnl = round_2(trbc_1_gnl)
    trbc_1_jz = round_2(trbc_1_jz)
    trbc_2 = str(trbc_2)[2:-2]
    trbc_2_gnl = round_2(trbc_2_gnl)
    trbc_2_jz = round_2(trbc_2_jz)

    # 按单位价值排序
    df_syhy_dw = df.sort_values(by=['syhy_dw_'], ascending=[False]).reset_index(drop=True)
    df_trbc_dw = df.sort_values(by=['trbc_dw_'], ascending=[False]).reset_index(drop=True)
    df_hstx_dw = df.sort_values(by=['hstx_dw_'], ascending=[False]).reset_index(drop=True)
    df_shjjh_dw = df.sort_values(by=['shjjh_dw_'], ascending=[False]).reset_index(drop=True)
    df_kqjh_dw = df.sort_values(by=['kqjh_dw_'], ascending=[False]).reset_index(drop=True)
    df_gt_dw = df.sort_values(by=['gt_dw_'], ascending=[False]).reset_index(drop=True)
    df_sy_dw = df.sort_values(by=['sy_dw_'], ascending=[False]).reset_index(drop=True)
    df_qhtj_dw = df.sort_values(by=['qhtj_dw_'], ascending=[False]).reset_index(drop=True)
    df_fylz_dw = df.sort_values(by=['fylz_dw_'], ascending=[False]).reset_index(drop=True)

    syhy_1_dw = df_syhy_dw.loc[[0], 'ZLDWMC_'].values
    syhy_1_dw_jz = df_syhy_dw.loc[[0], 'syhy_dw_'].values
    syhy_2_dw = df_syhy_dw.loc[[1], 'ZLDWMC_'].values
    syhy_2_dw_jz = df_syhy_dw.loc[[1], 'syhy_dw_'].values
    syhy_last_dw = df_syhy_dw.loc[[16], 'ZLDWMC_'].values
    syhy_last_dw_jz = df_syhy_dw.loc[[16], 'syhy_dw_'].values
    syhy_1_dw = str(syhy_1_dw)[2:-2]
    syhy_1_dw_jz = round_2(syhy_1_dw_jz)
    syhy_2_dw = str(syhy_2_dw)[2:-2]
    syhy_2_dw_jz = round_2(syhy_2_dw_jz)
    syhy_last_dw = str(syhy_last_dw)[2:-2]
    syhy_last_dw_jz = round_2(syhy_last_dw_jz)



    zhen = {
        'syhy_1':syhy_1,
        'syhy_1_gnl':syhy_1_gnl,
        'syhy_1_jz':syhy_1_jz,
        'syhy_2':syhy_2,
        'syhy_2_gnl':syhy_2_gnl,
        'syhy_2_jz':syhy_2_jz,

        'syhy_1_dw':syhy_1_dw,
        'syhy_1_dw_jz':syhy_1_dw_jz,
        'syhy_2_dw':syhy_2_dw,
        'syhy_2_dw_jz':syhy_2_dw_jz,
        'syhy_last_dw':syhy_last_dw,
        'syhy_last_dw_jz':syhy_last_dw_jz,
    }
    return zhen


def get_item(sm):
    # 水源涵养
    syhy_gnl = sm.loc[[0], '功能量'].values
    syhy_jz = sm.loc[[0], '可比价值量/亿元'].values
    syhy_bl = sm.loc[[0], '占调节比/%'].values
    syhy_gnl = round_2(syhy_gnl)
    syhy_jz = round_2(syhy_jz)
    syhy_bl = round_2(syhy_bl)

    # 土壤保持
    trbc_gnl = sm.loc[[1], '功能量'].values
    trbc_jz = sm.loc[[1], '可比价值量/亿元'].values
    trbc_bl = sm.loc[[1], '占调节比/%'].values
    trbc_gnl = round_2(trbc_gnl)
    trbc_jz = round_2(trbc_jz)
    trbc_bl = round_2(trbc_bl)

    # 洪水调蓄
    hstx_gnl = sm.loc[[4], '功能量'].values
    hstx_jz = sm.loc[[4], '可比价值量/亿元'].values
    hstx_bl = sm.loc[[4], '占总比/%'].values
    hstx_gnl = round_2(hstx_gnl)
    hstx_jz = round_2(hstx_jz)
    hstx_bl = round_2(hstx_bl)

    # 水体净化
    COD_gnl = sm.loc[[5], '功能量'].values
    COD_jz = sm.loc[[5], '可比价值量/亿元'].values
    ad_gnl = sm.loc[[6], '功能量'].values
    ad_jz = sm.loc[[6], '可比价值量/亿元'].values
    zl_gnl = sm.loc[[7], '功能量'].values
    zl_jz = sm.loc[[7], '可比价值量/亿元'].values
    stjh_jz = sm.loc[[8], '可比价值量/亿元'].values
    stjh_bl = sm.loc[[8], '占调节比/%'].values
    COD_gnl = round_2(COD_gnl)
    COD_jz = round_2(COD_jz)
    ad_gnl = round_2(ad_gnl)
    ad_jz = round_2(ad_jz)
    zl_gnl = round_2(zl_gnl)
    zl_jz = round_2(zl_jz)
    stjh_jz = round_2(stjh_jz)
    stjh_bl = round_2(stjh_bl)

    # 空气净化
    eyhl_gnl = sm.loc[[9], '功能量'].values
    eyhl_jz = sm.loc[[9], '可比价值量/亿元'].values
    dyhw_gnl = sm.loc[[10], '功能量'].values
    dyhw_jz = sm.loc[[10], '可比价值量/亿元'].values
    kqjh_jz = sm.loc[[11], '可比价值量/亿元'].values
    kqjh_bl = sm.loc[[11], '占调节比/%'].values
    eyhl_gnl = round_2(eyhl_gnl)
    eyhl_jz = round_2(eyhl_jz)
    dyhw_gnl = round_2(dyhw_gnl)
    dyhw_jz = round_2(dyhw_jz)
    kqjh_jz = round_2(kqjh_jz)
    kqjh_bl = round_2(kqjh_bl)

    # 固碳
    gt_gnl = sm.loc[[12], '功能量'].values
    gt_jz = sm.loc[[12], '可比价值量/亿元'].values
    gt_bl = sm.loc[[12], '占总比/%'].values
    gt_gnl = round_2(gt_gnl)
    gt_jz = round_2(gt_jz)
    gt_bl = round_2(gt_bl)

    # 释氧
    sy_gnl = sm.loc[[13], '功能量'].values
    sy_jz = sm.loc[[13], '可比价值量/亿元'].values
    sy_bl = sm.loc[[13], '占总比/%'].values
    sy_gnl = round_2(sy_gnl)
    sy_jz = round_2(sy_jz)
    sy_bl = round_2(sy_bl)

    # 气候调节
    qhtj_zb_gnl = sm.loc[[14], '功能量'].values
    qhtj_sm_gnl = sm.loc[[15], '功能量'].values
    qhtj_zb_jz = sm.loc[[14], '可比价值量/亿元'].values
    qhtj_sm_jz = sm.loc[[15], '可比价值量/亿元'].values
    qhtj_gnl = sm.loc[[16], '功能量'].values
    qhtj_jz = sm.loc[[16], '可比价值量/亿元'].values
    qhtj_bl = sm.loc[[16], '占调节比/%'].values
    qhtj_zb_gnl = round_2(qhtj_zb_gnl)
    qhtj_sm_gnl = round_2(qhtj_sm_gnl)
    qhtj_zb_jz = round_2(qhtj_zb_jz)
    qhtj_sm_jz = round_2(qhtj_sm_jz)
    qhtj_gnl = round_2(qhtj_gnl)
    qhtj_jz = round_2(qhtj_jz)
    qhtj_bl = round_2(qhtj_bl)

    # 负氧离子
    fylz_gnl = sm.loc[[17], '功能量'].values
    fylz_jz = sm.loc[[17], '可比价值量/亿元'].values
    fylz_bl = sm.loc[[17], '占调节比/%'].values
    fylz_gnl = round_2(fylz_gnl)
    fylz_jz = round_2(fylz_jz)
    fylz_bl = round_2(fylz_bl)

    # 调节服务
    tjfw_jz = sm.loc[[18], '可比价值量/亿元'].values
    tjfw_jz = round_2(tjfw_jz)

    # 供给产品

    # 文化服务

    dic = {
        'year': 2020,
        'country': '婺源县',
        'syhy_gnl': syhy_gnl,
        'syhy_jz': syhy_jz,
        'syhy_bl': syhy_bl,
        'trbc_gnl': trbc_gnl,
        'trbc_jz': trbc_jz,
        'trbc_bl': trbc_bl,
        'hstx_gnl': hstx_gnl,
        'hstx_jz': hstx_jz,
        'hstx_bl': hstx_bl,
        'stjh_jz': stjh_jz,
        'stjh_bl': stjh_bl,
        'COD_gnl': COD_gnl,
        'COD_jz': COD_jz,
        'ad_gnl': ad_gnl,
        'ad_jz': ad_jz,
        'zl_gnl': zl_gnl,
        'zl_jz': zl_jz,
        'kqjh_jz': kqjh_jz,
        'kqjh_bl': kqjh_bl,
        'eyhl_gnl': eyhl_gnl,
        'eyhl_jz': eyhl_jz,
        'dyhw_gnl': dyhw_gnl,
        'dyhw_jz': dyhw_jz,
        'gt_gnl': gt_gnl,
        'gt_jz': gt_jz,
        'gt_bl': gt_bl,
        'sy_gnl': sy_gnl,
        'sy_jz': sy_jz,
        'sy_bl': sy_bl,
        'qhtj_zb_gnl': qhtj_zb_gnl,
        'qhtj_sm_gnl': qhtj_sm_gnl,
        'qhtj_zb_jz': qhtj_zb_jz,
        'qhtj_sm_jz': qhtj_sm_jz,
        'qhtj_gnl': qhtj_gnl,
        'qhtj_jz': qhtj_jz,
        'qhtj_bl': qhtj_bl,
        'fylz_gnl': fylz_gnl,
        'fylz_jz': fylz_jz,
        'fylz_bl': fylz_bl,
        'tjfw_jz': tjfw_jz,
    }

    return dic

def inline_image(tpl, path):
    return InlineImage(tpl, path, width=Mm(150.6), height=Mm(85.4))

def get_pic(tpl):
    context = {
        'tjfw_jz_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇单位面积调节服务价值量统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'fylz_jz_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇单位面积负氧离子价值量统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'gt_jz_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇单位面积固碳价值量统计图.png',
                                 width=Mm(150.6), height=Mm(85.4)),
        'kqjh_jz_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇单位面积空气净化价值量统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'qhtj_jz_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇单位面积气候调节价值量统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'sy_jz_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇单位面积释氧价值量统计图.png',
                                 width=Mm(150.6), height=Mm(85.4)),
        'stjh_jz_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇单位面积水环境净化价值量统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'syhy_jz_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇单位面积水源涵养价值量统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'trbc_jz_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇单位面积土壤保持价值量统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'hstx_jz_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇单位面积植被洪水调蓄价值量统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'tjfw_gn_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇调节服务统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'fylz_gn_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇负氧离子统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'gt_gn_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇固碳统计图.png', width=Mm(150.6),
                                 height=Mm(85.4)),
        'kqjh_gn_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇空气净化统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'qhtj_gn_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇气候调节统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'sy_gn_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇释氧统计图.png', width=Mm(150.6),
                                 height=Mm(85.4)),
        'stjh_gn_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇水环境净化统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'syhy_gn_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇水源涵养统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'trbc_gn_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇土壤保持统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
        'hstx_gn_img': InlineImage(tpl, r'C:\Users\64906\Documents\乡镇_new\乡镇_new\2020年婺源县乡镇植被洪水调蓄统计图.png',
                                   width=Mm(150.6), height=Mm(85.4)),
    }
    return context


def replace_item(in_path, dic, zhen, out_path):
    dic.update(zhen)
    tpl = DocxTemplate(in_path)
    tpl.render(dic)
    tpl.save(out_path)


def replace_pic(in_path, out_path):
    tpl = DocxTemplate(in_path)
    pic = get_pic(tpl)
    tpl.render(pic)
    tpl.save(out_path)


def doSaveAas(doc_path):
    """
    将doc文档转换为docx文档
    :rtype: object
    """
    docx_path = doc_path.replace("doc", "docx")
    word = wc.Dispatch('Word.Application')
    doc = word.Documents.Open(doc_path)  # 目标路径下的文件
    doc.SaveAs(docx_path, 12, False, "", True, "", False, False, False, False)  # 转化后路径下的文件
    doc.Close()
    word.Quit()




if __name__ == '__main__':
    in_path = r'C:\Users\64906\Desktop\2020年上栗县GEP精算报告_20211020.docx'
    out_path = r'C:\Users\64906\Desktop\2020_out.docx'
    wy = pd.read_excel(r'C:\Users\64906\Documents\乡镇_new\乡镇_new\婺源县2020年GEP核算表.xlsx')
    shp = r'C:\Users\64906\Documents\乡镇_new\乡镇_new\regionres.shp'
    # docx = r'C:\Users\64906\Desktop\2020年上栗县GEP精算报告_20211020.doc'

    # doSaveAas(docx)
    item = get_item(wy)
    zhen = read_shp(shp)
    replace_item(in_path, item, zhen, out_path)
    # replace_pic(in_path, out_path)
