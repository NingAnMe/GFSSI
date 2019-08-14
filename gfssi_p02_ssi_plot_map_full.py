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


def plot_image_disk(data, out_file='test.jpg', res='4km'):
    ditu = plt.imread('Aid/ditu_{}.png'.format(res.lower()))
    row, col, _ = ditu.shape
    fig = plt.figure(figsize=(col / 100, row / 100), dpi=100)
    fig.figimage(ditu)
    fig.figimage(data, vmin=0, vmax=1000, cmap='jet', alpha=0.7)
    fig.patch.set_alpha(0)
    plt.savefig(out_file, transparent=True)
    print('>>> :{}'.format(out_file))


def plot_image_map(data, out_file='test.jpg', res='4km'):
    projlut_file = 'Aid/lonlat_projlut_{}_4509row_4356col.hdf'.format(res.lower())
    projlut = FY4ASSI.get_lonlat_projlut(projlut_file)
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
    fig = plt.figure(figsize=(col/100, row/100), dpi=100)
    fig.figimage(image_data, vmin=0, vmax=1000, cmap='jet')
    fig.patch.set_alpha(0)
    plt.savefig(out_file, transparent=True)
    print('>>> :{}'.format(out_file))


def plot_map_full(in_file, res='4km'):
    print('plot_map_orbit <<<:{}'.format(in_file))
    if not os.path.isfile(in_file):
        print('数据不存在:{}'.format(in_file))
        return
    dir_ = os.path.dirname(in_file)
    in_filename = os.path.basename(in_file)

    datas = FY4ASSI(in_file)
    datas_ = {
        'Itol': datas.get_ssi,
        'Ib': datas.get_ib,
        'Id': datas.get_id,
        'G0': datas.get_g0,
        'Gt': datas.get_gt,
        'DNI': datas.get_dni,
    }
    for dataname in datas_.keys():
        try:
            data = datas_[dataname]()
        except Exception as why:
            print(why)
            print('读取数据错误:{}'.format(dataname))
            data = None

        if data is not None:
            # 快视图绘制
            out_filename1 = in_filename + '_{}.jpg'.format(dataname)
            out_file1 = os.path.join(dir_, out_filename1)
            try:
                plot_image_disk(data, out_file=out_file1, res=res)
            except Exception as why:
                print(why)
                print('绘制图像错误:{}'.format(out_file1))

            # 等经纬图绘制
            out_filename2 = in_filename + '_latlon_{}.png'.format(dataname)
            out_file2 = os.path.join(dir_, out_filename2)
            try:
                plot_image_map(data, out_file=out_file2)
            except Exception as why:
                print(why)
                print('绘制图像错误:{}'.format(out_file2))


if __name__ == '__main__':
    i_dir = r'D:\SourceData\RemoteSensing\FY4A\AGRI\L2\SSI\20190630'
    i_filename = 'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_20190630000000_20190630001459_4000M_V0001.NC'
    i_file = os.path.join(i_dir, i_filename)
    plot_map_full(i_file)