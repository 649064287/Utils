# -*- coding: utf-8 -*-
'''
将一张图片修改到指定尺寸并切割为500*500等份的小图片最后再将所有小图拼接为一张完整的原图
Author:bobibo
'''
from PIL import Image
Image.MAX_IMAGE_PIXELS = 2300000000
import sys
import os

#修改尺寸
def add_white_edge(inImgPath, outImgPath, width, height):
    r"""
    给宽图片上下补白边，让其满足一定比例，然后缩放到指定尺寸
    inImgPath: 输入图片路径
    outImgPath: 输出图片路径
    width: 最终宽度
    height: 最终高度

    inImg = Image.open(inImgPath)
    print(inImg.size)

    对于手机、相机等设备拍摄的照片，由于手持方向的不同，拍出来的照片可能是旋转0°、90°、180°和270°。
    即使在电脑上利用软件将其转正，他们的exif信息中还是会保留方位信息。
    在用PIL读取这些图像时，读取的是原始数据，
    也就是说，即使电脑屏幕上显示是正常的照片，用PIL读进来后，
    也可能是旋转的图像，并且图片的size也可能与屏幕上的不一样。
    对于这种情况，可以利用PIL读取exif中的orientation信息，
    然后根据这个信息将图片转正后，再进行后续操作，具体如下。

    try:
     for orientation in ExifTags.TAGS.keys():
      if ExifTags.TAGS[orientation] == 'Orientation': break
     exif = dict(inImg._getexif().items())
     if exif[orientation] == 3:
      inImg = inImg.rotate(180, expand=True)
     elif exif[orientation] == 6:
      inImg = inImg.rotate(270, expand=True)
     elif exif[orientation] == 8:
      inImg = inImg.rotate(90, expand=True)
    except:
     pass
    width, height = inImg.size  # 获取原图像的水平方向尺寸和垂直方向尺寸。
    print(inImg.size)
    """
    print(f'{inImgPath}')
    inImg: Image.Image = Image.open(inImgPath)
    bgWidth = inImg.width
    bgHeight = inImg.height
    #if bgWidth > bgHeight:
        #bgHeight = math.ceil((bgWidth * height) / width)
    # 创建一个白色背景图片
    bgImg: Image.Image = Image.new("RGB", (bgWidth, bgHeight), (255, 255, 255))
    bgImg.paste(inImg, (0, round((bgHeight - inImg.height) / 2)))

    bgImg.resize((width, height), Image.LANCZOS).save(outImgPath)

#切图
def cut_image(image):
    width, height = image.size
    item_width = 512
    box_list = []
    # (left, upper, right, lower)
    for i in range(0,2):#两重循环，生成9张图片基于原图的位置,i是高,j是宽
        for j in range(0,2):
            #print((i*item_width,j*item_width,(i+1)*item_width,(j+1)*item_width))
            box = (j*item_width,i*item_width,(j+1)*item_width,(i+1)*item_width)
            box_list.append(box)

    image_list = [image.crop(box) for box in box_list]
    return image_list

#保存
def save_images(image_list, img_name):
    index = 1
    for image in image_list:
        image.save(r'E:\data\yantian\test\img2\clip/'+img_name+'_'+str(index).zfill(2) + '.png', 'PNG')
        index += 1

# 定义图像拼接函数
def image_compose(compose_path, start):
    # 拼接
    IMAGES_PATH = r"E:\data\zhejiang\p\png/"  # 图片集地址
    IMAGES_FORMAT = ['.png']  # 图片格式
    IMAGE_SIZE = 128  # 每张小图片的大小
    IMAGE_ROW = 8  # 图片间隔，也就是合并成一张图后，一共有几行
    IMAGE_COLUMN = 8  # 图片间隔，也就是合并成一张图后，一共有几列


    # 获取图片集地址下的所有图片名称
    image_names = [name for name in os.listdir(IMAGES_PATH) for item in IMAGES_FORMAT if
                   os.path.splitext(name)[1] == item]
    image_names.sort()

    names=image_names[start:start+64]
    compose_path=os.path.join(compose_path, names[0][:-7]+'.png')
    to_image = Image.new('RGB', (IMAGE_COLUMN * IMAGE_SIZE, IMAGE_ROW * IMAGE_SIZE))  # 创建一个新图
    # to_image = Image.new('RGB', (IMAGE_COLUMN * IMAGE_SIZE, IMAGE_ROW * IMAGE_SIZE)).convert('L')  # 创建一个新图
    # 循环遍历，把每张图片按顺序粘贴到对应位置上
    for y in range(1, IMAGE_ROW + 1):
        for x in range(1, IMAGE_COLUMN + 1):
            print(names[IMAGE_COLUMN * (y - 1) + x - 1])
            from_image = Image.open(IMAGES_PATH + names[IMAGE_COLUMN * (y - 1) + x - 1]).resize(
                (IMAGE_SIZE, IMAGE_SIZE), Image.ANTIALIAS)
            to_image.paste(from_image, ((x - 1) * IMAGE_SIZE, (y - 1) * IMAGE_SIZE))
    return to_image.save(compose_path)  # 保存新图


if __name__ == '__main__':
    file_path = r"E:\data\yantian\test\img2\img"
    out_path = r"E:\data\zhejiang\p\compose"

    for img in os.listdir(file_path):
        img_path = os.path.join(file_path, img)
        image = Image.open(img_path)
        # image = Image.open(img_path).convert('L')
        #image.show()
        image_list = cut_image(image)
        print(img[:img.find('.')])
        save_images(image_list, img[:img.find('.')])

    # for i in range(0, 4800, 64):
    #     image_compose(out_path, i)  # 调用函数

