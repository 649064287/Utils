import os
import random
import shutil
import zipfile
import codecs

import numpy as np
from xpinyin import Pinyin


def scan_files(directory, postfix=None):

    # path=unicode(directory,'utf-8')
    for root, sub_dirs, files in os.walk(directory):
        # # 二级目录
        # for sub_dir in sub_dirs:
        #     # 三级目录
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    cutmove_tif(root, special_file)
                else:
                    cutmove_shp(root, special_file)


def cutmove_tif(root, special_file):

    if os.path.isfile(target_img+"/"+special_file):
        os.remove(target_img+"/"+special_file)
    os.rename(root+"/"+special_file, target_img+"/"+special_file)


def cutmove_shp(root, special_file):

    if os.path.isfile(target_shp+"/"+special_file):
        os.remove(target_shp+"/"+special_file)
    start = special_file.find("_")
    end = special_file.find(".")
    r = special_file[start:end]
    new_name = special_file.replace(r, "")
    os.rename(root+"/"+special_file, target_shp+"/"+new_name)


def runmian():

    if not os.path.isdir(target_img):
        os.mkdir(target_img)
    if not os.path.isdir(target_shp):
        os.mkdir(target_shp)


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


def rename3(root):
    id=1
    for filename in os.listdir(root):
        dot = filename.find('.')
        newname = filename[:dot-4] + filename[dot:]
        os.rename(root + '/' + filename, root + '/' + newname)


def rename4(root):
    for filename in os.listdir(root):
        sp_dots=filename.split('.')
        # newname=sp_dots[0][:-5]+'.'+sp_dots[1]
        sp_=sp_dots[0].split('_')
        newname = sp_[0]+'_'+sp_[1]+'.'+sp_dots[1]
        os.rename(root + '/' + filename, root + '/' + newname)

def rename5(root):
    for filename in os.listdir(root):
        dot = filename.find('.')
        p = Pinyin()
        result = p.get_pinyin(filename[:dot])
        newname = result + '.tif'
        os.rename(root + '/' + filename, root + '/' + newname)

def rename6(img_path1, lab_path1):
    ind=0
    for filename in os.listdir(img_path1):
        img_name="region_%d_sat.tif" % ind
        lab_name="region_%d_lab.tif" % ind
        os.rename(img_path1 + '/' + filename, img_path1 + '/' + img_name)
        os.rename(lab_path1 + '/' + filename, lab_path1 + '/' + lab_name)
        ind=ind+1

def spilt_sample(src, target):
    if not os.path.exists(target):
        os.makedirs(target)
    # indrange_train = []
    # indrange_test = []
    # for x in range(235):
    #     if x % 10 < 7 :
    #         indrange_train.append(x)
    #
    #     if x % 10 == 7:
    #         indrange_test.append(x)
    #     # if x % 20 == 18:
    #     #     indrange_train.append(x)
    #     # if x % 20 == 8:
    #     #     indrange_test.append(x)

    # 生成包含 1-235 的整数序列
    samples = list(range(0, 235))

    # 随机打乱序列
    random.shuffle(samples)

    # 将序列分为两半
    # half = len(samples) // 2
    split_index = int(len(samples) * 9 / 10)
    indrange_train = samples[:split_index]
    indrange_test = samples[split_index:]

    raw_files = []
    seg_files = []
    for ind in indrange_test:
        raw_files.append(src + "/img/region_%d_sat.tif" % ind)
        seg_files.append(src + "/lab/region_%d_lab.tif" % ind)
        if not os.path.exists(src + "/img/region_%d_sat.tif" % ind):
            continue
        shutil.move(raw_files.pop(), target + "/img/region_%d_sat.tif" % ind)
        shutil.move(seg_files.pop(), target + "/lab/region_%d_lab.tif" % ind)



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
            # n = file.find(".")
            # print(file[n-2:n])
            # if file[n-2:n] == "_1":
            #     os.remove(directory + "\\" + file)
            if file.endswith('.zip'):
                os.remove(directory + "\\" + file)


def zipDir(startdir, file_news):
    # startdir = ".\\123"  #要压缩的文件夹路径
    # file_news = startdir +'.zip' # 压缩后文件夹的名字
    z = zipfile.ZipFile(file_news,'w',zipfile.ZIP_DEFLATED) #参数一：文件夹名
    for dirpath, dirnames, filenames in os.walk(startdir):
        fpath = dirpath.replace(startdir,'') #这一句很重要，不replace的话，就从根目录开始复制
        fpath = fpath and fpath + os.sep or ''#这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
        for filename in filenames:
            if not filename.endswith('.zip'):
                z.write(os.path.join(dirpath, filename),fpath+filename)
                print ('压缩成功')
    z.close()

def ReadFile(filePath,encoding):
    with codecs.open(filePath,'r',encoding) as f:
        return f.read()

def WriteFile(filePath,u,encoding):
    with codecs.open(filePath,"w",encoding) as f:
        f.write(u)

def UTF8BOM_UTF8(src,dst):
    content = ReadFile(src,encoding="utf-8-sig")
    WriteFile(dst,content,encoding="utf-8")

def move_tif(pix1000, pix1024, outpath):
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    for file in os.listdir(pix1024):
        src=os.path.join(pix1000, file)
        shutil.copy(src, outpath+file)

# root = "Z:\lry\sample_farm\新沂市耕地样本"
# target_img = r"Z:\lry\sample_farm\xy_img"
# target_shp = r"Z:\lry\sample_farm\xy_shp"

# target_poly = r"Z:\lry\data\lab"
# txt_path = "E:/train.txt"
# txt_out = "E:/train_2.txt"

# runmian()
# scan_files(root, ".tif")

# #重命名文件
# root = r'E:\项目8.29'
# for file in os.listdir(root):
#     rename(root + '/' + file, file)

# rename(root)
# refile_txt(txt_path, txt_out)
# dele(r"D:\lab1024")

#压缩文件
# root = r'E:\项目8.29'
# time = ['change', 'pre', 'now']
# for county in os.listdir(root):
#     for t in time:
#         filename = county+'_'+t
#         dirpath = root+'/'+county+'/'+t+'/'#C:\Users\64906\Desktop\德清-投影改\boli\change\
#         if not os.path.exists(dirpath):
#             continue
#         zipDir(dirpath,dirpath+filename+'.zip')
#         # dele(dirpath)
#     print(county)

#压缩文件
# root = r"E:\qingchuan\output"
# for county in os.listdir(root):
#     dirpath = root+'/'+county
#     zipDir(dirpath, dirpath+'/'+county+'.zip')
#     # dele(dirpath)
#     print(county)

# zipDir(r'D:\data\anji\anji_gep\douban\change', r'D:\data\anji\anji_gep\douban\change\1.zip')

# rename4(r"E:\data\yantian\train\lab\proj")

# rename6(r"E:\data\zhejiang\train 0227\tif\img", r"E:\data\zhejiang\train 0227\tif\lab")

# spilt_sample(r"E:\data\zhejiang\train 0304\tif", r"E:\data\zhejiang\train 0304\tif_test")

#转编码
# root = r"E:\qingchuan\sld"
# save = r"E:\qingchuan\sld2"
# for file in os.listdir(root):
#     filepath = root+'/'+file
#     savepath = save+'/'+file
#     UTF8BOM_UTF8(filepath, savepath)

# h, w = 1024, 1024
# p_h, p_w = 128, 128
# o = 0
#
# x_ = np.int32(np.linspace(o, h - p_h, 16))
# y_ = np.int32(np.linspace(o, w - p_w, 16))
#
# print("x_ array:", x_)
# print("y_ array:", y_)
#


print("finish")