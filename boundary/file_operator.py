import os
import shutil
import zipfile


def scan_files(directory, target_img, postfix=None):

    # path=unicode(directory,'utf-8')
    for root, sub_dirs, files in os.walk(directory):
        # # 二级目录
        # for sub_dir in sub_dirs:
        #     # 三级目录
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    cutmove_tif(root, special_file, target_img)
                # else:
                #     cutmove_shp(root, special_file, target)


def cutmove_tif(root, special_file, target_img):

    if os.path.isfile(target_img+"/"+special_file):
        os.remove(target_img+"/"+special_file)
    os.rename(root+"/"+special_file, target_img+"/"+special_file)


def cutmove_shp(root, special_file, target_shp):

    if os.path.isfile(target_shp+"/"+special_file):
        os.remove(target_shp+"/"+special_file)
    start = special_file.find("_")
    end = special_file.find(".")
    r = special_file[start:end]
    new_name = special_file.replace(r, "")
    os.rename(root+"/"+special_file, target_shp+"/"+new_name)


def runmian(target_img):

    if not os.path.isdir(target_img):
        os.mkdir(target_img)
    # if not os.path.isdir(target_shp):
    #     os.mkdir(target_shp)


def rename(directory, file1):
    """修改文件名 例：boli_change"""
    for root, subdir, files in os.walk(directory):
        for sub in subdir:
            sub_path = root + '/' + sub
            for filename in os.listdir(sub_path):
                dot = filename.find('.')
                newname = file1 + '_' + sub + filename[dot:]
                os.rename(sub_path+'/'+filename, sub_path +'/'+newname)


def rename2(directory):
    """修改文件夹名称"""
    for root, subdir, files in os.walk(directory):
        for s in subdir:
            if s == 'output':
                os.rename(root+'/'+s, root+'/'+'now')
            elif s == 'output0':
                os.rename(root+'/'+s, root+'/'+'pre')


def refile_txt(input, output):
    input = open(input, 'r')
    output = open(output, 'w')
    str_list = input.readlines()
    for str in str_list:
        # print(str)
        str = str.replace("G:\\lry\\google\\jzdl\\jz_img\\", "C:\\Users\\64906\\Documents\\workspace\\\Road-Extraction-master\\data\\train\\sat\\")
        str = str.replace("G:\\lry\\google\\jzdl\\jz_poly\\", "C:\\Users\\64906\\Documents\\workspace\\\Road-Extraction-master\\data\\train\\lab\\")
        output.writelines(str)


def dele(directory):
    for root, subdir, files in os.walk(directory):
        for file in files:
            n = file.find(".")
            print(file[n-2:n])
            if file[n-2:n] == "_1":
                os.remove(directory + "\\" + file)


def zipDir(dirpath,outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    # for root, subdir, files in os.walk(dirpath):

    zip = zipfile.ZipFile(outFullName,"w",zipfile.ZIP_DEFLATED)
    for path,dirnames,filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath,'')

        for filename in filenames:
            if filename.endswith('.xlsx'):
                continue
            zip.write(os.path.join(path,filename),os.path.join(fpath,filename))
    zip.close()

# root = "Z:\lry\sample_farm\新沂市耕地样本"
# target_img = r"Z:\lry\sample_farm\xy_img"
# target_shp = r"Z:\lry\sample_farm\xy_shp"
#
# target_poly = r"Z:\lry\data\lab"
# txt_path = "E:/train.txt"
# txt_out = "E:/train_2.txt"
#
# runmian()
# scan_files(root, ".tif")

# root = r'C:\Users\64906\Desktop\德清-投影改'
# for file in os.listdir(root):
#     rename(root + '/' + file, file)
# rename(root)
# refile_txt(txt_path, txt_out)
# dele(r"D:\lab1024")

#压缩文件
# root = r'C:\Users\64906\Desktop\德清-投影改'
# time = ['change', 'pre', 'now']
# for county in os.listdir(root):
#     for t in time:
#         filename = county+'_'+t
#         dirpath = root+'/'+county+'/'+t+'/'#C:\Users\64906\Desktop\德清-投影改\boli\change\
#         zipDir(dirpath,dirpath+filename+'.zip')
#     print(county)
# zipDir(r'C:\Users\64906\Desktop\德清-投影改\boli\change', r'C:\Users\64906\Desktop\德清-投影改\boli\now\boli_now.zip')

# print("finish")