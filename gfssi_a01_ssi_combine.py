#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/15
@Author  : AnNing
"""
from __future__ import print_function, division

import logging
import os
import h5py
import numpy as np
import pandas as pd
from netCDF4 import Dataset
import logging


def main(yaml_file):
    """
    :param yaml_file: (str) 接口yaml文件
    :return:
    """
    # ######################## 初始化 ###########################
    # 加载接口文件
    logging.debug("main: interface file <<< {}".format(yaml_file))

    interface_config = load_yaml_file(yaml_file)
    i_pair = interface_config['INFO']['pair']  # 卫星+传感器 or 卫星+传感器_卫星+传感器（str）
    i_nc_type = interface_config['INFO']['type']
    i_in_files = interface_config['PATH']['ipath']  # 待处理文件绝对路径列表（list）
    i_out_path = interface_config['PATH']['opath']  # 输出文件绝对路径（str）
    i_ymd = interface_config['INFO']['ymd']

    # ######################## 开始处理 ###########################
    # ######################## 加载数据 ###########################
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
