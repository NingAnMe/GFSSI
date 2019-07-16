#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/8/6 10:35
@Author  : AnNing
"""
from datetime import datetime
import os

import h5py

from lib.lib_hdf5 import read_hdf5
import numpy as np


DEBUG = True
TIME_TEST = False


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
        self.read_file_attr()

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

    def read_file_attr(self):
        with h5py.File(self.file_path) as hdf5_file:
            for k, v in hdf5_file.attrs.items():
                self.file_attr[k] = v

    # TODO 添加读取dataset属性的方法
    def read_dataset_attr(self):
        pass


class LoadH5():
    """
    read hdf5类型数据到字典中，支持合并
    """

    def __init__(self):
        self.data = {}

    def load(self, in_file, ymd):
        try:
            h5File_R = h5py.File(in_file, 'r')
            if len(h5File_R.keys()) > 0:
                if 'ymd' not in self.data.keys():
                    self.data['ymd'] = []
#                 ary_ymd = (np.array(int(ymd))).reshape(1, 1)
                self.data['ymd'].append(ymd)

            for key in h5File_R.keys():
                root_id = h5File_R.get(key)
                if type(root_id).__name__ == "Group":  # 判断名字是否属于组
                    if key not in self.data.keys():
                        self.data[key] = {}
                    for dkey in root_id.keys():
                        h5data = root_id.get(dkey)[:]

                        if dkey not in self.data[key].keys():

                            self.data[key][dkey] = h5data
                        else:
                            self.data[key][dkey] = np.concatenate(
                                (self.data[key][dkey], h5data))
                else:
                    h5data = h5File_R.get(key)[:]
                    if key not in self.data.keys():
                        self.data[key] = h5data
                    else:
                        self.data[key] = np.concatenate(
                            (self.data[key], h5data))

            h5File_R.close()
        except Exception as e:
            print str(e)
            print "Load file error: {}".format(in_file)


def write_h5(ofile, data):

    out_path = os.path.dirname(ofile)
    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    # 打开h5文件
    h5w = h5py.File(ofile, 'w')

    for key in sorted(data.keys()):
        if isinstance(data[key], dict):
            for key2 in data[key].keys():
                h5w.create_dataset(
                    '%s/%s' % (key, key2), data=data[key][key2], compression='gzip', compression_opts=5, shuffle=True)

        elif isinstance(data[key], np.ndarray):
            h5w.create_dataset(
                key, data=data[key], compression='gzip', compression_opts=5, shuffle=True)

        elif isinstance(data[key], list):
            h5w.create_dataset(
                key, data=data[key], compression='gzip', compression_opts=5, shuffle=True)

    h5w.close()


class ReadCombineData(object):

    def __init__(self, in_file):
        if not os.path.isfile(in_file):
            raise ValueError('File is not exist: {}'.format(in_file))
        self.in_file = in_file
        self.file_data = read_hdf5(in_file)

    def get_dn(self):
        dataset_name = 'dn_avg'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_ref_6sv(self):
        dataset_name = 'ref'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_k0(self):
        dataset_name = 'k0'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_k1(self):
        dataset_name = 'k1'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_k2(self):
        dataset_name = 'k2'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_sv(self):
        dataset_name = 'sv_avg'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_ref_sv(self):
        ref_sv = dict()
        datas = read_hdf5(self.in_file)
        for channel_name in datas:
            if not isinstance(datas[channel_name], dict):
                continue
            count = len(self.get_sv()[channel_name])
            ref_sv[channel_name] = np.array([0.] * count)
        return ref_sv


class ReadRegressionData(object):

    def __init__(self, in_file):
        if not os.path.isfile(in_file):
            raise ValueError('File is not exist: {}'.format(in_file))
        self.in_file = in_file
        self.file_data = read_hdf5(in_file)

    def get_rmse(self):
        dataset_name = 'rmse'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_count(self):
        dataset_name = 'count'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_k0_ms(self):
        dataset_name = 'k0_MS'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_k1_ms(self):
        dataset_name = 'k1_MS'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_k2_ms(self):
        dataset_name = 'k2_MS'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_k0_oper(self):
        dataset_name = 'k0'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_k1_oper(self):
        dataset_name = 'k1'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_k2_oper(self):
        dataset_name = 'k2'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_correlation(self):
        dataset_name = 'correlation'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            data[channel_name] = hdf5_datas[channel_name][dataset_name]
        return data

    def get_date(self):
        dataset_name = 'Time'
        data = dict()
        hdf5_datas = self.file_data
        for channel_name in hdf5_datas:
            if not isinstance(hdf5_datas[channel_name], dict):
                continue
            timestamp = hdf5_datas[channel_name][dataset_name]
            data[channel_name] = datetime.utcfromtimestamp(timestamp)
        return data
