#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/10/8 10:12
# @Author  : AnNing
import os
import numpy as np

from lib.lib_read_ssi import FY4ASSI
from lib.lib_hdf5 import write_out_file

from history import get_files_by_date


def extract_from_array(array, index, n):
    """
    在矩阵数据中提取等宽矩阵
    :param array: 2维矩阵
    :param index: 中心点的索引
    :param n: 提取数据的大小，n为奇数
    :return: 矩阵
    """
    assert n % 2 == 1, 'n必须为奇数'

    row_min = index[0] - n // 2
    row_max = row_min + n
    col_min = index[1] - n // 2
    col_max = col_min + n
    return array[row_min:row_max, col_min:col_max]


in_path = '/home/gfssi/GFData/SSIData/FY4A/SSI_4KMCorrect/Full/Orbit'
out_path = '/home/gfssi/GFData/SSIForecastData/FY4A/SSI_4KMCorrect/Full/Orbit'

infiles = get_files_by_date(in_path, '20190101', '20191231', 'nc', r'.*_NOM_(\d{8})')
infiles.sort()

n = 63
data_length = len(infiles)

# result = {
#     'data_x': (np.zeros((data_length, n, n), dtype=np.float32), np.float32),
#     'data_g0': (np.zeros((data_length, n, n), dtype=np.float32), np.float32),
#     'data_y': (np.zeros((data_length, 1), dtype=np.float32), np.float32),
#     'timestamp': (np.zeros((data_length, 1), dtype=np.float64), np.float64),
# }

for i, infile in enumerate(infiles):
    data_loader = FY4ASSI(infile)
    itol = data_loader.get_ssi()
    g0 = data_loader.get_g0()
    date = data_loader.get_date_time_orbit(infile)

    index = (601, 1730)  # 杭州 120.1647, 30.2261

    result = {
        'data_x': (np.zeros((1, n, n), dtype=np.float32), np.float32),
        'data_g0': (np.zeros((1, n, n), dtype=np.float32), np.float32),
        'data_y': (np.zeros((1, 1), dtype=np.float32), np.float32),
        'timestamp': (np.zeros((1, 1), dtype=np.float64), np.float64),
    }
    data_y = extract_from_array(itol, index, 1)
    print(data_y)

    if np.isnan(data_y).all():
        continue
    result['data_y'][0][0] = data_y

    data_x = extract_from_array(itol, index, n)
    data_x[np.isnan(data_x)] = 0
    result['data_x'][0][0] = data_x

    data_g0 = extract_from_array(g0, index, n)
    data_g0[np.isnan(data_g0)] = 0
    result['data_g0'][0][0] = data_g0

    result['timestamp'][0][0] = date.timestamp()

    outfile = infile.replace(in_path, out_path)
    if not os.path.isdir(out_path):
        os.makedirs(out_path)
    write_out_file(outfile, result)
