import os
import shutil
from osgeo import gdal,ogr,osr
import numpy as np
from tqdm import tqdm
from files import files,myargs
from collections import defaultdict
import config
calctype="land"
folders=myargs['folders']
calcFolder=folders[calctype]
gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8","YES")   

landconv={
    "011":"51",
    "012":"51",
    "013":"51",
    "021":"52",
    "022":"52",
    "023":"52",
    "031":"11",
    "032":"2",
    "033":"12",
    "041":"3",
    "042":"3",
    "043":"3",
    "101":"6",
    "102":"6",
    "103":"6",
    "104":"6",
    "105":"6",
    "106":"6",
    "111":"4",
    "112":"4",
    "113":"4",
    "114":"4",
    "115":"4",
    "116":"4",
    "117":"4",
    "118":"6",
    "121":"6",
    "122":"6",
    "123":"51",
    "124":"9",
    "125":"4",
    "126":"9",
    "127":"9",
    "201":"6",
    "202":"6",
    "203":"6",
    "204":"6",
    "205":"6",
    }
landconv = defaultdict(lambda: 'none', landconv)



def rasPrepare(parcelgrid=files['parcelgrid']):
    
    outShapefile=files['calcdata']
    #countyshp=files['countyshp']
    if not os.path.exists(parcelgrid):
        print('file not exist:' + parcelgrid)
        return
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSource=driver.Open(parcelgrid)
    if inDataSource is None:
        print('Could not open %s' % parcelgrid)
    layerUse = inDataSource.GetLayer()
    count=layerUse.GetFeatureCount()
    srs=layerUse.GetSpatialRef()

    if int(gdal.__version__[0]) >= 3:
        # GDAL 3 changes axis order: https://github.com/OSGeo/gdal/issues/1546
        srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    #countyDataSource=driver.Open(countyshp)
    #if countyDataSource is None:
    #    print('Could not open %s' % countyshp)
    #layer = countyDataSource.GetLayer()

    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
    # create the spatial reference, WGS84
    #srs = osr.SpatialReference()
    #srs.ImportFromEPSG(4326)

    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("ecology", srs, geom_type=ogr.wkbPolygon)
    # Add an ID field
    addfields=['js','by','zf','highzf','RKLS','vfc','npp']#'DLBM'
    #iField = ogr.FieldDefn('DLBM', ogr.OFTString)
    #outLayer.CreateField(iField)
    inLayerDefn = layerUse.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)
    for n in addfields:
        iField = ogr.FieldDefn(n, ogr.OFTReal)
        outLayer.CreateField(iField)
    featureDefn = outLayer.GetLayerDefn()

    rain = files['pre']
    storm = files['storm']
    evap = files['evp']
    highevap = files['hiTemEvp']
    erostif = files['eros']
    Ktif = files['K']
    LStif = files['LS']
    vegTif= files['fvc']
    nppTif = files['npp']

    rainDS = gdal.Open(rain)
    bandRain=rainDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    geotransRain=rainDS.GetGeoTransform()
    widthRain=rainDS.RasterXSize
    heightRain=rainDS.RasterYSize
    prosrsRain = osr.SpatialReference()
    prosrsRain.ImportFromWkt(rainDS.GetProjection())
    ctRain = osr.CoordinateTransformation(srs, prosrsRain)
    statsRain = rainDS.GetRasterBand(1).GetStatistics(True,True)

    stormDS = gdal.Open(storm)
    bandStorm=stormDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    geotransStorm=stormDS.GetGeoTransform()
    widthStorm=stormDS.RasterXSize
    heightStorm=stormDS.RasterYSize
    prosrsStorm = osr.SpatialReference()
    prosrsStorm.ImportFromWkt(stormDS.GetProjection())
    ctStorm = osr.CoordinateTransformation(srs, prosrsStorm)

    evapDS = gdal.Open(evap)
    bandEvap=evapDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    geotransEvap=evapDS.GetGeoTransform()
    widthEvap=evapDS.RasterXSize
    heightEvap=evapDS.RasterYSize
    prosrsEvap = osr.SpatialReference()
    prosrsEvap.ImportFromWkt(evapDS.GetProjection())
    ctEvap = osr.CoordinateTransformation(srs, prosrsEvap)
    statsEvap= evapDS.GetRasterBand(1).GetStatistics( True, True )

    highevapDS = gdal.Open(highevap)
    bandHighEvap=highevapDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    geotransHighEvap=highevapDS.GetGeoTransform()
    widthHighEvap=highevapDS.RasterXSize
    heightHighEvap=highevapDS.RasterYSize
    prosrsHighEvap = osr.SpatialReference()
    prosrsHighEvap.ImportFromWkt(highevapDS.GetProjection())
    ctHighEvap = osr.CoordinateTransformation(srs, prosrsEvap)
    statsHighEvap= highevapDS.GetRasterBand(1).GetStatistics( True, True )

    erosDS = gdal.Open(erostif)
    erosBand = erosDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    geotransEros=erosDS.GetGeoTransform()
    widthEros=erosDS.RasterXSize
    heightEros=erosDS.RasterYSize
    prosrsEros = osr.SpatialReference()
    prosrsEros.ImportFromWkt(erosDS.GetProjection())
    ctEros = osr.CoordinateTransformation(srs, prosrsEros)
    statsEros = erosDS.GetRasterBand(1).GetStatistics( True, True )

    if not os.path.exists(Ktif):
        dir=os.path.dirname(os.path.dirname(os.path.dirname(Ktif)))
        dir=os.path.join(dir,'land')
        Ktif=os.path.join(dir,myargs['land']['K'])
    KDS = gdal.Open(Ktif)
    bandK=KDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    geotransK=KDS.GetGeoTransform()
    widthK=KDS.RasterXSize
    heightK=KDS.RasterYSize
    prosrsK = osr.SpatialReference()
    prosrsK.ImportFromWkt(KDS.GetProjection())
    ctK = osr.CoordinateTransformation(srs, prosrsK)
    statsK = KDS.GetRasterBand(1).GetStatistics( True, True )

    if not os.path.exists(LStif):
        dir=os.path.dirname(os.path.dirname(os.path.dirname(LSTif)))
        dir=os.path.join(dir,'land')
        LStif=os.path.join(dir,myargs['land']['LS'])
    SLDS = gdal.Open(LStif)
    bandSL=SLDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    geotransSL=SLDS.GetGeoTransform()
    widthSL=SLDS.RasterXSize
    heightSL=SLDS.RasterYSize
    prosrsSL = osr.SpatialReference()
    prosrsSL.ImportFromWkt(SLDS.GetProjection())
    ctSL = osr.CoordinateTransformation(srs, prosrsSL)
    statsSL = SLDS.GetRasterBand(1).GetStatistics( True, True )

    if not os.path.exists(vegTif):
        dir=os.path.dirname(os.path.dirname(os.path.dirname(vegTif)))
        dir=os.path.join(dir,'land')
        vegTif=os.path.join(dir,myargs['land']['fvc'])
    vegDS = gdal.Open(vegTif)
    bandVeg=vegDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    geotransVeg=vegDS.GetGeoTransform()
    widthVeg=vegDS.RasterXSize
    heightVeg=vegDS.RasterYSize
    prosrsVeg = osr.SpatialReference()
    prosrsVeg.ImportFromWkt(vegDS.GetProjection())
    ctVeg = osr.CoordinateTransformation(srs, prosrsVeg)

    #ndviDS = gdal.Open(ndviTif)
    #bandNdvi=ndviDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    #geotransNdvi=ndviDS.GetGeoTransform()
    #widthNdvi=ndviDS.RasterXSize
    #heightNdvi=ndviDS.RasterYSize
    #prosrsNdvi = osr.SpatialReference()
    #prosrsNdvi.ImportFromWkt(ndviDS.GetProjection())
    #ctNdvi = osr.CoordinateTransformation(srs, prosrsNdvi)

    if not os.path.exists(nppTif):
        dir=os.path.dirname(os.path.dirname(os.path.dirname(nppTif)))
        dir=os.path.join(dir,'land')
        nppTif=os.path.join(dir,myargs['land']['npp'])
    #mod17a3DS = gdal.Open(nppTif)    
    #subdatasets = mod17a3DS.GetSubDatasets()
    #nppTif=subdatasets[0][0]

    nppDS = gdal.Open(nppTif)
    bandnpp = nppDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    geotransNpp=nppDS.GetGeoTransform()
    widthNpp=nppDS.RasterXSize
    heightNpp=nppDS.RasterYSize
    prosrsNpp = osr.SpatialReference()
    prosrsNpp.ImportFromWkt(nppDS.GetProjection())
    ctNpp = osr.CoordinateTransformation(srs, prosrsNpp)
    statsNpp = nppDS.GetRasterBand(1).GetStatistics( True, True )

    typenum = defaultdict(lambda:0)
    for inFeature in tqdm(layerUse):
        landtype = inFeature.GetField("DLBM")
        #ecotype = landconv[landtype]
        #typenum[ecotype] += 1
        #i+=100
        #if typenum[ecotype] > 10:
        #    continue
        landarea = inFeature.GetGeometryRef().Area()
        poly = inFeature.GetGeometryRef()
        center = poly.Centroid()
        geoX=center.GetPoint(0)[0]
        geoY=center.GetPoint(0)[1]

        coordsRain = ctRain.TransformPoint(geoX, geoY)
        imgX = (int)((coordsRain[0]-geotransRain[0])//geotransRain[1])
        imgY = (int)((coordsRain[1]-geotransRain[3])//geotransRain[5])
        if imgX>widthRain or imgX < 0 or imgY<0 or imgY>heightRain-1:
            print('rain data not pair!')
        dataRain=bandRain[imgY][imgX]
        if dataRain < 0 or dataRain > 65530:
            dataRain = statsRain[2]

        coordsStorm = ctStorm.TransformPoint(geoX, geoY)
        imgX = (int)((coordsStorm[0]-geotransStorm[0])//geotransStorm[1])
        imgY = (int)((coordsStorm[1]-geotransStorm[3])//geotransStorm[5])
        if imgX>widthStorm or imgX < 0 or imgY<0 or imgY>heightStorm-1:
            print('rain data not pair!')
        dataStorm=bandStorm[imgY][imgX]

        coordsEvap = ctEvap.TransformPoint(geoX, geoY)
        imgX = (int)((coordsEvap[0]-geotransEvap[0])//geotransEvap[1])
        imgY = (int)((coordsEvap[1]-geotransEvap[3])//geotransEvap[5])
        if imgX>widthEvap or imgX < 0 or imgY<0 or imgY>heightEvap-1:
            print('evp data not pair!')
        dataEvap=bandEvap[imgY][imgX]
        if dataEvap < 0 or dataEvap > 65530:
            dataEvap = statsEvap[2]

        coordsHighEvap = ctHighEvap.TransformPoint(geoX, geoY)
        imgX = (int)((coordsHighEvap[0]-geotransHighEvap[0])//geotransHighEvap[1])
        imgY = (int)((coordsHighEvap[1]-geotransHighEvap[3])//geotransHighEvap[5])
        if imgX>widthHighEvap or imgX < 0 or imgY<0 or imgY>heightHighEvap-1:
            print('evp data not pair!')
        dataHighEvap=bandHighEvap[imgY][imgX]

        coordsEros = ctEros.TransformPoint(geoX, geoY)
        imgX = (int)((coordsEros[0]-geotransEros[0])//geotransEros[1])
        imgY = (int)((coordsEros[1]-geotransEros[3])//geotransEros[5])
        if imgX>widthEros or imgX < 0 or imgY<0 or imgY>heightEros-1:
            print('eros data not pair!')
        dataEros=erosBand[imgY][imgX]
        if dataEros < 0 or dataEros > 65530:
            dataEros = statsEros[2]

        coordsK = ctK.TransformPoint(geoX, geoY)
        imgX = (int)((coordsK[0]-geotransK[0])//geotransK[1])
        imgY = (int)((coordsK[1]-geotransK[3])//geotransK[5])
        if imgX>widthK or imgX < 0 or imgY<0 or imgY>heightK-1:
            print('K data not pair!')
        dataK=bandK[imgY][imgX]
        if dataK < 0 or dataK > 65530:
            dataK = statsK[2]
        #dataK *= 1e-6

        coordsSL = ctSL.TransformPoint(geoX, geoY)
        imgX = (int)((coordsSL[0]-geotransSL[0])//geotransSL[1])
        imgY = (int)((coordsSL[1]-geotransSL[3])//geotransSL[5])
        if imgX>widthSL or imgX < 0 or imgY<0 or imgY>heightSL-1:
            print('SL data not pair!')
        dataSL=bandSL[imgY][imgX]
        if dataSL < 0 or dataSL > 65530:
            dataSL = statsSL[2]
        #dataSL *= 1e-2

        RKLS=dataEros*dataK*dataSL

        coordsVeg = ctVeg.TransformPoint(geoX, geoY)
        imgX = (int)((coordsVeg[0]-geotransVeg[0])//geotransVeg[1])
        imgY = (int)((coordsVeg[1]-geotransVeg[3])//geotransVeg[5])
        if imgX>widthVeg or imgX < 0 or imgY<0 or imgY>heightVeg-1:
            print('veg data not pair!')
        dataVeg=bandVeg[imgY][imgX]
        #dataVeg=(dataNdvi-myargs['const']['ndvimin'])/(myargs['const']['ndvimax']-myargs['const']['ndvimin'])
        #if dataVeg<=0: ratio=0
        #elif dataVeg>=0.5:ratio=1
        #else: ratio = dataVeg*2
        #num=(int)((ratio-0.1)//0.2+1)
        #dataC=0
        #if ecotype=='11':
        #    dataC=CTable[0][num]
        #elif ecotype=='52' or ecotype=='2' or ecotype=='12':
        #    dataC=CTable[1][num]
        #elif ecotype=='3': 
        #    dataC=CTable[2][num]
        
        coordsNpp = ctNpp.TransformPoint(geoX, geoY)
        imgX = (int)((coordsNpp[0]-geotransNpp[0])//geotransNpp[1])
        imgY = (int)((coordsNpp[1]-geotransNpp[3])//geotransNpp[5])
        if imgX>widthNpp-1 or imgX<0 or imgY<0 or imgY>heightNpp-1:
            print('npp data not pair')
        datanpp=bandnpp[imgY][imgX]
        if statsNpp[2] > 4:
            datanpp*=1e-4     #kgC/m²/year
        if datanpp<0:
            datanpp=0
        if datanpp>3.2760:
            datanpp=0

        #coordsNdvi = ctNdvi.TransformPoint(geoX, geoY)
        #imgX = (int)((coordsNdvi[0]-geotransNdvi[0])//geotransNdvi[1])
        #imgY = (int)((coordsNdvi[1]-geotransNdvi[3])//geotransNdvi[5])
        #if imgX>widthNdvi-1 or imgX<0 or imgY<0 or imgY>heightNdvi-1:
        #    print('npp data not pair')
        #datanpp=bandNdvi[imgY][imgX]*1e-4     #kgC/m²/year

        # Create the feature and set values
        feature = ogr.Feature(featureDefn)
        #if ecotype != "none":
        geom = inFeature.GetGeometryRef().Buffer(0)
        feature.SetGeometry(geom)
        #for i in range(0, outLayerDefn.GetFieldCount()):
        #    feature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        feature.SetField('regionNum', inFeature.GetField('regionNum'))
        if 'grid' in parcelgrid:
            feature.SetField('gridNum', inFeature.GetField('gridNum'))
        feature.SetField("DLBM", landtype)
        #feature.SetField("newDLBM", int(ecotype))
        feature.SetField("js", dataRain)
        feature.SetField("by", dataStorm)
        feature.SetField("zf", dataEvap)
        feature.SetField("highzf", dataHighEvap)
        feature.SetField("RKLS", RKLS)
        feature.SetField("vfc", dataVeg)
        feature.SetField("npp", datanpp)

        outLayer.CreateFeature(feature)
        feature = None

    # Save and close DataSource
    inDataSource = None
    outDataSource = None 
    #countyDataSource = None

def shpPrepare():
    parcelgrid=files['parcelgrid']
    outShapefile=files['calcdata']
    if not os.path.exists(parcelgrid):
        print('file not exist:' + parcelgrid)
        return
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSource=driver.Open(parcelgrid)
    if inDataSource is None:
        print('Could not open %s' % parcelgrid)
    layerUse = inDataSource.GetLayer()
    count=layerUse.GetFeatureCount()
    srs=layerUse.GetSpatialRef()

    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("ecology", srs, geom_type=ogr.wkbPolygon)

    addfields=['js','zf','RKLS','vfc','npp']#'DLBM'
    iField = ogr.FieldDefn('DLBM', ogr.OFTString)
    outLayer.CreateField(iField)
    iField = ogr.FieldDefn('regionNum', ogr.OFTInteger)
    outLayer.CreateField(iField)
    iField = ogr.FieldDefn('gridNum', ogr.OFTInteger)
    outLayer.CreateField(iField)
    inLayerDefn = layerUse.GetLayerDefn()
    #for i in range(0, inLayerDefn.GetFieldCount()):
    #    fieldDefn = inLayerDefn.GetFieldDefn(i)
    #    outLayer.CreateField(fieldDefn)
    for n in addfields:
        iField = ogr.FieldDefn(n, ogr.OFTReal)
        outLayer.CreateField(iField)
    featureDefn = outLayer.GetLayerDefn()


    typenum = defaultdict(lambda:0)
    for inFeature in tqdm(layerUse):
        landtype = inFeature.GetField("DLBM")
        #ecotype = landconv[landtype]
        #typenum[ecotype] += 1
        #i+=100
        #if typenum[ecotype] > 10:
        #    continue
        landarea = inFeature.GetGeometryRef().Area()
        dataRain=inFeature.GetField('js')
        dataEvap=inFeature.GetField('zf')
        RKLS=inFeature.GetField('r')*inFeature.GetField('k')*inFeature.GetField('l')*inFeature.GetField('s')
        dataVeg=inFeature.GetField('FVC'+str(myargs['xingzheng']['year']))
        datanpp=inFeature.GetField('NPP'+str(myargs['xingzheng']['year']))
        feature = ogr.Feature(featureDefn)
        geom = inFeature.GetGeometryRef().Buffer(0)
        feature.SetGeometry(geom)
        #for i in range(0, outLayerDefn.GetFieldCount()):
        #    feature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        feature.SetField('regionNum', inFeature.GetField('regionNum'))
        feature.SetField('gridNum', inFeature.GetField('gridNum'))
        feature.SetField("DLBM", landtype)
        #feature.SetField("newDLBM", int(ecotype))
        feature.SetField("js", dataRain)
        feature.SetField("zf", dataEvap)
        feature.SetField("RKLS", RKLS)
        feature.SetField("vfc", dataVeg)
        feature.SetField("npp", datanpp)

        outLayer.CreateFeature(feature)
        feature = None

    inDataSource = None
    outDataSource = None 

def shpRasPrepare():
    parcelgrid=files['parcelgrid']
    outShapefile=files['calcdata']
    if not os.path.exists(parcelgrid):
        print('file not exist:' + parcelgrid)
        return
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSource=driver.Open(parcelgrid)
    if inDataSource is None:
        print('Could not open %s' % parcelgrid)
    layerUse = inDataSource.GetLayer()
    count=layerUse.GetFeatureCount()
    srs=layerUse.GetSpatialRef()

    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("ecology", srs, geom_type=ogr.wkbPolygon)

    addfields=['js','zf','RKLS','vfc','npp']#'DLBM'
    iField = ogr.FieldDefn('DLBM', ogr.OFTString)
    outLayer.CreateField(iField)
    iField = ogr.FieldDefn('regionNum', ogr.OFTInteger)
    outLayer.CreateField(iField)
    iField = ogr.FieldDefn('gridNum', ogr.OFTInteger)
    outLayer.CreateField(iField)
    inLayerDefn = layerUse.GetLayerDefn()
    #for i in range(0, inLayerDefn.GetFieldCount()):
    #    fieldDefn = inLayerDefn.GetFieldDefn(i)
    #    outLayer.CreateField(fieldDefn)
    for n in addfields:
        iField = ogr.FieldDefn(n, ogr.OFTReal)
        outLayer.CreateField(iField)
    featureDefn = outLayer.GetLayerDefn()

    vegTif= files['fvc']
    nppTif = files['npp']
    if not os.path.exists(vegTif):
        dir=os.path.dirname(os.path.dirname(os.path.dirname(vegTif)))
        dir=os.path.join(dir,'zhejiang\\land')
        vegTif=os.path.join(dir,myargs['land']['fvc'])
    vegDS = gdal.Open(vegTif)
    bandVeg=vegDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    geotransVeg=vegDS.GetGeoTransform()
    widthVeg=vegDS.RasterXSize
    heightVeg=vegDS.RasterYSize
    prosrsVeg = osr.SpatialReference()
    prosrsVeg.ImportFromWkt(vegDS.GetProjection())
    ctVeg = osr.CoordinateTransformation(srs, prosrsVeg)

    #ndviDS = gdal.Open(ndviTif)
    #bandNdvi=ndviDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    #geotransNdvi=ndviDS.GetGeoTransform()
    #widthNdvi=ndviDS.RasterXSize
    #heightNdvi=ndviDS.RasterYSize
    #prosrsNdvi = osr.SpatialReference()
    #prosrsNdvi.ImportFromWkt(ndviDS.GetProjection())
    #ctNdvi = osr.CoordinateTransformation(srs, prosrsNdvi)

    if not os.path.exists(nppTif):
        dir=os.path.dirname(os.path.dirname(os.path.dirname(nppTif)))
        dir=os.path.join(dir,'zhejiang\\land')
        mod17a3=os.path.join(dir,myargs['land']['npp'])
        mod17a3DS = gdal.Open(mod17a3)    
        subdatasets = mod17a3DS.GetSubDatasets()
        nppTif=subdatasets[0][0]

    nppDS = gdal.Open(nppTif)
    bandnpp = nppDS.GetRasterBand(1).ReadAsArray().astype(np.float)
    geotransNpp=nppDS.GetGeoTransform()
    widthNpp=nppDS.RasterXSize
    heightNpp=nppDS.RasterYSize
    prosrsNpp = osr.SpatialReference()
    prosrsNpp.ImportFromWkt(nppDS.GetProjection())
    ctNpp = osr.CoordinateTransformation(srs, prosrsNpp)
    statsNpp = nppDS.GetRasterBand(1).GetStatistics( True, True )

    typenum = defaultdict(lambda:0)
    for inFeature in tqdm(layerUse):
        landtype = inFeature.GetField("DLBM")
        poly = inFeature.GetGeometryRef()
        center = poly.Centroid()
        geoX=center.GetPoint(0)[0]
        geoY=center.GetPoint(0)[1]

        coordsVeg = ctVeg.TransformPoint(geoX, geoY)
        imgX = (int)((coordsVeg[0]-geotransVeg[0])//geotransVeg[1])
        imgY = (int)((coordsVeg[1]-geotransVeg[3])//geotransVeg[5])
        if imgX>widthVeg or imgX < 0 or imgY<0 or imgY>heightVeg-1:
            print('veg data not pair!')
        dataVeg=bandVeg[imgY][imgX]
        
        coordsNpp = ctNpp.TransformPoint(geoX, geoY)
        imgX = (int)((coordsNpp[0]-geotransNpp[0])//geotransNpp[1])
        imgY = (int)((coordsNpp[1]-geotransNpp[3])//geotransNpp[5])
        if imgX>widthNpp-1 or imgX<0 or imgY<0 or imgY>heightNpp-1:
            print('npp data not pair')
        datanpp=bandnpp[imgY][imgX]
        if statsNpp[2] > 4:
            datanpp*=1e-4     #kgC/m²/year
        if datanpp<0:
            datanpp=0
        if datanpp>3.2760:
            datanpp=0

        landarea = inFeature.GetGeometryRef().Area()
        dataRain=inFeature.GetField('js')
        dataEvap=inFeature.GetField('zf')
        RKLS=inFeature.GetField('r')*inFeature.GetField('k')*inFeature.GetField('l')*inFeature.GetField('s')
        #dataVeg=inFeature.GetField('FVC'+str(myargs['xingzheng']['year']))
        #datanpp=inFeature.GetField('NPP'+str(myargs['xingzheng']['year']))
        feature = ogr.Feature(featureDefn)
        geom = inFeature.GetGeometryRef().Buffer(0)
        feature.SetGeometry(geom)
        #for i in range(0, outLayerDefn.GetFieldCount()):
        #    feature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        feature.SetField('regionNum', inFeature.GetField('regionNum'))
        feature.SetField('gridNum', inFeature.GetField('gridNum'))
        feature.SetField("DLBM", landtype)
        #feature.SetField("newDLBM", int(ecotype))
        feature.SetField("js", dataRain)
        feature.SetField("zf", dataEvap)
        feature.SetField("RKLS", RKLS)
        feature.SetField("vfc", dataVeg)
        feature.SetField("npp", datanpp)

        outLayer.CreateFeature(feature)
        feature = None

    inDataSource = None
    outDataSource = None 

if __name__ == '__main__':
    #dataPrepare()
    shpPrepare()
