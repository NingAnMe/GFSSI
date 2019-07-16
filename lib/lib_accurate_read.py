#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/12/10
@Author  : AnNing
"""
import os
from PB.pb_time import ymd2date
from lib.lib_hdf5 import read_hdf5


class ReadCombineData(object):
    def __init__(self, in_file):
        if not os.path.isfile(in_file):
            raise ValueError('File is not exist: {}'.format(in_file))
        self.in_file = in_file
        self.file_data = read_hdf5(in_file)

    def get_rad_bias(self, sky_type='all'):
        if sky_type.lower() == 'all':
            dataset_name = 'RadBias'
        elif sky_type.lower() == 'cloud':
            dataset_name = 'RadBiasCloud'
        elif sky_type.lower() == 'clear':
            dataset_name = 'RadBiasClear'
        else:
            raise KeyError('Cant handle this type: {}'.format(sky_type))
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_tbb_bias(self, sky_type):
        if sky_type.lower() == 'all':
            dataset_name = 'TbbBias'
        elif sky_type.lower() == 'cloud':
            dataset_name = 'TbbBiasCloud'
        elif sky_type.lower() == 'clear':
            dataset_name = 'TbbBiasClear'
        else:
            raise KeyError('Cant handle this type: {}'.format(sky_type))
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_bias(self, data_type, sky_type):
        if data_type == 'rad_rad':
            return self.get_rad_bias(sky_type)
        elif data_type == 'tbb_tbb':
            return self.get_tbb_bias(sky_type)
        else:
            raise KeyError('Cant handle this data type: {}'.format(data_type))

    def get_date(self):
        dataset_name = 'ymd'
        data = self.file_data.get(dataset_name)
        data = map(ymd2date, data)
        return data
