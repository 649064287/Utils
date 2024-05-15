import os
import numpy as np
from osgeo import gdal,ogr
import glob
from tqdm import tqdm
import casaNpp

def getNDVI(image_name,out=''):
    datasetname = gdal.Open( image_name )
    if datasetname is None:
        print('Could not open %s'% image_name)
        return
    numBand = datasetname.RasterCount
    if numBand < 4:
        return
    img_width = datasetname.RasterXSize
    img_height = datasetname.RasterYSize
    # landsat8
    # band5 = np.array(datasetname.GetRasterBand(5).ReadAsArray(),np.float)
    # band4 = np.array(datasetname.GetRasterBand(4).ReadAsArray(),np.float)
    # ndvi = (band5-band4)/(band5+band4+1e-5)
    # del band4
    # nodata=-9999
    # ndvi[band5==0]=nodata
    # del band5

    # Sentinel2
    band8 = np.array(datasetname.GetRasterBand(8).ReadAsArray(), np.float)
    band4 = np.array(datasetname.GetRasterBand(4).ReadAsArray(), np.float)
    ndvi = (band8 - band4) / (band8 + band4 + 1e-5)
    del band4
    nodata = -9999
    ndvi[band8 == 0] = nodata
    del band8

    driver = gdal.GetDriverByName('GTiff')
    if out=='':
        out=image_name.rsplit('.',1)[0]+'_ndvi.tif'
    outRaster = driver.Create(out, img_width, img_height, 1, gdal.GDT_Float32)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(ndvi)
    outband.SetNoDataValue(nodata)

    geoTrans = datasetname.GetGeoTransform()
    outRaster.SetGeoTransform(geoTrans)
    outRaster.SetProjection(datasetname.GetProjection())
    outband.FlushCache()
    return out

def getNDWI(image_name,out=''):
    datasetname = gdal.Open( image_name )
    if datasetname is None:
        print('Could not open %s'% image_name)
        return
    numBand = datasetname.RasterCount
    if numBand < 2:
        return
    img_width = datasetname.RasterXSize
    img_height = datasetname.RasterYSize
    band3 = np.array(datasetname.GetRasterBand(5).ReadAsArray(),np.float)
    band8 = np.array(datasetname.GetRasterBand(6).ReadAsArray(),np.float)
    ndwi = (band3-band8)/(band3+band8+1e-5)
    del band3
    nodata=-9999
    ndwi[band8==0]=nodata
    del band8

    driver = gdal.GetDriverByName('GTiff')
    if out=='':
        out=image_name.rsplit('.',1)[0]+'_ndwi.tif'
    outRaster = driver.Create(out, img_width, img_height, 1, gdal.GDT_Float32)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(ndwi)
    outband.SetNoDataValue(nodata)

    geoTrans = datasetname.GetGeoTransform()
    outRaster.SetGeoTransform(geoTrans)
    outRaster.SetProjection(datasetname.GetProjection())
    outband.FlushCache()
    return out

def getVFC(image_name,out=''):
    datasetname = gdal.Open( image_name )
    if datasetname is None:
        print('Could not open %s'% image_name)
        return
    numBand = datasetname.RasterCount
    if numBand < 4:
        return
    img_width = datasetname.RasterXSize
    img_height = datasetname.RasterYSize
    band4 = np.array(datasetname.GetRasterBand(4).ReadAsArray(),np.float)
    band3 = np.array(datasetname.GetRasterBand(3).ReadAsArray(),np.float)
    ndvi = (band4-band3)/(band4+band3+1e-5)
    del band3
    ndvi[band4==0]=-9999
    del band4
    num = np.sum(ndvi.flat>-1)
    print(num)
    hist,bins=np.histogram(ndvi.flat,bins=200,range=(-1,1))
    print(hist[0])
    minok=maxok=0
    num1=min(num*1e-4,1000)
    for i in range(1,200):
        hist[i] += hist[i-1]
        if not minok and hist[i] > num1:
            ndvimin = i/100.0 - 1
            minok=1
        if not maxok and hist[i] > num-num1:
            ndvimax = i/100.0 - 1
            maxok=1
    #ndvimax = ndvi.max()
    #ndvimin = ndvi.min()
    ndvimin = -0.1
    print('max=%f,min=%f'%(ndvimax,ndvimin))
    vfc = (ndvi-ndvimin)/(ndvimax-ndvimin)
    vfc[vfc<0]=0
    vfc[vfc>1]=1

    driver = gdal.GetDriverByName('GTiff')
    if out=='':
        out=image_name.rsplit('.',1)[0]+'_vfc.tif'
    outRaster = driver.Create(out, img_width, img_height, 1, gdal.GDT_Float32)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(vfc)
    #outband.SetNoDataValue(0)

    geoTrans = datasetname.GetGeoTransform()
    outRaster.SetGeoTransform(geoTrans)
    outRaster.SetProjection(datasetname.GetProjection())
    outband.FlushCache()
    return

def ndvi2VFC(ndvi_name,ndvimax=0.9,ndvimin=-0.5,out=''):
    datasetname = gdal.Open( ndvi_name )
    if datasetname is None:
        print('Could not open %s'% ndvi_name)
        return
    numBand = datasetname.RasterCount
    if numBand != 1:
        return
    img_width = datasetname.RasterXSize
    img_height = datasetname.RasterYSize
    ndvi = np.array(datasetname.GetRasterBand(1).ReadAsArray(),np.float)
    statsNdvi = datasetname.GetRasterBand(1).GetStatistics(True,True)
    ndvimax=statsNdvi[1]
    ndvimin=statsNdvi[0]

    vfc = (ndvi-ndvimin)/(ndvimax-ndvimin)
    vfc[vfc<0]=0
    vfc[vfc>1]=1

    driver = gdal.GetDriverByName('GTiff')
    if out=='':
        out=ndvi_name.rsplit('.',1)[0]+'_vfc.tif'
    outRaster = driver.Create(out, img_width, img_height, 1, gdal.GDT_Float32)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(vfc)
    outband.SetNoDataValue(0)

    geoTrans = datasetname.GetGeoTransform()
    outRaster.SetGeoTransform(geoTrans)
    outRaster.SetProjection(datasetname.GetProjection())
    outband.FlushCache()
    return

def ndvi2max(ndvi_folder,out=''):
    files=glob.glob(os.path.join(ndvi_folder,'*.hdf'))
    mod13q1DS0 = gdal.Open(files[0])    
    subdatasets = mod13q1DS0.GetSubDatasets()
    ndviDS0 = gdal.Open(subdatasets[0][0])
    width=ndviDS0.RasterXSize
    height=ndviDS0.RasterYSize
    ndvimax=np.zeros((height,width),np.float32)
    for file in tqdm(files):
        mod13q1DS = gdal.Open(file)    
        subdatasets = mod13q1DS.GetSubDatasets()
        ndviDS = gdal.Open(subdatasets[0][0])
        ndvidata=ndviDS.GetRasterBand(1).ReadAsArray().astype(np.float)
        ndvimax=np.maximum(ndvimax,ndvidata)
        ndviDS=None
        mod13q1DS=None
    
    driver = gdal.GetDriverByName('GTiff')
    if out=='':
        out=os.path.join(ndvi_folder,'maxndvi.tif')
    print('output to '+out)
    outRaster = driver.Create(out, width, height, 1, gdal.GDT_Float32)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(ndvimax)
    outband.SetNoDataValue(0)

    outRaster.SetGeoTransform(ndviDS0.GetGeoTransform())
    outRaster.SetProjection(ndviDS0.GetProjection())
    outband.FlushCache()
    outRaster=None
    ndviDS0=None
    mod13q1DS0=None
    
def RasterMosaic():
    print("图像拼接")
    input1=r"x:\GEPData\NPP\MOD17A3HGF.A2020001.h28v05.006.2021113150124.hdf"
    input2=r"x:\GEPData\NPP\MOD17A3HGF.A2020001.h28v06.006.2021113150140.hdf"
    inputrasfile1 = gdal.Open(input1, gdal.GA_ReadOnly) # 第一幅影像
    subdatasets = inputrasfile1.GetSubDatasets()
    inputTif1=subdatasets[0][0]
    inputDS1 = gdal.Open(inputTif1)
    inputProj1 = inputDS1.GetProjection()
    inputrasfile2 = gdal.Open(input2, gdal.GA_ReadOnly) # 第一幅影像
    subdatasets = inputrasfile2.GetSubDatasets()
    inputTif2=subdatasets[0][0]
    inputDS2 = gdal.Open(inputTif2)
    inputProj2 = inputDS2.GetProjection()
    outputfilePath = r'x:\GEPData\NPP\MOD17A3HGF.A2020001.h28v0506.tif'
    options=gdal.WarpOptions(srcSRS=inputProj1, dstSRS=inputProj1,format='GTiff',resampleAlg=gdal.GRA_Bilinear)
    gdal.Warp(outputfilePath,[inputDS1,inputDS2],options=options)

def RasterMosaic2():
    print("图像拼接")
    input1=r"X:\GEPData\NDVI\2018\maxndvi.tif"
    input2=r"X:\GEPData\NDVI\2018\v05\maxndvi.tif"
    inputDS1 = gdal.Open(input1, gdal.GA_ReadOnly) # 第一幅影像
    inputProj1 = inputDS1.GetProjection()
    inputDS2 = gdal.Open(input2, gdal.GA_ReadOnly) # 第一幅影像
    inputProj2 = inputDS2.GetProjection()
    outputfilePath = r'x:\GEPData\NDVI\2018\maxndvi_mosaic.tif'
    options=gdal.WarpOptions(srcSRS=inputProj1, dstSRS=inputProj1,format='GTiff',resampleAlg=gdal.GRA_Bilinear)
    gdal.Warp(outputfilePath,[inputDS1,inputDS2],options=options)

def getLSWI(image_name, image_name2, out=''):
    datasetname = gdal.Open(image_name)
    datasetname2 = gdal.Open(image_name2)
    if datasetname is None:
        print('Could not open %s' % image_name)
        return
    if datasetname2 is None:
        print('Could not open %s' % image_name2)
        return
    img_width = datasetname.RasterXSize
    img_height = datasetname.RasterYSize

    band8 = np.array(datasetname.GetRasterBand(1).ReadAsArray(), np.float)
    band11 = np.array(datasetname2.GetRasterBand(1).ReadAsArray(), np.float)
    bandnew = np.zeros((img_width, img_height))
    for j in range(img_height):
        for i in range(img_width):
            px_band8, py_band8 = casaNpp.imagexy2geo(datasetname, i, j)
            coords_band8 = casaNpp.geo2lonlat(datasetname, px_band8, py_band8)
            geotrans_bandnew = casaNpp.lonlat2geo(datasetname2, coords_band8[0], coords_band8[1])
            imgX, imgY = casaNpp.geo2imagexy(datasetname2, geotrans_bandnew[0], geotrans_bandnew[1])#band_11像素坐标
            imgX = int(imgX)
            imgY = int(imgY)
            if imgX > img_width - 1 or imgX < 0 or imgY < 0 or imgY > img_height - 1:
                print('nvdi data not pair!')
                continue
            bandnew[i, j] = band11[imgX, imgY]



    LSWI = (band8-bandnew)/(band8+bandnew)
    del band8
    nodata = -9999
    LSWI[bandnew == 0] = nodata
    del bandnew

    driver = gdal.GetDriverByName('GTiff')
    if out == '':
        out = image_name.rsplit('.', 1)[0] + '_LSWI.tif'
    outRaster = driver.Create(out, img_width, img_height, 1, gdal.GDT_Float32)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(LSWI)
    outband.SetNoDataValue(nodata)

    geoTrans = datasetname.GetGeoTransform()
    outRaster.SetGeoTransform(geoTrans)
    outRaster.SetProjection(datasetname.GetProjection())
    outband.FlushCache()
    return out

def getLSWI2(image_name, out=''):
    datasetname = gdal.Open(image_name)
    if datasetname is None:
        print('Could not open %s' % image_name)
        return
    img_width = datasetname.RasterXSize
    img_height = datasetname.RasterYSize

    #LSWI=(NIR-SWIR)/(NIR+SWIR)
    # landsat8
    # band5 = np.array(datasetname.GetRasterBand(5).ReadAsArray(), np.float)
    # band6 = np.array(datasetname.GetRasterBand(6).ReadAsArray(), np.float)#SWIR1
    # LSWI = (band5-band6)/(band5+band6)
    # del band5
    # nodata = -9999
    # LSWI[band6 == 0] = nodata
    # del band6

    #Sentinel2
    band8 = np.array(datasetname.GetRasterBand(8).ReadAsArray(), np.float)
    band11 = np.array(datasetname.GetRasterBand(11).ReadAsArray(), np.float)
    LSWI = (band8 - band11) / (band8 + band11)
    del band8
    nodata = -9999
    LSWI[band11 == 0] = nodata
    del band11

    driver = gdal.GetDriverByName('GTiff')
    if out == '':
        out = image_name.rsplit('.', 1)[0] + '_lswi.tif'
    outRaster = driver.Create(out, img_width, img_height, 1, gdal.GDT_Float32)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(LSWI)
    outband.SetNoDataValue(nodata)

    geoTrans = datasetname.GetGeoTransform()
    outRaster.SetGeoTransform(geoTrans)
    outRaster.SetProjection(datasetname.GetProjection())
    outband.FlushCache()
    return out

if __name__ == '__main__':

    # RasterMosaic2()
    # ndvi2VFC(r'x:\GEPData\NDVI\2018\maxndvi_mosaic.tif')
    #year='2020'
    #folder=os.path.join(r"x:\GEPData\NDVI",year)
    #folder=os.path.join(folder,'v05')
    #ndvi2max(folder)
    # ndvi2VFC(os.path.join(folder,'maxndvi.tif'))
    # ndvi2VFC(r"D:\map_yancheng\ndvi\2022_clip.tif")

    #getVFC(r"\\192.168.50.56\Data\tongxiang\GF1B_PMS_20200722_rpc_GS_mosaic_clip_warp.dat")
    getNDVI(r"E:\map_anji&deqing\2021\12\L1C_T51RTP_A025140_20211229T024115\composite\T51RTP_20211229T024119_12bands.tif")
    # getVFC(r"E:\Data\tongxiang\gf2-20200218\tongxiang_20200218.tif")
    getLSWI2(r"E:\map_anji&deqing\2021\12\L1C_T51RTP_A025140_20211229T024115\composite\T51RTP_20211229T024119_12bands.tif")

    # root = r"D:\map_anji\2021\lswi\12"
    # for name in os.listdir(root):
    #     if name.endswith('.tif'):
    #         getLSWI2(root + '\\' + name)

    # getNDWI(r"D:\map_yancheng\LC09_L2SP_119037_20220618_20220701_02_T1\1\LC09_L2SP_119037_20220618_20220701_02_T1_S_7.tif")
