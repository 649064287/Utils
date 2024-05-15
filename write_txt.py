import os

image_path = r"D:\data\sample_farm2\img"
poly_path = r"D:\data\sample_farm2\lab"
# line_path = r'Z:\Project_Data\tongxiang_building\20210702_label'
txt_path = r"D:\data\sample_farm2\train.txt"

# 写训练集
f = open(txt_path, "w")
files = os.listdir(image_path)
for file in files:
    if file[-4:] == ".tif":
        # if file.find(".tif") != -1 and file.find("tif.") == -1:
        image_name = os.path.join(image_path, file)
        poly_name = os.path.join(poly_path, file)
        # line_name = os.path.join(line_path, file)
        # f.write(image_name + "\n")
        f.write(image_name + " " + poly_name + "\n")
        # f.write(image_name + " " + line_name + "\n")
        # f.write(image_name + " " + poly_name + " " + line_name + "\n")

f.close()

# # 写测试集
# f = open(txt_path, "w")
# files = os.listdir(image_path)
# for file in files:
#     if file.find(".tif") != -1 and file.find("tif.") == -1:
#         image_name = os.path.join(image_path, file)
#         f.write(image_name + " " + "\n")
#
# f.close()
