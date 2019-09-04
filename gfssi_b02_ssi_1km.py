#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/27
@Author  : AnNing
"""
import os
import h5py
import numpy as np
from scipy.interpolate import griddata
from lib.lib_read_ssi import FY4ASSI
from lib.lib_database import add_result_data, exist_result_data
from lib.lib_constant import FULL_VALUE


def lat2row(lat):
    row = int(((lat - 9.995) / 0.01))
    return row


def modiGHI(a, b, r):
    c = a * (1 + (r[0] * b / 1000 + r[1]) * 0.01)
    return c


def topoCorrection(radiaArray, deltHgt):
    ghi_ri = []
    rr = [[2.6036, 0.0365], [2.6204, 0.0365], [2.6553, 0.0362], [2.6973, 0.0356], [2.7459, 0.0343],
          [2.8012, 0.0324], [2.8616, 0.0299], [2.9236, 0.0257], [2.9870, 0.0204]]

    if len(deltHgt) == len(radiaArray):
        for i in range(len(deltHgt)):
            if i >= lat2row(52.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]), np.array(deltHgt[i]), rr[8]))
            if i >= lat2row(47.5) and i < lat2row(52.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]), np.array(deltHgt[i]), rr[7]))
            if i >= lat2row(42.5) and i < lat2row(47.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]), np.array(deltHgt[i]), rr[6]))
            if i >= lat2row(37.5) and i < lat2row(42.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]), np.array(deltHgt[i]), rr[5]))
            if i >= lat2row(32.5) and i < lat2row(37.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]), np.array(deltHgt[i]), rr[4]))
            if i >= lat2row(27.5) and i < lat2row(32.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]), np.array(deltHgt[i]), rr[3]))
            if i >= lat2row(22.5) and i < lat2row(27.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]), np.array(deltHgt[i]), rr[2]))
            if i >= lat2row(17.5) and i < lat2row(22.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]), np.array(deltHgt[i]), rr[1]))
            if i < lat2row(17.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]), np.array(deltHgt[i]), rr[0]))
    return np.array(ghi_ri)


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


def fy4a_ssi_4km_to_1km(in_file, out_file, resultid=None, planid=None, datatime=None, resolution_type=None):
    print('<<< itcal: {}'.format(in_file))

    area_type = 'Full_DISK'
    if os.path.isfile(out_file):
        print('数据已经存在: {}'.format(out_file))
        if not exist_result_data(resultid=resultid, datatime=datatime,
                                 resolution_type=resolution_type,
                                 area_type=area_type):
            add_result_data(resultid=resultid, planid=planid, address=out_file, datatime=datatime,
                            resolution_type=resolution_type, area_type=area_type)
        return

    datas = FY4ASSI(in_file)
    data_get = {
        'SSI': datas.get_ssi,
        'DirSSI': datas.get_ib,
        'DifSSI': datas.get_id,
        'G0': datas.get_g0,
        'Gt': datas.get_gt,
        'DNI': datas.get_dni,
    }
    result = {}
    elements = data_get.keys()

    lats_4km = FY4ASSI.get_latitude_4km()
    lons_4km = FY4ASSI.get_longitude_4km()

    lats_1km = FY4ASSI.get_latitude_1km()
    lons_1km = FY4ASSI.get_longitude_1km()
    ddem = FY4ASSI.get_ddem_1km()

    lats_min = np.nanmin(lats_1km) - 5
    lats_max = np.nanmax(lats_1km) + 5
    lons_min = np.nanmin(lons_1km) - 5
    lons_max = np.nanmax(lons_1km) + 5

    print(lats_min, lats_max, lons_min, lons_max)

    index1 = np.logical_and.reduce((lons_4km <= lons_max, lons_4km >= lons_min,
                                    lats_4km <= lats_max, lats_4km >= lats_min,))

    for element in elements:
        print(element)
        values = data_get.get(element)()
        index2 = np.isfinite(values)
        index = np.logical_and(index1, index2)
        valid_count = index.sum()
        print(index1.sum())
        print(index2.sum())
        print('有效点数量:{}'.format(valid_count))
        if valid_count <= 0:
            data = np.full_like(lons_1km, np.nan)
        else:
            lats_ = lats_4km[index].reshape(-1, 1)
            lons_ = lons_4km[index].reshape(-1, 1)
            points = np.concatenate((lons_, lats_), axis=1)
            values = values[index]
            data = griddata(points, values, (lons_1km, lats_1km), method='linear')
            data = topoCorrection(data, ddem)
        result[element] = data

    _write_out_file(out_file, result)
    if os.path.isfile(out_file) and not exist_result_data(resultid=resultid, datatime=datatime,
                                                          resolution_type=resolution_type,
                                                          area_type=area_type):
        add_result_data(resultid=resultid, planid=planid, address=out_file, datatime=datatime,
                        resolution_type=resolution_type, area_type=area_type)
