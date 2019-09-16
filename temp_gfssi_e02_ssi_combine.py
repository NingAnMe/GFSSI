#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/15
@Author  : AnNing
"""
from __future__ import print_function, division

import os
import re

import h5py
import numpy as np

from lib.lib_read_ssi import FY4ASSI
from lib.lib_constant import FULL_VALUE


def add_data(data, data_tem):
    """
    combine太阳能数据
    :param data:
    :param data_tem:
    :return:
    """
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

    valid_count = 0
    for key in result:
        if result[key] is None:
            continue
        else:
            valid_count += 1
    if valid_count == 0:
        print('没有足够的有效数据，不生成结果文件')
        return

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


def combine_full(in_files, out_file, day=False):
    """
    :param in_files:
    :param out_file:
    :param day: 是否日合成，因为日合成的时候，要改变数据的单位为KW/m2
    :return:
    """
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
        print('combine <<< :{}'.format(in_file))
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


def get_files_by_date(dir_path, time_start, time_end, ext=None, pattern=None):
    """
    :param dir_path: 文件夹
    :param time_start: 开始时间
    :param time_end: 结束时间
    :param ext: 后缀名, '.hdf5'
    :param pattern: 匹配时间的模式
    :return: list
    """
    files_found = []
    if pattern is not None:
        pattern = pattern
    else:
        pattern = r".*(\d{8})"

    for root, dirs, files in os.walk(dir_path):
        for file_name in files:
            if ext is not None:
                if '.' not in ext:
                    ext = '.' + ext
                if os.path.splitext(file_name)[1].lower() != ext.lower():
                    continue
            re_result = re.match(pattern, file_name)
            if re_result is not None:
                time_file = ''.join(re_result.groups())
            else:
                continue
            if int(time_start) <= int(time_file) <= int(time_end):
                files_found.append(os.path.join(root, file_name))
    files_found.sort()
    return files_found


if __name__ == '__main__':

    in_dir = '/FY4/FY4A/AGRI/L2/SSI/DISK/NOM/2018'
    pattern = r".*NOM_(\d{14})"
    in_files = get_files_by_date(in_dir, 20180101000000, 20181231245959, 'NC', pattern)
    print(len(in_files))
    in_files = in_files
    out_dir = '/home/gsics/anning/GFSSI'
    out_filename = 'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_2018_4000M_V0001.NC'
    out_file = os.path.join(out_dir, out_filename)
    combine_full(in_files, out_file, True)
