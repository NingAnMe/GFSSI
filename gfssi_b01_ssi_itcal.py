#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/1
@Author  : AnNing
功能：
1、计算G0、Gt、DNI
2、补全缺失的整点时次数据的Itol、Ib、Id

优化
1、修改为矩阵运算
2、优化assignE
3、DEBUG函数assignTime，原来的函数直接在hour加8可能超过24
"""
import os

import h5py
import numpy as np
from dateutil.relativedelta import relativedelta

from lib.lib_constant import FULL_VALUE, ER_TXT, EP_TXT
from lib.lib_read_ssi import FY4ASSI
from lib.lib_database import add_result_data, exist_result_data


G0_Correct = 0.75  # 使用G0订正Itol的系数


def cos(x):
    return np.cos(np.radians(x))


def sin(x):
    return np.sin(np.radians(x))


def isleap(y):
    y = int(y)
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0


def calDoy(y, m, d):
    y = int(y)
    m = int(m)
    d = int(d)
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


def assignTime(date):
    """
    DEBUG函数assignTime，原来的函数直接在hour加8可能超过24
    :param date:
    :return:
    """
    date += relativedelta(hours=8)  # 修改时间为北京时
    datestrf = date.strftime('%Y-%m-%d-%H-%M-%S')
    y, m, d, h, mm, s = datestrf.split('-')
    return [int(i) for i in (y, m, d, h, mm)]


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
        e_file = ER_TXT
    else:
        e_file = EP_TXT
    e_data = np.loadtxt(e_file)
    md = int('{:02d}{:02d}'.format(m, d))

    index = np.where(e_data == md)
    row = index[0]
    if row.size != 0:
        return e_data[row, 1]
    else:
        raise ValueError('没有找到E值： {}'.format((y, m, d)))


def _write_out_file(out_file, result):
    valid_count = 0
    for key in result:
        if result[key] is None:
            continue
        else:
            valid_count += 1
    if valid_count == 0:
        print('没有足够的有效数据，不生成结果文件')
        return

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


def itcal(in_file, out_file, resultid=None, planid=None, datatime=None, resolution_type=None):
    # 如果原来的整点数据不存在，直接使用G0进行补充
    # 如果原来的整点数据存在，使用G0进行校正
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

    beta = 35.0  # 常量

    try:
        datas = FY4ASSI(in_file)
    except Exception as why:
        print(why)
        print('初始化FY4A SSI读取类错误')
        return
    date_time = FY4ASSI.get_date_time_orbit(in_file)
    y, m, d, hr, minus = assignTime(date_time)
    e = assignE(y, m, d)
    doy = calDoy(y, m, d)
    delta = calDelta(doy)
    print(delta)
    try:
        lons = FY4ASSI.get_longitude_4km()
        lats = FY4ASSI.get_latitude_4km()
    except Exception as why:
        print(why)
        print('读取lons和lats错误')
        return

    DQF = np.ones_like(lons, dtype=np.int8)  # 标识数据集

    Omega = calOmega(hr, minus, lons, e)
    cos_the_taz = calCosThetaz(lats, delta, Omega)
    G0 = calG0(doy, cos_the_taz)
    print('G0')
    print(np.nanmin(G0), np.nanmax(G0))
    print((G0 > 0).sum())
    index_invalid_g0 = np.logical_or(G0 >= 1400, G0 <= 0)  # ########################## G0的无效值赋值为nan
    G0[index_invalid_g0] = np.nan
    if np.isnan(G0).all():
        print('Warning::::::::没有有效的G0数据，不生产数据')
        return

    # G0无效
    DQF[index_invalid_g0] = 0

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

        # Itol 有效
        index_valid_itol = np.logical_and(np.isfinite(Itol), Itol < G0)
        DQF[index_valid_itol] = 1

        # 校正G0有效，但是Itol无效的数据
        index_invalid_itol = np.logical_or(Itol > G0, np.logical_and(np.isnan(Itol), np.isfinite(G0)))
        Itol[index_invalid_itol] = G0_Correct * G0[index_invalid_itol]
        Ib[index_invalid_itol] = 0.3 * Itol[index_invalid_itol]
        Id[index_invalid_itol] = 0.7 * Itol[index_invalid_itol]
        DQF[index_invalid_itol] = 2
    else:
        Itol = G0_Correct * G0
        Ib = 0.3 * Itol
        Id = 0.7 * Itol

    # 计算Gt和DNI
    Rb = calRb(lats, beta, delta, Omega, cos_the_taz)
    Ai = Ib / G0
    Gt = calGt(Ib, Id, Ai, Rb, beta, Itol)
    DNI = Ib / cos_the_taz

    # 校正Gt
    index_invalid_gt = np.logical_and(Gt < 0, np.isfinite(G0))
    Gt[index_invalid_gt] = 0.75 * G0[index_invalid_gt]
    DQF[index_invalid_gt] = 3
    Gt[lats < 0] = np.nan  # 20191121 AnNing 根据用户需求，Gt的数据只生产北半球

    # 输出数据
    result = {'G0': G0, 'Gt': Gt, 'DNI': DNI, 'SSI': Itol, 'DirSSI': Ib, 'DifSSI': Id, 'DQF': DQF}

    try:
        _write_out_file(out_file, result)
        if os.path.isfile(out_file) and not exist_result_data(resultid=resultid, datatime=datatime,
                                                              resolution_type=resolution_type,
                                                              area_type=area_type):
            add_result_data(resultid=resultid, planid=planid, address=out_file, datatime=datatime,
                            resolution_type=resolution_type, area_type=area_type, element=None)
    except Exception as why:
        print(why)
        print('输出结果文件错误')
        return

# if __name__ == '__main__':
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
# in_dir = '/home/gfssi/GFData/Result/FY4A+AGRI/SSI_4KM/Orbit/20190630'
# out_dir = '/home/gfssi/GFData/Result/FY4A+AGRI/SSI_4KMCorrect/Orbit/20190630'
# file_name = 'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_20190630000000_20190630001459_4000M_V0001.NC'
# in_file = os.path.join(in_dir, file_name)
# out_file = os.path.join(out_dir, file_name)
# itcal(in_file, out_file)
