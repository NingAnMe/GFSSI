#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/12
@Author  : AnNing
"""
import os
import h5py
import numpy as np

from lib.lib_read_ssi import FY4ASSI, FY3DSSI
from lib.lib_constant import FULL_VALUE
from lib.lib_get_index_by_lonlat import get_data_by_index, get_area_index


def _write_out_file(out_file, result):
    out_dir = os.path.dirname(out_file)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    valid_count = 0
    for key in result:
        if result[key] is None:
            continue
        else:
            valid_count += 1
    if valid_count == 0:
        print('没有足够的有效数据，不生成结果文件')
        return

    # try:
    compression = 'gzip'
    compression_opts = 5
    shuffle = True
    with h5py.File(out_file, 'w') as hdf5:
        for dataset in result.keys():
            data = result[dataset]
            if data is not None:
                data[np.isnan(data)] = FULL_VALUE
                hdf5.create_dataset(dataset,
                                    dtype=np.float32, data=result[dataset], compression=compression,
                                    compression_opts=compression_opts,
                                    shuffle=shuffle)
    print('成功生成HDF文件 >>>:{}'.format(out_file))
    # except Exception as why:
    #     print(why)
    #     print('HDF写入数据错误')
    #     os.remove(out_file)


def area(in_file, out_file, left_up_lon=None, left_up_lat=None, right_down_lon=None, right_down_lat=None,
         resolution_type=None, resultid=None):
    print('area <<< :{}'.format(in_file))
    if not os.path.isfile(in_file):
        print('数据不存在:{}'.format(in_file))
        return

    out_path = os.path.dirname(out_file)
    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    if 'fy4a' in resultid.lower() and '4km' in resolution_type.lower():
        loader = FY4ASSI
        lons = FY4ASSI.get_longitude_4km()
        lats = FY4ASSI.get_latitude_4km()
    elif 'fy4a' in resultid.lower() and '1km' in resolution_type.lower():
        loader = FY4ASSI
        lons = FY4ASSI.get_longitude_1km()
        lats = FY4ASSI.get_latitude_1km()
    elif 'fy3d' in resultid.lower() and '1km' in resolution_type.lower():
        loader = FY3DSSI
        lons = FY3DSSI.get_longitude_1km()
        lats = FY3DSSI.get_latitude_1km()
    else:
        raise ValueError('不支持此分辨率: {}'.format(resolution_type))

    data_all = {
        'SSI': None,
        'DirSSI': None,
        'DifSSI': None,
        'G0': None,
        'Gt': None,
        'DNI': None,
        'Latitude': None,
        'Longitude': None,
    }

    try:
        datas = loader(in_file)
        data_get = {
            'SSI': datas.get_ssi,
            'DirSSI': datas.get_ib,
            'DifSSI': datas.get_id,
            'G0': datas.get_g0,
            'Gt': datas.get_gt,
            'DNI': datas.get_dni,
            'Latitude': lats,
            'Longitude': lons,
        }
        (row_min, row_max), (col_min, col_max) = get_area_index(lons=lons, lats=lats, left_up_lon=left_up_lon,
                                                                left_up_lat=left_up_lat, right_down_lon=right_down_lon,
                                                                right_down_lat=right_down_lat)
        for dataname in data_all:
            data_all[dataname] = get_data_by_index(data=data_get[dataname](), row_min=row_min, row_max=row_max,
                                                   col_min=col_min, col_max=col_max)
    except Exception as why:
        print(why)
        print('选取数据过程出错，文件为：{}'.format(in_file))
        return

    try:
        _write_out_file(out_file, data_all)
    except Exception as why:
        print(why)
        print('输出结果文件错误')
        return
