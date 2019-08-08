#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/15
@Author  : AnNing
"""
from __future__ import print_function, division

import os
import h5py
import numpy as np

from lib.lib_read import FY4ASSI
from lib.lib_constant import FULL_VALUE


def add_data(data, data_tem):
    if data_tem is None:
        return data
    if data is None:
        data = data_tem
    else:
        index_add = np.logical_and(np.isfinite(data_tem), np.isfinite(data))
        data[index_add] += data_tem[index_add]
        index_equal = np.logical_and(np.isfinite(data_tem), np.isnan(data))
        data[index_equal] = data_tem[index_equal]
    return data


def _write_out_file(out_file, result):
    out_dir = os.path.dirname(out_file)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    try:
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
        print('>>> 成功生成HDF文件{}'.format(out_file))
    except Exception as why:
        print(why)
        print('HDF写入数据错误')
        os.remove(out_file)


def combine(in_files, out_file, day=False):
    out_path = os.path.dirname(out_file)
    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    data_all = {
        'SSI': None,
        'DirSSI': None,
        'DifSSI': None,
        'G0': None,
        'Gt': None,
        'DNI': None,
    }

    for in_file in in_files:
        try:
            datas = FY4ASSI(in_file)
            data_get = {
                'SSI': datas.get_ssi,
                'DirSSI': datas.get_ib,
                'DifSSI': datas.get_id,
                'G0': datas.get_g0,
                'Gt': datas.get_gt,
                'DNI': datas.get_dni,
            }
            for dataname in data_all:
                data_all[dataname] = add_data(data_all[dataname], data_get[dataname]())
        except Exception as why:
            print(why)
            print('合成数据过程出错，文件为：{}'.format(in_file))
            continue

    # 从时次产品转为日产品的时候，单位变为kw/m2
    try:
        if day:
            print('从时次产品转为日产品的时候，单位变为kw/m2')
            for dataname in data_all:
                data = data_all[dataname]
                if data is not None:
                    data_all[dataname] = data * 0.001
    except Exception as why:
        print(why)
        print('转换单位出错')

    try:
        _write_out_file(out_file, data_all)
    except Exception as why:
        print(why)
        print('输出结果文件错误')
        return
