#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/15
@Author  : AnNing
"""
from __future__ import print_function, division

import logging
import shutil
import os
import h5py
import numpy as np


from lib.lib_initialize import load_yaml_file


FULL_VALUE = 65532
LOG_FILE = 'a01.log'


def main(yaml_file):
    """
    :param yaml_file: (str) 接口yaml文件
    :return:
    """
    # ######################## 初始化 ###########################
    # 加载接口文件
    logging.debug("main: interface file <<< {}".format(yaml_file))

    # interface_config = load_yaml_file(yaml_file)
    # i_pair = interface_config['INFO']['pair']  # 卫星+传感器 or 卫星+传感器_卫星+传感器（str）
    # i_in_files = interface_config['PATH']['ipath']  # 待处理文件绝对路径列表（list）
    # i_out_file = interface_config['PATH']['opath']  # 输出文件绝对路径（str）
    # i_ymdhms_start = interface_config['INFO']['ymdhms_start']  # 日期 YYYYMMDDHHMMDD
    # i_ymdhms_end = interface_config['INFO']['ymdhms_end']  # 日期 YYYYMMDDHHMMDD
    # i_is_orbit = interface_config['INFO'].get('is_orbit', False)  # 如果是轨道产品转其他产品，这一项需要设置为True
    # i_log_path = interface_config['INFO']['log']

    # ######################## 开始处理 ###########################
    # ######################## 加载数据 ###########################
    i_pair = 'FY4A+AGRI'
    i_in_files = ['/home/gfssi/GFData/Result/FY4A+AGRI/SSI_4KM/Orbit/20190630/FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_20190630000000_20190630001459_4000M_V0001.NC',
                  '/home/gfssi/GFData/Result/FY4A+AGRI/SSI_4KM/Orbit/20190630/FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_20190630001500_20190630002959_4000M_V0001.NC'
                  ]
    i_out_file = '/home/gfssi/GFData/Result/FY4A+AGRI/SSI_4KM/Daily/20190630/FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_20190630000000_20190630235959_4000M_V0001.NC'
    i_is_orbit = True
    i_log_path = '/home/gfssi/GFData/log'

    log_file = os.path.join(i_log_path, LOG_FILE)

    in_files = np.sort(i_in_files)

    # 统计有效文件的数量
    file_count = 0
    for in_file in in_files:
        if os.path.isfile(in_file):
            logging.debug("main: data file <<< {}".format(in_file))
            file_count += 1
        else:
            continue
    if file_count == 0:
        logging.warning("***Warning***Don't have valid file, file count is {}".format(file_count))
        return

    # 如果是轨道产品合成日产品，单位需要转为 KW/m2，scalar=0.001
    if i_is_orbit:
        result = combine(in_files, i_out_file, scalar=0.001)
    else:
        result = combine(in_files, i_out_file)

    if result:
        logging.info("Out file >>>: {}".format(i_out_file))
    else:
        logging.error("Can't create the file: {}".format(i_out_file))


def combine(in_files, out_file, scalar=1., offset=0.):
    out_path = os.path.dirname(out_file)
    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    if not os.path.isfile(out_file):
        shutil.copyfile(in_files[0], out_file)

    ssi = None
    difssi = None
    dirssi = None
    for in_file in in_files:
        reader = FY4ASSI(in_file)
        ssi_tem = reader.read_ssi()
        difssi_tem = reader.read_difssi()
        dirssi_tem = reader.read_dirssi()

        ssi = add_data(ssi, ssi_tem)
        difssi = add_data(difssi, difssi_tem)
        dirssi = add_data(dirssi, dirssi_tem)

    # 从时次产品转为日产品的时候，单位变为kw/m2
    ssi = ssi * scalar + offset
    difssi = difssi * scalar + offset
    dirssi = dirssi * scalar + offset

    ssi[ssi == 0] = FULL_VALUE
    difssi[difssi == 0] = FULL_VALUE
    dirssi[dirssi == 0] = FULL_VALUE

    FY4ASSI.modify_data(out_file, ssi, difssi, dirssi)
    return True


def add_data(data, data_tem):
    if data_tem is None:
        return data
    if data is None:
        data = data_tem
    else:
        data += data_tem
    return data


class FY4ASSI(object):
    def __init__(self, in_file):
        self.in_file = in_file
        self.full_value = -999

    def read_ssi(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('SSI')[:]
            index = np.logical_or.reduce((dataset == self.full_value, dataset < 0, dataset > 1500))
            dataset[index] = 0
            return dataset

    def read_difssi(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('DifSSI')[:]
            index = np.logical_or.reduce((dataset == self.full_value, dataset < 0, dataset > 1500))
            dataset[index] = 0
            return dataset

    def read_dirssi(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('DirSSI')[:]
            index = np.logical_or.reduce((dataset == self.full_value, dataset < 0, dataset > 1500))
            dataset[index] = 0
            return dataset

    @staticmethod
    def modify_data(out_file, ssi, difssi, dirssi):
        with h5py.File(out_file, 'a') as hdf:
            for k, v in zip(('SSI', 'DifSSI', 'DirSSI'), (ssi, difssi, dirssi)):
                dataset = hdf.get(k)
                dataset[...] = v
                dataset.attrs.modify('units', np.array('KW/m2', dtype=h5py.special_dtype(vlen=str)))


if __name__ == '__main__':
    yaml = ''
    main(yaml)
