#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/1
@Author  : AnNing
1、修改为矩阵运算
2、优化assignE
3、DEBUG函数assignTime，原来的函数直接在hour加8可能超过24
"""
import os
import sys
import h5py
import numpy as np
from lib.lib_read import FY4ASSI
from shutil import copyfile
from lib.lib_constant import FULL_VALUE
from datetime import datetime
from dateutil.relativedelta import relativedelta


def cos(x):
    return np.cos(np.radians(x))


def sin(x):
    return np.sin(np.radians(x))


def isleap(y):
    y = int(y)
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0


def calDoy(y, m, d):
    Doy = 0
    a = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if isleap(y):
        a[1] = 29
    for x in a[0:m - 1]:
        Doy += x
    return Doy + d


def calDelta(Doy):
    # print "360/365*(284 + Doy) is %f" % (360.0/365*(284 + Doy))
    return 23.45 * sin(360.0 / 365 * (284 + Doy))


def calOmega(hr, min, lon, E):
    TT = hr + min / 60.0 + 4 * (lon - 120) / 60.0 + E / 60.0
    return (TT - 12) * 15


def calCosThetaz(lat, Delta, Omega):
    return cos(lat) * cos(Delta) * cos(Omega) + sin(lat) * sin(Delta)


def calG0(Doy, CosThetaz):
    return 1366.1 * (1 + 0.033 * cos(360.0 / 365 * Doy)) * CosThetaz


def calRb(lat, Beta, Delta, Omega, CosThetaz):
    return (cos(lat - Beta) * cos(Delta) * cos(Omega) + sin(lat - Beta) * sin(Delta)) / CosThetaz


def calGt(Ib, Id, Ai, Rb, Beta, Itol):
    return (Ib + Id * Ai) * Rb + Id * (1 - Ai) * (1 + cos(Beta)) / 2.0 + Itol * 0.2 * (1 - cos(Beta)) / 2.0

def assignTime(ymdhms):
    """
    DEBUG函数assignTime，原来的函数直接在hour加8可能超过24
    :param ymdhms:
    :return:
    """
    date = datetime.strptime(ymdhms, '%Y%m%d%H%M%S')
    date += relativedelta(hours=8)  # 修改时间为北京时
    datestrf = date.strftime('%Y-%m-%d-%H-%M-%S')
    y, m, d, h, mm, s = datestrf.split('-')
    return y, m, d, h, mm

def assignE(y, m, d):
    """
    assignE
    :param y:
    :param m:
    :param d:
    :return:
    """
    y = int(y)
    m = int(m)
    d = int(d)
    if isleap(y):
        e_file = 'step2/er.txt'
    else:
        e_file = 'step2/ep.txt'
    e_data = np.loadtxt(e_file)
    md = int('{:02d}{:02d}'.format(m, d))

    index = np.where(e_data == md)
    row = index[0]
    if row.size != 0:
        return e_data[row, 1]
    else:
        raise ValueError('没有找到E值： {}'.format((y, m, d)))


def _write_out_file(in_file, out_file, result):
    out_dir = os.path.dirname(out_file)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    if not os.path.isfile(out_file):
        copyfile(in_file, out_file)

    try:
        compression = 'gzip'
        compression_opts = 5
        shuffle = True
        with h5py.File(out_file, 'a') as hdf5:
            for dataset in result.keys():
                hdf5.create_dataset(dataset,
                                    dtype=np.float32, data=result[dataset], compression=compression,
                                    compression_opts=compression_opts,
                                    shuffle=shuffle)
        print('成功生成HDF文件{}'.format(out_file))
    except Exception as why:
        print(why)
        os.remove(out_file)


def itcal(in_file, out_file):
    # 如果原来的整点数据不存在，直接使用G0进行补充
    # 如果原来的整点数据存在，使用G0进行校正

    beta = 35.0  # 常量

    try:
        datas = FY4ASSI(in_file)
    except Exception as why:
        print(why)
        print('初始化FY4A SSI读取类错误')
        return
    ymdhms = datas.get_date_time()
    y, m, d, hr, minus = assignTime(ymdhms)
    e = assignE(y, m, d)
    doy = calDoy(y, m, d)
    delta = calDelta(doy)

    try:
        lons = FY4ASSI.get_longitude()
        lats = FY4ASSI.get_latitude()
    except Exception as why:
        print(why)
        print('读取lons和lats错误')
        return

    Omega = calOmega(hr, minus, lons, e)
    cos_the_taz = calCosThetaz(lats, delta, Omega)
    G0 = calG0(doy, cos_the_taz)
    print('G0')
    print(np.nanmin(G0), np.nanmax(G0))
    print((G0 > 0).sum())
    index_invalid_g0 = np.logical_or(G0 >= 1400, G0 <= 0)  # ########################## G0的无效值赋值为nan
    G0[index_invalid_g0] = np.nan

    # 校正总直散数据
    if os.path.isfile(in_file):

        try:
            Itol = datas.get_ssi()
            Ib = datas.get_dirssi()
            Id = datas.get_difssi()
        except Exception as why:
            print(why)
            print('读取ssi，dirssi和difssi错误')
            return

        # 将G0 >= 1400, G0 <= 0的值置为nan
        Itol[index_invalid_g0] = np.nan
        Ib[index_invalid_g0] = np.nan
        Id[index_invalid_g0] = np.nan

        # 校正G0有效，但是Itol无效的数据
        index_invalid = np.logical_or(Itol > G0, np.logical_and(np.isnan(Itol), np.isfinite(G0)))
        Itol[index_invalid] = 0.5 * G0[index_invalid]
        Ib[index_invalid] = 0.3 * Itol[index_invalid]
        Id[index_invalid] = 0.7 * Itol[index_invalid]
    else:
        Itol = 0.5 * G0
        Ib = 0.3 * Itol
        Id = 0.7 * Itol

    # 计算Gt和DNI
    Rb = calRb(lats, beta, delta, Omega, cos_the_taz)
    Ai = Ib / G0
    Gt = calGt(Ib, Id, Ai, Rb, beta, Itol)
    DNI = Ib / cos_the_taz

    # 校正Gt
    index_invalid_gt = np.logical_and(Gt < 0, np.isfinite(G0))
    Gt[index_invalid_gt] = 0.8 * G0[index_invalid_gt]

    # 输出数据
    result = {'G0': G0, 'Gt': Gt, 'DNI': DNI, 'SSI': Itol, 'DirSSI': Ib, 'DifSSI': Id}

    try:
        _write_out_file(in_file, out_file, result)
    except Exception as why:
        print(why)
        print('输出结果文件错误')
        return


if __name__ == '__main__':
    #     in_dir = '/home/gfssi/GFData/Source/FY4A+AGRI/SSI_4KM/Orbit/20190630/'
    # out_dir = '/home/gfssi/GFData/Result/FY4A+AGRI/SSI_4KM/Orbit/20190630/'
    # filenames = os.listdir(in_dir)
    # filenames.sort()
    #
    # for file_name in filenames:
    #     if file_name[-2:] != 'NC':
    #         continue
    #     else:
    #         in_file = os.path.join(in_dir, file_name)
    #         out_file = os.path.join(out_dir, file_name)
    #         itcal(in_file, out_file)
    in_dir = '/home/gfssi/GFData/Result/FY4A+AGRI/SSI_4KM/Orbit/20190630'
    out_dir = '/home/gfssi/GFData/Result/FY4A+AGRI/SSI_4KM/Orbit/20190630'
    file_name = 'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_20190630000000_20190630001459_4000M_V0001.NC'
    in_file = os.path.join(in_dir, file_name)
    out_file = os.path.join(out_dir, file_name)
    itcal(in_file, out_file)
