#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/6
@Author  : AnNing
"""
import os

import matplotlib.pyplot as plt
import numpy as np
from lib.lib_read_ssi import FY4ASSI, FY3DSSI
from lib.lib_database import add_result_data, exist_result_data
from lib.lib_proj import fill_points_2d_nan
from lib.lib_constant import BASEMAP_FY4_4KM


def plot_image_disk(*args, **kwargs):
    resultid = kwargs.get('resultid')
    if resultid is not None and 'fy4a' in resultid.lower():
        plot_fy4a_image_disk(*args, **kwargs)
    else:
        print('plot_image_disk不支持此分辨率{}'.format(resultid))


def plot_fy4a_image_disk(data, out_file='test.jpg', resolution_type='4km', vmin=0, vmax=1000, **kwargs):
    if '4km' in resolution_type.lower():
        ditu = plt.imread(BASEMAP_FY4_4KM)
        row, col, _ = ditu.shape
        fig = plt.figure(figsize=(col / 100, row / 100), dpi=100)
        fig.figimage(ditu)
    else:
        print('plot_image_disk 不支持此分辨率: {}'.format(resolution_type))
        return

    fig.figimage(data, vmin=vmin, vmax=vmax, cmap='jet', alpha=0.7)
    fig.patch.set_alpha(0)
    plt.savefig(out_file, transparent=True)
    fig.clear()
    plt.close()
    print("监测到数据的最小值和最大值：{}， {}".format(np.nanmin(data), np.nanmax(data)))
    print('>>> :{}'.format(out_file))


def plot_fy3_image_map(data, out_file='test.jpg', resolution_type='1km', vmin=0, vmax=2, **kwargs):
    if '1km' in resolution_type.lower():
        row, col = data.shape
    else:
        print('plot_fy3_image_map:不支持的分辨率:{}'.format(resolution_type))
        return

    fig = plt.figure(figsize=(col / 100, row / 100), dpi=100)
    fig.figimage(data, vmin=vmin, vmax=vmax, cmap='jet')
    fig.patch.set_alpha(0)
    plt.savefig(out_file, transparent=True)
    fig.clear()
    plt.close()
    print("监测到数据的最小值和最大值：{}， {}".format(np.nanmin(data), np.nanmax(data)))
    print('>>> :{}'.format(out_file))


def plot_image_map(*args, **kwargs):
    resultid = kwargs['resultid']
    if 'fy4a' in resultid.lower():
        plot_fy4_image_map(*args, **kwargs)
    elif 'fy3d' in resultid.lower():
        plot_fy3_image_map(*args, **kwargs)
    else:
        print('plot_image_map:不支持的卫星和分辨率: {}'.format(resultid))


def plot_fy4_image_map(data, out_file='test.jpg', resolution_type='4km', vmin=0, vmax=1000, interp=3, **kwargs):
    if '4km' in resolution_type.lower():
        projlut = FY4ASSI.get_lonlat_projlut_4km()
    elif '1kmcorrect' in resolution_type.lower():
        projlut = FY4ASSI.get_lonlat_projlut_1km()
        interp = 0
    elif '1km' in resolution_type.lower():
        projlut = FY4ASSI.get_lonlat_projlut_1km()
    else:
        raise ValueError('plot_image_map 不支持此分辨率: {}'.format(resolution_type))
    row, col = projlut['row_col']
    image_data = np.full((row, col), np.nan, dtype=np.float32)
    proj_i = projlut['prj_i']
    proj_j = projlut['prj_j']
    pre_i = projlut['pre_i']
    pre_j = projlut['pre_j']

    # 投影方格以外的数据过滤掉
    valid_index = np.logical_and.reduce((proj_i >= 0, proj_i < row,
                                         proj_j >= 0, proj_j < col))
    proj_i = proj_i[valid_index]
    proj_j = proj_j[valid_index]
    pre_i = pre_i[valid_index]
    pre_j = pre_j[valid_index]

    image_data[proj_i, proj_j] = data[pre_i, pre_j]
    fig = plt.figure(figsize=(col / 100, row / 100), dpi=100)

    for i in range(interp):
        fill_points_2d_nan(image_data)

    fig.figimage(image_data, vmin=vmin, vmax=vmax, cmap='jet')
    fig.patch.set_alpha(0)
    plt.savefig(out_file, transparent=True)
    fig.clear()
    plt.close()
    print("监测到数据的最小值和最大值：{}， {}".format(np.nanmin(data), np.nanmax(data)))
    print('>>> :{}'.format(out_file))


def plot_map_full(in_file, vmin=0, vmax=1000, resultid='', planid='', datatime='', resolution_type=None):
    print('plot_map_orbit <<<:{}'.format(in_file))
    if not os.path.isfile(in_file):
        print('数据不存在:{}'.format(in_file))
        return
    dir_ = os.path.dirname(in_file)
    in_filename = os.path.basename(in_file)

    if 'fy4a' in resultid.lower():
        datas = FY4ASSI(in_file)
    elif 'fy3d' in resultid.lower():
        datas = FY3DSSI(in_file)
    else:
        print('不支持的卫星：{}'.format(resultid))
        return
    datas_ = {
        'Itol': datas.get_ssi,
        'Ib': datas.get_ib,
        'Id': datas.get_id,
        'G0': datas.get_g0,
        'Gt': datas.get_gt,
        'DNI': datas.get_dni,
    }
    for element in datas_.keys():
        try:
            data = datas_[element]()
        except Exception as why:
            print(why)
            print('读取数据错误:{}'.format(element))
            data = None

        if data is not None:
            # 快视图绘制
            area_type = 'Full_DISK'
            out_filename1 = in_filename + '_{}_{}.PNG'.format(area_type, element)
            out_file1 = os.path.join(dir_, out_filename1)

            try:
                if not os.path.isfile(out_file1):
                    plot_image_disk(data, out_file=out_file1, resultid=resultid, resolution_type=resolution_type,
                                    vmin=vmin, vmax=vmax)
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

            # 等经纬图绘制
            area_type = 'Full_LATLON'
            out_filename2 = in_filename + '_{}_{}.PNG'.format(area_type, element)
            out_file2 = os.path.join(dir_, out_filename2)
            # try:
            if not os.path.isfile(out_file2):
                plot_image_map(data, out_file=out_file2, resultid=resultid, resolution_type=resolution_type,
                               vmin=vmin,
                               vmax=vmax)
            else:
                print('文件已经存在，跳过:{}'.format(out_file2))
            # 入库
            if os.path.isfile(out_file2) and not exist_result_data(resultid=resultid, datatime=datatime,
                                                                   resolution_type=resolution_type,
                                                                   element=element, area_type=area_type):
                add_result_data(resultid=resultid, planid=planid, address=out_file2, datatime=datatime,
                                resolution_type=resolution_type, area_type=area_type, element=element)
            # except Exception as why:
            #     print(why)
            #     print('绘制{}图像错误:{}'.format(area_type, out_file2))


if __name__ == '__main__':
    i_dir = r'D:\SourceData\RemoteSensing\FY4A\AGRI\L2\SSI\20190630'
    i_filename = 'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_20190630000000_20190630001459_4000M_V0001.NC'
    i_file = os.path.join(i_dir, i_filename)
    plot_map_full(i_file)
