import os
import numpy as nup
from netCDF4 import Dataset
import matplotlib.pyplot  as plt
import matplotlib

# directory_name = r"C:\Users\64906\Desktop\solar\2018"

def get_solar(path):
    # Data2 = []
    # for filename in os.listdir(path):
    #     nc_file = path + "\\" + filename
    nc_obj = Dataset(path)
    data = nc_obj['monthly_global_radiation'][:]
    # print(data)
    # Data2.append(data)
    return data

# get_solar(directory_name)