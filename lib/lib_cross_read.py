#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/9/12
@Author  : AnNing
"""
from datetime import datetime
import os

import h5py
import numpy as np
from lib_hdf5 import merge_dict_data


class ReadCollocation(object):
    def __init__(self, in_file):
        if not os.path.isfile(in_file):
            raise ValueError("collocation file is not exist: {}".format(in_file))

        self.in_file = in_file
        self.satellite = None
        self.sensor = None
        self.channels = None

    def get_dn_mean(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_FovDnMean'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_ref_mean(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_FovRefMean'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_rad_mean(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_FovRadMean'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_tbb_mean(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_FovTbbMean'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_ref_std(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_EnvRefStd'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_rad_std(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_EnvRadStd'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_tbb_std(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_EnvTbbStd'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_longitude(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_Lon'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_latitude(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_Lat'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_sun_zenith(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_SolZ'.format(channel_name, satellite))
                # 20190221 临时性修改如果 SolZ 不存在，使用 SoZ，原来的合成文件名字是SoZ，后期修改
                if dataset is None:
                    dataset = hdf5.get('{}/S{:1d}_SoZ'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_time(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_Time'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_k0(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_K0'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_k1(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_K1'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_sv(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_SV'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data

    def get_bb(self, satellite=1):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset = hdf5.get('{}/S{:1d}_BB'.format(channel_name, satellite))
                if dataset is not None:
                    data_hdf5 = dataset[:]
                    data[channel_name] = data_hdf5
        return data


    def get_filter_longitude_latitude(self):
        """
        过滤相同位置的经纬度数据
        :return:
        """
        data = set()
        latitude_all = self.get_latitude()
        longitude_all = self.get_longitude()
        for channel_name in latitude_all:
            if channel_name in longitude_all:
                latitude = latitude_all[channel_name].reshape(-1, ).tolist()
                longitude = longitude_all[channel_name].reshape(-1, ).tolist()
                data.update(set(zip(longitude, latitude)))
        data = list(data)
        data = np.array(data, dtype=np.float32)
        return data[:, 0], data[:, 1]


def get_collocation_data(in_files, data_type, satellite=1):
    """
    从多个文件中获取数据,并进行拼接
    """
    data_all = None
    for in_file in in_files:
        if not os.path.isfile(in_file):
            continue
        data_reader = ReadCollocation(in_file)
        data_type = data_type.lower()

        if data_type == 'dn':
            data = data_reader.get_dn_mean(satellite)
        elif data_type == 'ref':
            data = data_reader.get_ref_mean(satellite)
        elif data_type == 'rad':
            data = data_reader.get_rad_mean(satellite)
        elif data_type == 'tbb':
            data = data_reader.get_tbb_mean(satellite)
        elif data_type == 'dn_ref':
            data = None
        elif data_type == 'rad_rad':
            data = data_reader.get_rad_std(satellite)
        elif data_type == 'ref_ref':
            data = data_reader.get_ref_std(satellite)
        elif data_type == 'tbb_tbb':
            data = data_reader.get_tbb_std(satellite)
        elif data_type == 'time':
            data = data_reader.get_time()
        elif data_type == 'longitude':
            data = data_reader.get_longitude()
        elif data_type == 'sun_zenith':
            data = data_reader.get_sun_zenith(satellite)
        else:
            raise TypeError('can not handle this type: {}'.format(data_type))

        if data_all is None:
            data_all = data
        else:
            merge_dict_data(data_all, data)
    return data_all


class ReadCoeff(object):
    def __init__(self, in_file):
        if not os.path.isfile(in_file):
            raise ValueError("collocation file is not exist: {}".format(in_file))

        self.in_file = in_file
        self.satellite = None
        self.sensor = None
        self.channels = None

    def get_md(self, data_type, data_time):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset_name = '{}/{}_MD_{}'.format(channel_name, data_type, data_time)
                dataset = hdf5.get(dataset_name)
                if dataset is not None:
                    data_hdf5 = dataset.value
                    data[channel_name] = data_hdf5
        return data

    def get_bias(self, data_type, data_time):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset_name = '{}/{}_Bias_{}'.format(channel_name, data_type, data_time)
                dataset = hdf5.get(dataset_name)
                if dataset is not None:
                    data_hdf5 = dataset.value
                    data[channel_name] = data_hdf5
        return data

    def get_k0(self, data_type, data_time):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset_name = '{}/{}_K0_{}'.format(channel_name, data_type, data_time)
                dataset = hdf5.get(dataset_name)
                if dataset is not None:
                    data_hdf5 = dataset.value
                    data[channel_name] = data_hdf5
        return data

    def get_k1(self, data_type, data_time):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset_name = '{}/{}_K1_{}'.format(channel_name, data_type, data_time)
                dataset = hdf5.get(dataset_name)
                if dataset is not None:
                    data_hdf5 = dataset.value
                    data[channel_name] = data_hdf5
        return data

    def get_count(self, data_type, data_time):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset_name = '{}/{}_Count_{}'.format(channel_name, data_type, data_time)
                dataset = hdf5.get(dataset_name)
                if dataset is not None:
                    data_hdf5 = dataset.value
                    data[channel_name] = data_hdf5
        return data

    def get_date(self, data_type, data_time):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for name_key in hdf5:
                if 'CH_' in name_key:
                    channel_name = name_key
                else:
                    continue
                dataset_name = '{}/{}_Time_{}'.format(channel_name, data_type, data_time)
                dataset = hdf5.get(dataset_name)
                if dataset is not None:
                    data_hdf5 = dataset.value
                    date = datetime.utcfromtimestamp(data_hdf5)
                    data[channel_name] = date
        return data


if __name__ == '__main__':
    collocation_data = r"D:\nsmc\cross_data\collocation\FY3D+MERSI_METOP-A+IASI\COLLOC+LEOLEOIR," \
                       r"FY3D+MERSI_METOP-A+IASI_C_BABJ_20180730.hdf5 "
    read_collocation = ReadCollocation(collocation_data)
    read_collocation.get_filter_longitude_latitude()
