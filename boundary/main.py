import add_coordinate_001 as coor
from image import tif_greytif as greytif, tif_poly as poly

if __name__=="__main__":
    #二值图路径
    binary_path = r"D:\data\sample_farm2\xy\kuang"
    #带坐标影像路径/不带坐标系灰度图路径
    img_pos_folder = r"D:\data\sample_farm2\xy\img_1000"
    img_none_folder = r"D:\data\sample_farm2\xy\kuang_grey"
    #带坐标影像路径/不带坐标系影像路径
    img_pos_1000 = r"D:\data\sample_farm2\xy\img_1000"
    img_none_1024 = r"D:\data\sample_farm2\xy\img_xy_1024"
    #带坐标灰度图路径
    grey_proj_path = r"D:\data\sample_farm2\xy\kuang_grey_proj"

    greytif.tif_greytif(binary_path)#二值图转灰度图
    coor.get_coor(img_pos_folder, img_none_folder)#灰度图添加坐标
    coor.get_coor(img_pos_1000, img_none_1024)#1024影像添加坐标系
    poly.raster2poly(grey_proj_path)#shp外框

