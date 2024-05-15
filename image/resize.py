import os

import cv2


def resize_1024(src, save):
    h, w, c = src.shape
    res = cv2.resize(src, (int(w + 24), int(h + 24)))
    # cv2.imshow('src', src)
    # cv2.imshow('res', res)
    cv2.imwrite(save, res)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def resize_4096(src, save):
    h, w, c = src.shape
    res = cv2.resize(src, (int(w * 4), int(h * 4)))
    # cv2.imshow('src', src)
    # cv2.imshow('res', res)
    cv2.imwrite(save, res)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def resize_1000(src, save):
    h, w, c = src.shape
    res = cv2.resize(src, (int(w - 24), int(h - 24)))
    # cv2.imshow('src', src)
    # cv2.imshow('res', res)
    cv2.imwrite(save, res)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    src_path = r"E:\data\yantian\train\img\tif"
    save_path = r"E:\data\yantian\train\img\tif_1000"

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    for filename in os.listdir(src_path):
        if filename.endswith('.tif'):
            try:
                file_path = src_path + '/' + filename
                src = cv2.imread(file_path)
                # resize_4096(src, save_path + '/' + filename)
                # resize_1024(src, save_path + '/' + filename)
                resize_1000(src, save_path + '/' + filename)
            except:
                print(filename)
