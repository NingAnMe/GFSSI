#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/6
@Author  : AnNing
"""
import os

import matplotlib.pyplot as plt
import numpy as np

from lib.lib_read_ssi import FY4ASSI
from lib.lib_database import add_result_data, exist_result_data
from lib.lib_constant import BASEMAP_FY4_4KM


def plot_fy4a_cloud_disk(data, out_file='test.jpg', resolution_type='4km'):
    if '4km' in resolution_type.lower():
        ditu = plt.imread(BASEMAP_FY4_4KM)
        row, col, _ = ditu.shape
        fig = plt.figure(figsize=(col / 100, row / 100), dpi=100)
        fig.figimage(ditu)
    else:
        print('plot_image_disk 不支持此分辨率: {}'.format(resolution_type))
        return

    fig.figimage(data)
    fig.patch.set_alpha(0)
    plt.savefig(out_file, transparent=True)
    fig.clear()
    plt.close()
    print("监测到数据的最小值和最大值：{}， {}".format(np.nanmin(data), np.nanmax(data)))
    print('>>> :{}'.format(out_file))


def plot_map_full(in_file, resultid='', planid='', datatime='', resolution_type=None):
    print('plot_map_orbit <<<:{}'.format(in_file))
    if not os.path.isfile(in_file):
        print('数据不存在:{}'.format(in_file))
        return

    if 'fy4a' in resultid.lower():
        rgb = FY4ASSI(in_file).get_rgb_ref()
    else:
        print('不支持的卫星：{}'.format(resultid))
        return

    element = "Cloud"
    area_type = "Full"

    out_file1 = in_file + ".PNG"
    try:
        if not os.path.isfile(out_file1):
            plot_fy4a_cloud_disk(rgb, out_file=out_file1, resolution_type=resolution_type)
        else:
            print('文件已经存在，跳过:{}'.format(out_file1))
        # 入库
        if os.path.isfile(out_file1) and not exist_result_data(resultid=resultid, datatime=datatime,
                                                               resolution_type=resolution_type,
                                                               element=element, area_type=area_type):
            add_result_data(resultid=resultid, planid=planid, address=out_file1, datatime=datatime,
                            resolution_type=resolution_type, area_type=area_type, element=element)
    except Exception as why:
        print(why)
        print('绘制{}图像错误:{}'.format(area_type, out_file1))


if __name__ == '__main__':
    i_dir = r'D:\SourceData\RemoteSensing\FY4A\AGRI\L2\SSI\20190630'
    i_filename = 'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_20190630000000_20190630001459_4000M_V0001.NC'
    i_file = os.path.join(i_dir, i_filename)
    plot_map_full(i_file)
