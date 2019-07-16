#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/11/23
@Author  : AnNing
"""
from datetime import datetime
import os

import h5py
import numpy as np
from lib.lib_hdf5 import read_hdf5

DEBUG = True
TIME_TEST = False


class ReadProjData(object):
    def __init__(self, in_file):
        if not os.path.isfile(in_file):
            raise ValueError('File is not exist: {}'.format(in_file))
        self.in_file = in_file

    def get_ref(self):
        dataset_name = 'REF'
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5_datas:
            for channel_name in hdf5_datas.keys():
                data_name = '{}/{}'.format(channel_name, dataset_name)
                dataset = hdf5_datas.get(data_name)
                if dataset is not None:
                    data[channel_name] = dataset[:]
        return data

    def get_latitude(self):
        dataset_name = 'Latitude'
        data = None
        with h5py.File(self.in_file, 'r') as hdf5_datas:
            if dataset_name in hdf5_datas.keys():
                dataset = hdf5_datas.get(dataset_name)
                if dataset is not None:
                    data = dataset[:]
        return data

    def get_longitude(self):
        dataset_name = 'Longitude'
        data = None
        with h5py.File(self.in_file, 'r') as hdf5_datas:
            if dataset_name in hdf5_datas.keys():
                dataset = hdf5_datas.get(dataset_name)
                if dataset is not None:
                    data = dataset[:]
        return data
