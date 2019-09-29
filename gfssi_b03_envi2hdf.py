#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/9/29 16:16
# @Author  : AnNing
import os
import sys

import numpy as np
from lib.lib_read_ssi import FY3DSSIENVI
from lib.lib_hdf5 import write_out_file
from lib.lib_constant import FULL_VALUE
from lib.lib_database import exist_result_data, add_result_data


def fy3d_envi2hdf(in_file, out_file, resultid, planid, datatime, resolution_type):
    area_type = 'Full_DISK'
    if os.path.isfile(out_file):
        print('数据已经存在: {}'.format(out_file))
        if not exist_result_data(resultid=resultid, datatime=datatime,
                                 resolution_type=resolution_type,
                                 area_type=area_type):
            add_result_data(resultid=resultid, planid=planid, address=out_file, datatime=datatime,
                            resolution_type=resolution_type, area_type=area_type, element=None)
        return
    print('<<< itcal: {}'.format(in_file))

    in_file_gc = in_file
    in_file_bc = in_file_gc.replace('Gc', 'Bc')
    in_file_dc = in_file_gc.replace('Gc', 'Dc')
    in_file_sz = in_file_gc.replace('Gc', 'Sz')

    ssi = FY3DSSIENVI(in_file_gc)
    dirssi = FY3DSSIENVI(in_file_bc)
    difssi = FY3DSSIENVI(in_file_dc)
    sz = FY3DSSIENVI(in_file_sz)

    result = {
        'SSI': (ssi.get_data(), np.float),
        'DirSSI': (dirssi.get_data(), np.float),
        'DifSSI': (difssi.get_data(), np.float),
        'Sz': (sz.get_data(), np.float)
    }

    write_out_file(out_file, result, full_value=FULL_VALUE)
    if os.path.isfile(out_file) and not exist_result_data(resultid=resultid, datatime=datatime,
                                                          resolution_type=resolution_type,
                                                          area_type=area_type):
        add_result_data(resultid=resultid, planid=planid, address=out_file, datatime=datatime,
                        resolution_type=resolution_type, area_type=area_type, element=None)
