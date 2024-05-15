import os

from osgeo import gdal

root = r"E:\data\ddl\zhejiang\0424\res"
outpath = r"E:\data\ddl\zhejiang\0424\res_png"
if not os.path.exists(outpath):
    os.mkdir(outpath)
for file in os.listdir(root):
    print(file)
    if file=="Thumbs.db":
        continue
    file_path=root+'/'+file
    ds=gdal.Open(file_path)
    driver=gdal.GetDriverByName('PNG')
    dst_ds = driver.CreateCopy(outpath + '/' + file[:-4] + '.png', ds)
    dst_ds = None
    src_ds = None