#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/1
@Author  : AnNing
"""
from datetime import datetime
import os
import numpy as np
import h5py
from PB.DRC.GEO import get_fy4_lon_lat_lut
from lib.lib_constant import PROJ_LUT_4KM, FY4_LON_LAT_LUT


class FY4ASSI(object):
    def __init__(self, in_file):
        self.in_file = in_file
        self.lon_lat_lut = get_fy4_lon_lat_lut()

    @staticmethod
    def get_date_time_orbit(in_file):
        filename = os.path.basename(in_file)
        ymdhms = filename.split('_')[-4]
        return datetime.strptime(ymdhms, '%Y%m%d%H%M%S')

    def get_itol(self):
        """
        总
        :return:
        """
        return self.get_ssi()

    def get_ib(self):
        """
        直
        :return:
        """
        return self.get_dirssi()

    def get_id(self):
        """
        散
        :return:
        """
        return self.get_difssi()

    def get_g0(self):
        """
        天
        :return:
        """
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('G0')
            if dataset is not None:
                data = dataset[:]
                index = np.logical_or(data <= 0, data >= 1500)
                data[index] = np.nan
                return data

    def get_gt(self):
        """
        斜
        :return:
        """
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('Gt')
            if dataset is not None:
                data = dataset[:]
                index = np.logical_or(data <= 0, data >= 1500)
                data[index] = np.nan
                return data

    def get_dni(self):
        """
        角
        :return:
        """
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('DNI')
            if dataset is not None:
                data = dataset[:]
                index = np.logical_or(data <= 0, data >= 1500)
                data[index] = np.nan
                return data

    def get_ssi(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('SSI')
            if dataset is not None:
                data = dataset[:]
                index = np.logical_or(data <= 0, data >= 1500)
                data[index] = np.nan
                return data

    def get_difssi(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('DifSSI')
            if dataset is not None:
                data = dataset[:]
                index = np.logical_or(data <= 0, data >= 1500)
                data[index] = np.nan
                return data

    def get_dirssi(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('DirSSI')
            if dataset is not None:
                data = dataset[:]
                index = np.logical_or(data <= 0, data >= 1500)
                data[index] = np.nan
                return data

    @staticmethod
    def get_latitude():
        # -81, 81
        full_value = -999
        with h5py.File(FY4_LON_LAT_LUT, 'r') as hdf:
            dataset = hdf.get('Latitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_longitude():
        # 23, 186
        full_value = -639
        offset = 104.7
        with h5py.File(FY4_LON_LAT_LUT, 'r') as hdf:
            dataset = hdf.get('Longitude')[:]
            dataset[dataset == full_value] = np.nan
            dataset += offset  # 由于经纬度查找表的问题，这里有一个偏移量
            idx_finite = np.isfinite(dataset)
            dataset[idx_finite][dataset > 180] -= 360  # 加上偏移量以后，原来的值会超过180，需要恢复其正常位置
            return dataset

    def get_latitude_area(self):
        full_value = -999
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('Latitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    def get_longitude_area(self):
        full_value = -999
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('Longitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_longitude_proj():
        full_value = -999
        with h5py.File(PROJ_LUT_4KM, 'r') as hdf:
            dataset = hdf.get('Longitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_latitude_proj():
        full_value = -999
        with h5py.File(PROJ_LUT_4KM, 'r') as hdf:
            dataset = hdf.get('Latitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_lonlat_projlut():
        result = {}
        with h5py.File(PROJ_LUT_4KM, 'r') as hdf:
            for dataset in hdf:
                result[dataset] = hdf.get(dataset)[:]
            return result

    @staticmethod
    def modify_data(out_file, ssi, difssi, dirssi):
        with h5py.File(out_file, 'a') as hdf:
            for k, v in zip(('SSI', 'DifSSI', 'DirSSI'), (ssi, difssi, dirssi)):
                dataset = hdf.get(k)
                dataset[...] = v
                dataset.attrs.modify('units', np.array('KW/m2', dtype=h5py.special_dtype(vlen=str)))
