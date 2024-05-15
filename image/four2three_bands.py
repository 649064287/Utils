from PIL import Image
import os
def get_file_names(data_dir, file_type=['tif', 'tiff','png','jpg']):
    result_dir = []
    result_name = []
    for maindir, subdir, file_name_list in os.walk(data_dir):
        for filename in file_name_list:
            apath = maindir + '/' + filename
            ext = apath.split('.')[-1]
            if ext in file_type:
                result_dir.append(apath)
                result_name.append(filename)
            else:
                pass
    return result_dir, result_name

def fourTo3(data_dir, out_dir,file_type = ['tif', 'tiff','png','jpg']):
    img_dir, img_name = get_file_names(data_dir, file_type)
    count = 0
    for each_dir, each_name in zip(img_dir,img_name):
        image = Image.open(each_dir)
        r, g, b, a = image.split()
        image = Image.merge("RGB", (r, g, b))
        out_dir_images = out_dir + '/' + each_name
        image.save(out_dir_images)

if __name__ == '__main__':
    data_dir = r'Z:\lry\Data\old\img\test_img_8bit_png' #需转换得图片路径
    out_dir = r'Z:\lry\Data\old\img\test_img_3bands' #转换后存储的路径
    file_type = ['tif', 'tiff','png','jpg']
    fourTo3(data_dir,out_dir,file_type)
