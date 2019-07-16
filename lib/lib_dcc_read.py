#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/9/12
@Author  : AnNing
"""
import os
import re
from datetime import datetime

import h5py
import numpy as np


class ReadSlt(object):
    def __init__(self, in_file, sensor):
        if not os.path.isfile(in_file):
            raise ValueError("dcc file is not exist: {}".format(in_file))

        self.in_file = in_file
        self.satellite = None
        self.sensor = sensor

        self.set_satellite()

    def set_satellite(self):
        """
        set self.satellite
        :return:
        """
        file_name = os.path.basename(self.in_file)
        pattern = r'([A-Z0-9]+)_%s.*' % self.sensor
        m = re.match(pattern, file_name)
        if m:
            self.satellite = m.groups()[0]
        else:
            raise ValueError('Cant get the satellite name from file name.')


class ReadSltFY3DMersi(ReadSlt):
    """
    读取SLT文件
    """
    def __init__(self, in_file):
        sensor = 'MERSI'
        super(ReadSltFY3DMersi, self).__init__(in_file, sensor)

        self.adms_index_by_window = [1, 3, 5, 9, 15]  # 分别对应 1, 3, 5, 9, 15
        self.channels = 19

    def __get_adms_index(self, window_size):
        window_size = int(window_size)

        if window_size not in self.adms_index_by_window:
            raise ValueError("window size is not in {}".format(self.adms_index_by_window))
        index = self.adms_index_by_window.index(window_size)
        return index

    def get_degradation_adms(self, window_size):
        data = dict()
        adms_index = self.__get_adms_index(window_size)

        with h5py.File(self.in_file, 'r') as hdf5:
            data_hdf5 = hdf5.get('DN_ADMs')[:, :, adms_index]
            invalid_value = 65535
            index_invalid = np.where(data_hdf5 == invalid_value)

            data_hdf5 = data_hdf5.astype(np.float32)
            data_hdf5[index_invalid] = np.nan

        for i in xrange(self.channels):
            channel_name = 'CH_{:02d}'.format(i + 1)
            data_channel = data_hdf5[i] / 100.
            data[channel_name] = data_channel
        return data

    def get_ref_adms(self, window_size):
        data = dict()
        adms_index = self.__get_adms_index(window_size)

        with h5py.File(self.in_file, 'r') as hdf5:
            data_hdf5 = hdf5.get('REF_ADMs')[:, :, adms_index]
            invalid_value = 65535
            index_invalid = np.where(data_hdf5 == invalid_value)

            data_hdf5 = data_hdf5.astype(np.float32)
            data_hdf5[index_invalid] = np.nan

        for i in xrange(self.channels):
            channel_name = 'CH_{:02d}'.format(i + 1)
            data_channel = data_hdf5[i] / 100.
            data[channel_name] = data_channel
        return data

    def get_latitude(self):

        with h5py.File(self.in_file, 'r') as hdf5:
            data_hdf5 = hdf5.get('Latitude')[:]
            invalid_value = -1
            index_invalid = np.logical_and(data_hdf5 >= 9000, data_hdf5 <= -9000)
            index_invalid = np.logical_and(index_invalid, data_hdf5 == invalid_value)

            data_hdf5 = data_hdf5.astype(np.float32)
            data_hdf5[index_invalid] = np.nan

        data = data_hdf5 / 100.
        return data

    def get_longitude(self):

        with h5py.File(self.in_file, 'r') as hdf5:
            data_hdf5 = hdf5.get('Longitude')[:]
            invalid_value = -1
            index_invalid = np.logical_and(data_hdf5 >= 18000, data_hdf5 <= -18000)
            index_invalid = np.logical_and(index_invalid, data_hdf5 == invalid_value)

            data_hdf5 = data_hdf5.astype(np.float32)
            data_hdf5[index_invalid] = np.nan

        data = data_hdf5 / 100.
        return data


class ReadStatistics(object):
    def __init__(self, in_file):
        if not os.path.isfile(in_file):
            raise ValueError("Statistics file is not exist: {}".format(in_file))

        self.in_file = in_file

    def get_ref_avg(self):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for channel_name in hdf5:
                hdf5_data = hdf5.get(channel_name)
                if type(hdf5_data).__name__ == 'Group':
                    data[channel_name] = hdf5[channel_name]['REF_Avg'].value
        return data

    def get_ref_mod(self):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for channel_name in hdf5:
                hdf5_data = hdf5.get(channel_name)
                if type(hdf5_data).__name__ == 'Group':
                    data[channel_name] = hdf5[channel_name]['REF_Mod'].value
        return data

    def get_ref_med(self):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for channel_name in hdf5:
                hdf5_data = hdf5.get(channel_name)
                if type(hdf5_data).__name__ == 'Group':
                    data[channel_name] = hdf5[channel_name]['REF_Med'].value
        return data

    def get_ref_count(self):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for channel_name in hdf5:
                hdf5_data = hdf5.get(channel_name)
                if type(hdf5_data).__name__ == 'Group':
                    data[channel_name] = hdf5[channel_name]['REF_Count'].value
        return data

    def get_degradation_avg(self):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for channel_name in hdf5:
                hdf5_data = hdf5.get(channel_name)
                if type(hdf5_data).__name__ == 'Group':
                    data[channel_name] = hdf5[channel_name]['Degradation_Avg'].value
        return data

    def get_degradation_mod(self):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for channel_name in hdf5:
                hdf5_data = hdf5.get(channel_name)
                if type(hdf5_data).__name__ == 'Group':
                    data[channel_name] = hdf5[channel_name]['Degradation_Mod'].value
        return data

    def get_degradation_med(self):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for channel_name in hdf5:
                hdf5_data = hdf5.get(channel_name)
                if type(hdf5_data).__name__ == 'Group':
                    data[channel_name] = hdf5[channel_name]['Degradation_Med'].value
        return data

    def get_degradation_count(self):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for channel_name in hdf5:
                hdf5_data = hdf5.get(channel_name)
                if type(hdf5_data).__name__ == 'Group':
                    data[channel_name] = hdf5[channel_name]['Degradation_Count'].value
        return data

    def get_ymd(self):
        with h5py.File(self.in_file, 'r') as hdf5:
            ymd = hdf5.get('Date').value
        return ymd

    def get_date(self):
        ymd = self.get_ymd()
        return datetime.strptime(str(ymd), '%Y%m%d')


class ReadBias(object):
    def __init__(self, in_file):
        if not os.path.isfile(in_file):
            raise ValueError("Bias file is not exist: {}".format(in_file))

        self.in_file = in_file

    def get_ref_avg(self):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for channel_name in hdf5:
                hdf5_data = hdf5.get(channel_name)
                if type(hdf5_data).__name__ == 'Group':
                    data[channel_name] = hdf5[channel_name]['REF_Avg'].value
        return data

    def get_ref_mod(self):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for channel_name in hdf5:
                hdf5_data = hdf5.get(channel_name)
                if type(hdf5_data).__name__ == 'Group':
                    data[channel_name] = hdf5[channel_name]['REF_Mod'].value
        return data

    def get_ref_med(self):
        data = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for channel_name in hdf5:
                hdf5_data = hdf5.get(channel_name)
                if type(hdf5_data).__name__ == 'Group':
                    data[channel_name] = hdf5[channel_name]['REF_Med'].value
        return data

    def get_ymd(self):
        with h5py.File(self.in_file, 'r') as hdf5:
            ymd = hdf5.get('Date').value
        return ymd

    def get_date(self):
        ymd = self.get_ymd()
        return datetime.strptime(str(ymd), '%Y%m%d')


def get_slt_reader(pair):
    """
    获取卫星对对应的提取类
    :param pair:
    :return:
    """
    read_class = {
        'FY3D+MERSI': ReadSltFY3DMersi
    }
    if pair in read_class:
        return read_class[pair]
    else:
        raise 'Dont have the data read class: {}'.format(pair)


if __name__ == '__main__':
    slt_data_fy3d_mersi = r"D:\nsmc\dcc_data\SLT\FY3D_MERSI_DCC_SLT_20171219.H5"
    read_slt_fy3d_mersi = ReadSltFY3DMersi(slt_data_fy3d_mersi)

    stat_data = r"D:\nsmc\dcc_data\Stats\FY3D+MERSI_DCC_Statistics_20180101_Rolldays_10_new_38.HDF5"
    read_statistics = ReadStatistics(stat_data)

    bias_data = r"D:\nsmc\dcc_data\BIAS\FY3D+MERSI_STANDARD+STANDARD_DCC_Statistics_20180101_Rolldays_10_new_38.HDF5"
    read_bias = ReadBias(bias_data)

    # print read_statistics.get_ref_avg()
    # print read_statistics.get_ref_med()
    # print read_statistics.get_ref_mod()
    # print read_statistics.get_ref_count()
    # print read_statistics.get_ymd()

    print read_bias.get_ref_avg()
    print read_bias.get_ref_med()
    print read_bias.get_ref_mod()
    print read_bias.get_ymd()
    print read_bias.get_date()
