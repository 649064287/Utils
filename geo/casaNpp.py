import os

from osgeo import gdal, osr
import math
import numpy as np
import cv2
import pandas as pd

from geo import solar
from geo.solar import get_solar

filename = r'D:\map_anji\2021\1\L1C_T50RQU_A029115_20210118T024029\composite\T50RQU_20210118T024031_ndvi.tif'


def get_FPAR(file_path, out=r'E:\map_anji&deqing\2021\test\FPAR\7_FPAR.tif'):
    for file in file_path:
        ndviDS = gdal.Open(file)
        img_width = ndviDS.RasterXSize
        img_height = ndviDS.RasterYSize
        data = ndviDS.GetRasterBand(1).ReadAsArray().astype(np.float32)
        data1 = data[data != -9999.0]

        maN = np.max(data1)
        miN = np.min(data1)
        # FPAR = (NDVI-NDVImin)*(FPARmax-FPARmin)/(NDVImax-NDVImin)+FPARmin
        FPAR_NDVI = (data - miN) * (0.95 - 0.001) / (maN - miN) + 0.001

        # SR = (1+NDVI)/(1-NDVI)
        SR = (1 + data) / (1 - data)
        maR = np.max(SR)
        miR = np.min(SR)
        # FPAR_SR = (SR-SRmin)*(FPARmax-FPARmin)/(SRmax-SRmin)+FPARmin
        FPAR_SR = (SR - miR) * (0.95 - 0.001) / (maR - miR) + 0.001

        FPAR = (FPAR_NDVI + FPAR_SR) / 2  ##植被层对入射光合有效辐射的吸收比例

        driver = gdal.GetDriverByName('GTiff')
        if out=='':
            out=file_path.rsplit('.',1)[0]+'_FPAR.tif'
        outRaster = driver.Create(out, img_width, img_height, 1, gdal.GDT_Float32)
        outband = outRaster.GetRasterBand(1)
        outband.WriteArray(FPAR)
        # outband.WriteArray(FPAR.reshape(img_height, img_width))
        # outband.SetNoDataValue(nodata)

        geoTrans = ndviDS.GetGeoTransform()
        outRaster.SetGeoTransform(geoTrans)
        outRaster.SetProjection(ndviDS.GetProjection())
        outband.FlushCache()


def optTem(filelist, MeanTemList):
    """
    按月份遍历NVDI：
        找到每个像素NVDI最大值
        找到每个像素最适温度（月平均温度）
    返回NDVI最大时最适温度
    :param filelist:
    :return:
    """
    ndviDS = gdal.Open(filelist[0])
    Narr = ndviDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    rows = ndviDS.RasterXSize
    cols = ndviDS.RasterYSize
    NDVImaxValue = Narr  ##先假定第一个月的NDVI是最大的，然后跟后面的对比，不断替换，找到最大值
    NDVImaxMonth = np.ones((rows, cols), int)
    NDVImaxMonthMeanTem = np.zeros((rows, cols))  ##定义最适温度数组
    for i in range(len(filelist)):  ##2001年的时候，i= 0时，代表的是1月
        ndviDS = gdal.Open(filelist[i])
        NDVIarr = ndviDS.GetRasterBand(1).ReadAsArray().astype(np.float)
        (dir1, name1) = os.path.split(filelist[i])
        yy, yymm = findYM(name1)
        for row in range(rows):
            for col in range(cols):
                if NDVImaxValue[row, col] >= NDVIarr[row, col]:
                    NDVImaxValue[row, col] = NDVImaxValue[row, col]  ## NDVImaxValue保持不变
                    NDVImaxMonth[row, col] = NDVImaxMonth[row, col]  ## NDVImaxMonth保持不变
                    # print(int(NDVImaxMonth[row,col]))
                    NDVImaxMonthMeanTem[row, col] = MeanTemList[int(NDVImaxMonth[row, col]) - 1]  ##最适温度
                    # print(NDVImaxMonthMeanTem[row, col])
                else:
                    NDVImaxValue[row, col] = NDVIarr[row, col]
                    NDVImaxMonth[row, col] = int(yymm[5:7])
                    NDVImaxMonthMeanTem[row, col] = MeanTemList[int(yymm[5:7]) - 1]  ##最适温度
    return NDVImaxMonthMeanTem


def getSRSPair(dataset):
    '''
    获得给定数据的投影参考系和地理参考系
    :param dataset: GDAL地理数据
    :return: 投影参考系和地理参考系
    '''
    prosrs = osr.SpatialReference()
    prosrs.ImportFromWkt(dataset.GetProjection())
    geosrs = prosrs.CloneGeogCS()
    return prosrs, geosrs


def geo2lonlat(ct, x, y):
    '''
    将投影坐标转为经纬度坐标（具体的投影坐标系由给定数据确定）
    :param dataset: GDAL地理数据
    :param x: 投影坐标x
    :param y: 投影坐标y
    :return: 投影坐标(x, y)对应的经纬度坐标(lon, lat)
    '''
    # prosrs, geosrs = getSRSPair(dataset)
    # ct = osr.CoordinateTransformation(prosrs, geosrs)
    coords = ct.TransformPoint(x, y)
    return coords[:2]


def lonlat2geo(ct, lon, lat):
    '''
    将经纬度坐标转为投影坐标（具体的投影坐标系由给定数据确定）
    :param dataset: GDAL地理数据
    :param lon: 地理坐标lon经度
    :param lat: 地理坐标lat纬度
    :return: 经纬度坐标(lon, lat)对应的投影坐标
    '''
    # prosrs, geosrs = getSRSPair(dataset)
    # ct = osr.CoordinateTransformation(geosrs, prosrs)
    coords = ct.TransformPoint(lon, lat)
    return coords[:2]


def imagexy2geo(trans, row, col):
    '''
    根据GDAL的六参数模型将影像图上坐标（行列号）转为投影坐标或地理坐标（根据具体数据的坐标系统转换）
    :param dataset: GDAL地理数据
    :param row: 像素的行号
    :param col: 像素的列号
    :return: 行列号(row, col)对应的投影坐标或地理坐标(x, y)
    '''
    # trans = dataset.GetGeoTransform()
    px = trans[0] + col * trans[1] + row * trans[2]
    py = trans[3] + col * trans[4] + row * trans[5]
    return px, py


def geo2imagexy(dataset, x, y):
    '''
    根据GDAL的六 参数模型将给定的投影或地理坐标转为影像图上坐标（行列号）
    :param dataset: GDAL地理数据
    :param x: 投影或地理坐标x
    :param y: 投影或地理坐标y
    :return: 影坐标或地理坐标(x, y)对应的影像图上行列号(row, col)
    '''
    trans = dataset.GetGeoTransform()
    a = np.array([[trans[1], trans[2]], [trans[4], trans[5]]])
    b = np.array([x - trans[0], y - trans[3]])
    return np.linalg.solve(a, b)  # 使用numpy的linalg.solve进行二元一次方程的求解

def srs2imagexy(srs_trans, new_trans, row, col, ct_srs, ct_new):
    # srs像素转投影坐标
    geox_srs, geoy_srs = imagexy2geo(srs_trans, row, col)
    #srs投影转经纬
    coords = geo2lonlat(ct_srs, geox_srs, geoy_srs)
    #经纬转new投影
    geo_new = lonlat2geo(ct_new, coords[0], coords[1])

    imgX = (int)((geo_new[0] - new_trans[0]) // new_trans[1])
    imgY = (int)((geo_new[1] - new_trans[3]) // new_trans[5])
    imgX = int(imgX)
    imgY = int(imgY)
    return imgX, imgY

def srs2imagexy2(srsDS, newDS, row, col):
    # srs像素转投影坐标
    px_srs, py_srs = imagexy2geo(srsDS, row, col)
    # srs投影转经纬
    coords_srs = geo2lonlat(srsDS, px_srs, py_srs)
    # srs经纬转ndvi投影
    geotrans_nvdi = lonlat2geo(newDS, coords_srs[0], coords_srs[1])
    # nvdi投影转像素
    imgX, imgY = geo2imagexy(newDS, geotrans_nvdi[0], geotrans_nvdi[1])
    imgX = int(imgX)
    imgY = int(imgY)
    return imgX, imgY


def optTem2(filelist, MeanTemList, out=r'E:\map_anji&deqing\2021\test\topt\NDVImaxMonthMeanTem.tif'):
    """
    按月份遍历NVDI：
        找到每个像素NVDI最大值
        找到每个像素最适温度（当月平均温度）
    返回NDVI最大时最适温度
    :param filelist: 十二个月份的NVDI
    :param MeanTemList:十二个月份的平均气温
    :return:
    """

    srsDS = gdal.Open(filelist[0])
    srs_row = srsDS.RasterYSize  # 行->高
    srs_col = srsDS.RasterXSize  # 列->宽
    prosrs, geosrs = getSRSPair(srsDS)
    ct_srs = osr.CoordinateTransformation(prosrs, geosrs)#投影转经纬
    geotransSRS = srsDS.GetGeoTransform()  # 地理参考系坐标
    Narr = srsDS.GetRasterBand(1).ReadAsArray().astype(np.float)

    NDVImaxValue = Narr  ##先假定第一个月的NDVI是最大的，然后跟后面的对比，不断替换，找到最大值
    NDVImaxMonth = np.ones((srs_row, srs_col), int)
    NDVImaxMonthMeanTem = np.zeros((srs_row, srs_col))  ##定义最适温度数组

    print(len(filelist))
    for i in range(len(filelist)):  ##2001年的时候，i= 0时，代表的是1月
        # NDVI
        ndviDS = gdal.Open(filelist[i])
        nvdi_row = ndviDS.RasterYSize
        nvdi_col = ndviDS.RasterXSize
        proNvdi, geoNvdi = getSRSPair(ndviDS)
        ct_nvdi = osr.CoordinateTransformation(geoNvdi, proNvdi)# 经纬转投影
        geotransNdvi = ndviDS.GetGeoTransform()  # 地理参考系坐标
        NDVIarr = ndviDS.GetRasterBand(1).ReadAsArray().astype(np.float)

        JanMeanTemDS = gdal.Open(MeanTemList[0])
        JanMeanTem_row = JanMeanTemDS.RasterYSize
        JanMeanTem_col = JanMeanTemDS.RasterXSize
        JanMeanTemTrans = JanMeanTemDS.GetGeoTransform()
        proJanMeanTem, geoJanMeanTem = getSRSPair(JanMeanTemDS)
        ct_JanMeanTem = osr.CoordinateTransformation(geoJanMeanTem, proJanMeanTem)
        JanMeanTemArr = JanMeanTemDS.GetRasterBand(1).ReadAsArray().astype(np.float)

        # tem
        MeanTemDS = gdal.Open(MeanTemList[i])
        MeanTem_row = MeanTemDS.RasterYSize
        MeanTem_col = MeanTemDS.RasterXSize
        proMeanTem, geoMeanTem = getSRSPair(MeanTemDS)
        ct_MeanTem = osr.CoordinateTransformation(geoMeanTem, proMeanTem)
        geotransMeanTem = MeanTemDS.GetGeoTransform()  # 地理参考系坐标
        MeanTemarr = MeanTemDS.GetRasterBand(1).ReadAsArray().astype(np.float)

        (dir1, name1) = os.path.split(MeanTemList[i])
        yy = name1[-6:-4]
        for col in range(srs_col):
            for row in range(srs_row):
                try:
                    imgX, imgY = srs2imagexy(geotransSRS, geotransNdvi, row, col, ct_srs, ct_nvdi) #nvdi像素坐标

                    if imgX > srs_col - 1 or imgX < 0 or imgY < 0 or imgY > srs_row - 1:
                        print('nvdi data not pair!')
                        continue
                    if NDVImaxValue[row, col] >= NDVIarr[imgY, imgX]:
                        NDVImaxValue[row, col] = NDVImaxValue[row, col]  ## NDVImaxValue保持不变
                        NDVImaxMonth[row, col] = NDVImaxMonth[row, col]  ## NDVImaxMonth保持不变
                        # print(int(NDVImaxMonth[row, col]))

                        JanX, JanY = srs2imagexy(geotransSRS, JanMeanTemTrans, row, col, ct_srs, ct_JanMeanTem)

                        if JanX > JanMeanTem_col - 1 or JanX < 0 or JanY < 0 or JanY > JanMeanTem_row - 1:
                            print('temp data not pair!')
                            continue
                        NDVImaxMonthMeanTem[row, col] = JanMeanTemArr[JanY, JanX]  ##一月温度作为最适温度
                        print(NDVImaxMonthMeanTem[row, col])
                    else:
                        NDVImaxValue[row, col] = NDVIarr[imgY, imgX]
                        NDVImaxMonth[row, col] = int(yy)  # 每个像素点的月份

                        imgX_tem, imgY_tem = srs2imagexy(geotransSRS, geotransMeanTem, row, col, ct_srs, ct_MeanTem)

                        if imgX_tem > MeanTem_col - 1 or imgX_tem < 0 or imgY_tem < 0 or imgY_tem > MeanTem_row - 1:
                            print('temp data not pair!')
                            continue
                        NDVImaxMonthMeanTem[row, col] = MeanTemarr[imgY_tem, imgX_tem]  ##当月温度作为最适温度
                        print("change")
                        print(int(NDVImaxMonth[row, col]))
                        print(NDVImaxMonthMeanTem[row, col])
                except IndexError:
                    print(IndexError)
                    continue

    driver = gdal.GetDriverByName('GTiff')
    # out = filelist[0].rsplit('.', 1)[0] + '_NDVImaxMonthMeanTem.tif'
    outRaster = driver.Create(out, srs_col, srs_row, 1, gdal.GDT_Float32)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(NDVImaxMonthMeanTem)
    # outband.SetNoDataValue(nodata)

    geoTrans = srsDS.GetGeoTransform()
    outRaster.SetGeoTransform(geoTrans)
    outRaster.SetProjection(srsDS.GetProjection())
    outband.FlushCache()
    # return NDVImaxMonthMeanTem


def merge_raster(path_in, pattern1, pattern2):
    root = path_in + '/'
    if os.path.exists(path_in):
        file_all = os.listdir(path_in)
        file = []
        for p in file_all:
            # if p[-8:] == 'nvdi.tif' or p[-4:] == 'nvdi.TIF':
            # if p.endswith('ndvi.tif'):
            if p.endswith(pattern1):
                file.append(root + p)
            elif p.endswith(pattern2):
                file.append(root + p)
    else:
        raise ValueError('Path not exists')
    path_out=path_in+'/'+pattern2
    gdal.Warp(path_out, file)

def solar_lon2imagexy(trans_srs, ct_srs, width_veg, high_veg):
    # srs像素转投影坐标
    px_srs, py_srs = imagexy2geo(trans_srs, width_veg, high_veg)
    # srs投影转经纬
    coords_srs = geo2lonlat(ct_srs, px_srs, py_srs)
    x = coords_srs[0]*10
    y = ((900+coords_srs[1]*10+1)+1)
    x = int(x)
    y = int(y)
    return x, y

def get_NPP(NdviList, MeanTemlist, LSWIList, Solar_path, FPARList):
    """"""
# Data2 SOL  太阳总辐射量
# RData FPAR
# Rn 净辐射量
# Data3 temperature 某一月平均气温
# Data4 rain月总降水
# Topt是指像元x处的最适温度,即该像元的NDVI在一年中达到最大时当月的平均温度。
# Te1 Te2 温度胁迫系数 Te 光能利用率
# E 实际蒸散量    Ep 潜在蒸散量    W 水分胁迫系数
    srsDS = gdal.Open(NdviList[0])
    srs_row = srsDS.RasterYSize  # 高
    srs_col = srsDS.RasterXSize  # 宽
    prosrs, geosrs = getSRSPair(srsDS)
    ct_srs = osr.CoordinateTransformation(prosrs, geosrs)  # 投影转经纬
    geotrans_srs = srsDS.GetGeoTransform()  # 地理参考系坐标
    # srsData = srsDS.GetRasterBand(1).ReadAsArray().astype(np.float32)

    for i in range(1):
        RDataDs = gdal.Open(FPARList[i])
        RData_row = RDataDs.RasterYSize  # 高
        RData_col = RDataDs.RasterXSize  # 宽
        proRData, geoRData = getSRSPair(RDataDs)
        ct_RData = osr.CoordinateTransformation(geoRData, proRData)  # 经纬转投影
        geotransRData = RDataDs.GetGeoTransform()  # 地理参考系坐标
        RData = RDataDs.GetRasterBand(1).ReadAsArray().astype(np.float32)

        # W / m2是每平方米的功率
        # MJ / M2是每平方米得到的能量,
        # 比如, 1W / m2, 照射了1秒, 就是1J / M2, 照射了1000000秒, 就是1MJ / M2
        # W/m2->MJ/m2
        Data2 = get_solar(SolarList[i])*(60*60*24*31/1e6)
        Data2_row = Data2.shape[0]
        Data2_col = Data2.shape[1]

        Data3Ds = gdal.Open(MeanTemlist[i])  # 某一月平均气温
        Data3_row = Data3Ds.RasterYSize  # 高
        Data3_col = Data3Ds.RasterXSize  # 宽
        proData3, geoData3 = getSRSPair(Data3Ds)
        ct_Data3 = osr.CoordinateTransformation(geoData3, proData3)  # 经纬转投影
        geotransData3 = Data3Ds.GetGeoTransform()  # 地理参考系坐标
        Data3 = Data3Ds.GetRasterBand(1).ReadAsArray().astype(np.float32)

        Data4Ds = gdal.Open(LSWIList[i])  # lswi代替水胁迫系数
        Data4_row = Data4Ds.RasterYSize  # 高
        Data4_col = Data4Ds.RasterXSize  # 宽
        proData4, geoData4 = getSRSPair(Data4Ds)
        ct_Data4 = osr.CoordinateTransformation(geoData4, proData4)  # 经纬转投影
        geotransData4 = Data4Ds.GetGeoTransform()  # 地理参考系坐标
        Data4 = Data4Ds.GetRasterBand(1).ReadAsArray().astype(np.float32)

        Data4=(1+Data4)/(1+np.max(Data4)) #土壤水分胁迫系数Wscalar

        ToptDs = gdal.Open(r"E:\map_anji&deqing\2021\test\topt\7_NDVImaxMonthMeanTem.tif")#最适气温
        Topt_row = ToptDs.RasterYSize  # 高
        Topt_col = ToptDs.RasterXSize  # 宽
        # proTopt, geoTopt = getSRSPair(ToptDs)
        # ct_Topt = osr.CoordinateTransformation(geoTopt, proTopt)  # 经纬转投影
        # geotransTopt = ToptDs.GetGeoTransform()  # 地理参考系坐标
        Topt = ToptDs.GetRasterBand(1).ReadAsArray().astype(np.float32)

        APAR = np.zeros((srs_row, srs_col))
        Te = np.zeros((srs_row, srs_col))
        Te1 = np.zeros((srs_row, srs_col))
        Te2 = np.zeros((srs_row, srs_col))
        # E = np.zeros((width_veg, high_veg))
        # Ep = np.zeros((width_veg, high_veg))
        # Ep0 = np.zeros((width_veg, high_veg))
        # Rn = np.zeros((width_veg, high_veg))
        NPP = np.zeros((srs_row, srs_col))

        for col in range(srs_col):
            for row in range(srs_row):
                print("col: ",col)
                X_RData, Y_RData = srs2imagexy(geotrans_srs, geotransRData, row, col, ct_srs, ct_RData)
                X_Data2, Y_Data2 = solar_lon2imagexy(geotrans_srs, ct_srs, row, col)
                # print(X_Data2)
                # print(Y_Data2)
                X_Data3, Y_Data3 = srs2imagexy(geotrans_srs, geotransData3, row, col, ct_srs, ct_Data3)
                X_Data4, Y_Data4 = srs2imagexy(geotrans_srs, geotransData4, row, col, ct_srs, ct_Data4)

                if X_RData > RData_col - 1 or X_RData < 0 or Y_RData < 0 or Y_RData > RData_row - 1:
                    print('RData not pair!')
                    continue
                if X_Data2 > Data2_col - 1 or X_Data2 < 0 or Y_Data2 < 0 or Y_Data2 > Data2_row - 1:
                    print('Data2 not pair!')
                    continue
                APAR[row, col] = RData[Y_RData, X_RData] * Data2[Y_Data2, X_Data2] * 0.5#RData: FPAR Data2: SOL
                Te1[row, col] = 0.8 + 0.02 * Topt[row, col] - 0.0005 * Topt[row, col] ** 2

                if X_Data3 > Data3_col - 1 or X_Data3 < 0 or Y_Data3 < 0 or Y_Data3 > Data3_row - 1:
                    print('Data3 not pair!')
                    continue
                Te2[row, col] = 1.184 / (1 + math.exp(0.2 * (Topt[row, col] - 10 - Data3[Y_Data3, X_Data3]))) * 1 \
                              / (1 + math.exp(0.3 * (-Topt[row, col] - 10 + Data3[Y_Data3, X_Data3])))
                # print(Te2[row, col])
                Te[row, col] = Te2[row, col] * Te1[row, col]
                # print(Te[row, col])

                # Ep0[xi,yj] = 16*(10*Data3[xi,yj]/I)**a
                # Rn[xi,yj] = ((Ep0[xi,yj]*Data4[xi,yj])**0.5)*(0.369+0.589*((Ep0[xi,yj]/Data4[xi,yj])**0.5)) #净辐射量
                # E[xi,yj] = Data4[xi,yj]*Rn[xi,yj]*(Data4[xi,yj]**2+Rn[xi,yj]**2+Data4[xi,yj]*Rn[xi,yj]) \
                # /((Data4[xi,yj]+Rn[xi,yj])*(Data4[xi,yj]**2+Rn[xi,yj]**2))   #E 区域实际蒸散量
                # Ep[xi,yj] = (E[xi,yj]+Ep0[xi,yj])/2 #Ep 区域潜在蒸散量，区域热量指数RTI
                # W[xi,yj] = 0.5+(0.5*E[xi,yj])/Ep[xi,yj]

                if X_Data4 > Data4_col - 1 or X_Data4 < 0 or Y_Data4 < 0 or Y_Data4 > Data4_row - 1:
                    print('Data4 not pair!')
                    continue
                # print('Data2: ',Data2[Y_Data2, X_Data2])
                # print('RData: ', RData[Y_RData, X_RData])
                # print('Te: ', Te[row, col])
                # print('Data4: ', Data4[Y_Data4, X_Data4])
                NPP[row, col] = Data2[Y_Data2, X_Data2] * RData[Y_RData, X_RData] * 0.5 * Te[row, col] * Data4[Y_Data4, X_Data4] * 0.541  # NPP
                print('NPP: ', NPP[row, col])

        nodata = -9999.0
        NPP[NPP < 0 or NPP>9999.0] = nodata

        driver = gdal.GetDriverByName('GTiff')
        out = NdviList[i].rsplit('.', 1)[0] + '_NPP.tif'
        outRaster = driver.Create(out, srs_col, srs_row, 1, gdal.GDT_Float32)
        outband = outRaster.GetRasterBand(1)
        outband.WriteArray(NPP)
        # outband.SetNoDataValue(nodata)

        geoTrans = srsDS.GetGeoTransform()
        outRaster.SetGeoTransform(geoTrans)
        outRaster.SetProjection(srsDS.GetProjection())
        outband.FlushCache()

# def adjust_npp(image_name, out=r'E:\map_anji&deqing\2021\test\nvdi\npp.tif'):
#     datasetname = gdal.Open(image_name)
#     if datasetname is None:
#         print('Could not open %s' % image_name)
#         return
#     img_width = datasetname.RasterXSize
#     img_height = datasetname.RasterYSize
#     data = np.array(datasetname.GetRasterBand(1).ReadAsArray(), np.float)
#
#     # LSWI=(NIR-SWIR)/(NIR+SWIR)
#     # landsat8
#     # band5 = np.array(datasetname.GetRasterBand(5).ReadAsArray(), np.float)
#     # band6 = np.array(datasetname.GetRasterBand(6).ReadAsArray(), np.float)#SWIR1
#     # LSWI = (band5-band6)/(band5+band6)
#     # del band5
#     # nodata = -9999
#     # LSWI[band6 == 0] = nodata
#     # del band6
#
#     # Sentinel2
#     # band8 = np.array(datasetname.GetRasterBand(8).ReadAsArray(), np.float)
#     # band11 = np.array(datasetname.GetRasterBand(11).ReadAsArray(), np.float)
#     # LSWI = (band8 - band11) / (band8 + band11)
#     # del band8
#     nodata = -9999
#     data[data > 1000] = nodata
#     data[data < 0]=nodata
#     data[data == 0] = nodata
#     # del band11
#
#     driver = gdal.GetDriverByName('GTiff')
#     if out == '':
#         out = image_name.rsplit('.', 1)[0] + '_lswi.tif'
#     outRaster = driver.Create(out, img_width, img_height, 1, gdal.GDT_Float32)
#     outband = outRaster.GetRasterBand(1)
#     outband.WriteArray(data)
#     outband.SetNoDataValue(nodata)
#
#     geoTrans = datasetname.GetGeoTransform()
#     outRaster.SetGeoTransform(geoTrans)
#     outRaster.SetProjection(datasetname.GetProjection())
#     outband.FlushCache()
#     return out


if __name__ == "__main__":

    bands_path = r"E:\data\yancheng\2023\射阳河水质监测\02\B5"
    nvdi_path = r"E:\map_anji&deqing\2021\test\ndvi"
    LSWI_path = r"E:\map_anji&deqing\2021\test\lswi"
    MeanTem_path = r"E:\map_anji&deqing\2021\test\temp"
    Solar_path = r"E:\map_anji&deqing\2021\test\solar"
    FPAR_path = r"E:\map_anji&deqing\2021\test\FPAR"

    merge_raster(bands_path, 'B5.TIF', 'B5.tif')
    # merge_raster(bands_path, 'lswi.tif')

    # MeanTemlist = []
    # NdviList = []
    # SolarList = []
    # LSWIList = []
    # FPARList = []
    #
    # for tem in os.listdir(MeanTem_path):
    #     if tem.endswith('.tif'):
    #         MeanTemlist.append(MeanTem_path + '/' + tem)
    # MeanTemlist.sort(key=lambda x: int(x[x.find(".tif")-2:x.find(".tif")]))
    #
    # for file in os.listdir(nvdi_path):
    #     list = file.split('.')
    #     NdviList.append(nvdi_path + '/' + file)
    # NdviList.sort(key=lambda x: int(x[x.find("_ndvi.tif")-2:x.find("_ndvi.tif")]))
    #
    #
    # for solar in os.listdir(Solar_path):
    #     SolarList.append(Solar_path + '\\' + solar)
    # SolarList.sort(key=lambda x: int(x[x.find("_monthly")-1:x.find("_monthly")]))
    #
    # for file in os.listdir(LSWI_path):
    #     LSWIList.append(LSWI_path + '/' + file)
    # LSWIList.sort(key=lambda x: int(x[x.find(".tif")-1:x.find(".tif")]))
    #
    # for FPAR in os.listdir(FPAR_path):
    #     if FPAR.endswith('.tif'):
    #         FPARList.append(FPAR_path + '/' + FPAR)
    # FPARList.sort(key=lambda x: int(x[x.find("_FPAR")-1:x.find("_FPAR")]))

    # get_FPAR(NdviList)
    # optTem2(NdviList, MeanTemlist)
    # get_NPP(NdviList, MeanTemlist, LSWIList, Solar_path, FPARList)
    print("finish")



