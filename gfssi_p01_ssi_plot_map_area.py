#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/13
@Author  : AnNing
"""
import os
import matplotlib.pyplot as plt
from lib.lib_read_ssi import FY4ASSI
from lib.lib_get_index_by_lonlat import get_area_index


def screenshot(in_file, out_file, row_min=None, row_max=None, col_min=None, col_max=None):
    """
    根据行列号截图
    :param in_file:
    :param out_file:
    :param row_min:
    :param row_max:
    :param col_min:
    :param col_max:
    :return:
    """
    data = plt.imread(in_file)
    data_new = data[row_min:row_max+1, col_min:col_max+1]
    row, col, _ = data.shape
    fig = plt.figure(figsize=(col/100, row/100), dpi=100)
    fig.figimage(data_new, vmin=0, vmax=1000, cmap='jet')
    fig.patch.set_alpha(0)
    plt.savefig(out_file, transparent=True)
    print('>>> :{}'.format(out_file))


def plot_map_area(in_file, out_file, left_up_lon=None, left_up_lat=None, right_down_lon=None, right_down_lat=None):
    print('plot_map_orbit <<<:{}'.format(in_file))
    if not os.path.isfile(in_file):
        print('数据不存在:{}'.format(in_file))
        return

    lons = FY4ASSI.get_longitude()
    lats = FY4ASSI.get_latitude()
    try:
        (row_min, row_max), (col_min, col_max) = get_area_index(lons=lons, lats=lats, left_up_lon=left_up_lon,
                                                                left_up_lat=left_up_lat, right_down_lon=right_down_lon,
                                                                right_down_lat=right_down_lat)
        screenshot(in_file, out_file, row_min=row_min, row_max=row_max, col_min=col_min, col_max=col_max)
    except Exception as why:
        print(why)
        print('绘制图像错误:{}'.format(out_file))


if __name__ == '__main__':
    i_dir = r'D:\SourceData\RemoteSensing\FY4A\AGRI\L2\SSI\20190630'
    i_filename = 'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_20190630000000_20190630001459_4000M_V0001.NC'
    i_file = os.path.join(i_dir, i_filename)
    plot_map_full(i_file)
