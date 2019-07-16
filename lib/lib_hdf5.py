#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/9/12
@Author  : AnNing
"""
import os

import h5py
import numpy as np


def write_hdf5(out_file, datas):
    """
    :param out_file: (str)
    :param datas: (dict)
    :return:
    """
    if not datas:
        return
    with h5py.File(out_file, 'w') as hdf5:
        for key in datas:
            if isinstance(datas[key], dict):
                group_name = key
                group_data = datas[key]
                if isinstance(group_data, dict):
                    for dataset_name in group_data:
                        data = group_data[dataset_name]
                        # 处理
                        hdf5.create_dataset('/{}/{}'.format(group_name, dataset_name),
                                            dtype=np.float32, data=data)
            else:
                dataset_name = key
                data = datas[dataset_name]
                # 处理
                hdf5.create_dataset(dataset_name, data=data)
    print '>>> {}'.format(out_file)


def write_hdf5_and_compress(out_file, datas):
    """
    :param out_file: (str)
    :param datas: (dict)
    :return:
    """
    if not datas:
        return
    compression = 'gzip'
    compression_opts = 5
    shuffle = True
    with h5py.File(out_file, 'w') as hdf5:
        for key in datas:
            if isinstance(datas[key], dict):
                group_name = key
                group_data = datas[key]
                if isinstance(group_data, dict):
                    for dataset_name in group_data:
                        data = group_data[dataset_name]
                        # 处理
                        hdf5.create_dataset('/{}/{}'.format(group_name, dataset_name),
                                            dtype=np.float32, data=data, compression=compression,
                                            compression_opts=compression_opts,
                                            shuffle=shuffle)
            else:
                dataset_name = key
                data = datas[dataset_name]
                # 处理
                hdf5.create_dataset(dataset_name, data=data, compression=compression,
                                    compression_opts=compression_opts,
                                    shuffle=shuffle)
    print '>>> {}'.format(out_file)


def read_hdf5(in_file):
    """
    :param in_file:
    :return:
    """
    datas = {}
    with h5py.File(in_file, 'r') as hdf5:
        for key in hdf5:
            if type(hdf5[key]).__name__ == 'Group':
                group_name = key
                if group_name not in datas:
                    datas[group_name] = {}
                group_data = hdf5[key]
                for dataset_name in group_data:
                    data = group_data[dataset_name].value
                    # 处理
                    datas[group_name][dataset_name] = data
            else:
                dataset_name = key
                data = hdf5[dataset_name].value
                # 处理
                datas[dataset_name] = data
    return datas


def merge_dict_data(dict_data1, dict_data2):
    """
    将 data2 添加到 data1
    :param dict_data1: (dict)
    :param dict_data2: (dict)
    :return: data_shape = (1, n)
    """
    if not isinstance(dict_data1, dict) or not isinstance(dict_data2, dict):
        raise TypeError('Data is not dict type')
    for channel_name in dict_data2:
        if channel_name not in dict_data1:
            dict_data1[channel_name] = dict_data2[channel_name]
        else:
            data1 = dict_data1[channel_name]
            data2 = dict_data2[channel_name]
            channel_data = np.append(data1, data2)
            dict_data1[channel_name] = channel_data


class ReadHDF5(object):
    """
    read_hdf5()
    read_groups()
    read_datasets()
    read_group()
    read_datasets()
    """

    def __init__(self, in_file):
        self.file_path = in_file
        self.dir_path = os.path.dirname(in_file)
        self.file_name = os.path.basename(in_file)

        self.ymd = None
        self.hm = None

        self.data = dict()
        self.file_attr = dict()
        self.data_attr = dict()

    def read_hdf5(self, datasets=None, groups=None):
        """
        :param datasets: [str] 需要读取的数据集
        :param groups: [str] 需要读取的数据组
        :return:
        """
        if datasets:
            self.read_datasets(datasets)
        if groups:
            self.read_groups(groups)
        if datasets is None and groups is None:
            self.read_all()

    def read_all(self):
        with h5py.File(self.file_path, 'r') as hdf5_file:
            for item in hdf5_file:
                if type(hdf5_file[item]).__name__ == 'Group':
                    hdf5_group = hdf5_file[item]
                    self.read_group(hdf5_group)
                else:
                    hdf5_dataset = hdf5_file[item]
                    self.read_dataset(hdf5_dataset)

    def read_groups(self, groups):
        """
        :param groups: [str] 需要读取的数据组
        :return:
        """
        with h5py.File(self.file_path, 'r') as hdf5_file:
            for group in groups:
                hdf5_group = hdf5_file[group]
                self.read_group(hdf5_group)

    def read_datasets(self, datasets):
        """
        :param datasets: [str] 需要读取的数据集
        :return:
        """
        with h5py.File(self.file_path, 'r') as hdf5_file:
            for dataset in datasets:
                print dataset
                hdf5_dataset = hdf5_file[dataset]
                self.read_dataset(hdf5_dataset)

    def read_group(self, hdf5_group):
        for item in hdf5_group:
            if type(hdf5_group[item]).__name__ == 'Group':
                hdf5_group = hdf5_group[item]
                self.read_group(hdf5_group)
            else:
                hdf5_dataset = hdf5_group[item]
                self.read_dataset(hdf5_dataset)

    def read_dataset(self, hdf5_dataset):
        dataset_path = hdf5_dataset.name.split('/')
        dataset_name = dataset_path.pop()
        data = self._create_data_dict(dataset_path)
        data[dataset_name] = hdf5_dataset.value

    def _create_data_dict(self, dataset_path):
        """
        :param dataset_path: [str]
        :return: dict
        """
        data = self.data
        for i in dataset_path:
            if not i:
                continue
            if i in data:
                data = data[i]
                continue
            else:
                data[i] = {}
                data = data[i]
        return data

    # TODO 添加读取属性的方法
    def read_file_attr(self):
        pass

    def read_dataset_attr(self):
        pass
