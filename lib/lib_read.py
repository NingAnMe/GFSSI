#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/1
@Author  : AnNing
"""
import os
import numpy as np
import h5py

from PB.DRC.GEO import get_fy4_lon_lat_lut
FY4_LON_LAT_LUT = get_fy4_lon_lat_lut()


class FY4ASSI(object):
    def __init__(self, in_file):
        self.in_file = in_file
        self.lon_lat_lut = get_fy4_lon_lat_lut()

    def get_date_time(self):
        filename = os.path.basename(self.in_file)
        ymdhms = filename.split('_')[-4]
        return ymdhms

    def get_itol(self):
        return self.get_ssi()

    def get_ib(self):
        return self.get_dirssi()

    def get_id(self):
        return self.get_difssi()

    def get_g0(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('G0')[:]
            index = np.logical_or(dataset <= 0, dataset >= 1500)
            dataset[index] = np.nan
            return dataset

    def get_gt(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('G0')[:]
            index = np.logical_or(dataset <= 0, dataset >= 1500)
            dataset[index] = np.nan
            return dataset

    def get_dni(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('G0')[:]
            index = np.logical_or(dataset <= 0, dataset >= 1500)
            dataset[index] = np.nan
            return dataset

    def get_ssi(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('SSI')[:]
            index = np.logical_or(dataset <= 0, dataset >= 1500)
            dataset[index] = np.nan
            return dataset

    def get_difssi(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('DifSSI')[:]
            index = np.logical_or(dataset <= 0, dataset >= 1500)
            dataset[index] = np.nan
            return dataset

    def get_dirssi(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('DirSSI')[:]
            index = np.logical_or(dataset <= 0, dataset >= 1500)
            dataset[index] = np.nan
            return dataset

    @staticmethod
    def get_latitude():
        full_value = -999
        with h5py.File(FY4_LON_LAT_LUT, 'r') as hdf:
            dataset = hdf.get('Latitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_longitude():
        full_value = -639
        offset = 104.7
        with h5py.File(FY4_LON_LAT_LUT, 'r') as hdf:
            dataset = hdf.get('Longitude')[:]
            dataset[dataset == full_value] = np.nan
            dataset += offset  # 由于经纬度查找表的问题，这里有一个偏移量
            return dataset

    @staticmethod
    def modify_data(out_file, ssi, difssi, dirssi):
        with h5py.File(out_file, 'a') as hdf:
            for k, v in zip(('SSI', 'DifSSI', 'DirSSI'), (ssi, difssi, dirssi)):
                dataset = hdf.get(k)
                dataset[...] = v
                dataset.attrs.modify('units', np.array('KW/m2', dtype=h5py.special_dtype(vlen=str)))
