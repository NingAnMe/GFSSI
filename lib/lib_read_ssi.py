#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/1
@Author  : AnNing
"""
from datetime import datetime
import re
import numpy as np
import gdal
import h5py
from lib.lib_constant import *


class FY3DSSIENVI:
    def __init__(self, in_file):
        self.in_file = in_file

        dataset = gdal.Open(self.in_file)
        self.XSize = dataset.RasterXSize
        self.YSize = dataset.RasterYSize
        self.GeoTransform = dataset.GetGeoTransform()
        self.ProjectionInfo = dataset.GetProjection()

    def get_data(self):
        dataset = gdal.Open(self.in_file)
        band = dataset.GetRasterBand(1)
        data = band.ReadAsArray(0, 0, self.XSize, self.YSize).astype(np.float32)
        return data

    def get_lon_lat(self):
        gtf = self.GeoTransform
        x_range = range(0, self.XSize)
        y_range = range(0, self.YSize)
        x, y = np.meshgrid(x_range, y_range)
        lon = gtf[0] + x * gtf[1] + y * gtf[2]
        lat = gtf[3] + x * gtf[4] + y * gtf[5]
        return lon, lat


class FY3DSSI:
    def __init__(self, in_file):
        self.in_file = in_file

    @staticmethod
    def get_latitude_1km():
        full_value = -999
        with h5py.File(LON_LAT_LUT_FY3_1KM, 'r') as hdf:
            dataset = hdf.get('Latitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_longitude_1km():
        full_value = -999
        with h5py.File(LON_LAT_LUT_FY3_1KM, 'r') as hdf:
            dataset = hdf.get('Longitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset


class FY4ASSI(object):
    def __init__(self, in_file):
        self.in_file = in_file

    @staticmethod
    def get_date_time_orbit(in_file):
        filename = os.path.basename(in_file)
        p = r'.*NOM_(\d{14})_\d{14}_'
        r = re.match(p, filename)
        date_time = r.groups()[0]
        return datetime.strptime(date_time, '%Y%m%d%H%M%S')

    @staticmethod
    def get_date_time_daily(in_file):
        filename = os.path.basename(in_file)
        p = r'.*NOM_(\d{8})_'
        r = re.match(p, filename)
        date_time = r.groups()[0]
        return datetime.strptime(date_time, '%Y%m%d')

    @staticmethod
    def get_date_time_monthly(in_file):
        filename = os.path.basename(in_file)
        p = r'.*NOM_(\d{6})_'
        r = re.match(p, filename)
        date_time = r.groups()[0]
        return datetime.strptime(date_time, '%Y%m')

    @staticmethod
    def get_date_time_yearly(in_file):
        filename = os.path.basename(in_file)
        p = r'.*NOM_(\d{4})_'
        r = re.match(p, filename)
        date_time = r.groups()[0]
        return datetime.strptime(date_time, '%Y')

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
                index = data <= 0
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
                index = data <= 0
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
                index = data <= 0
                data[index] = np.nan
                return data

    def get_ssi(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('SSI')
            if dataset is not None:
                data = dataset[:]
                index = np.logical_or(data <= 0, data >= 10000)
                data[index] = np.nan
                return data

    def get_difssi(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('DifSSI')
            if dataset is not None:
                data = dataset[:]
                index = np.logical_or(data <= 0, data >= 10000)
                data[index] = np.nan
                return data

    def get_dirssi(self):
        with h5py.File(self.in_file, 'r') as hdf:
            dataset = hdf.get('DirSSI')
            if dataset is not None:
                data = dataset[:]
                index = np.logical_or(data <= 0, data >= 10000)
                data[index] = np.nan
                return data

    @staticmethod
    def get_latitude_4km():
        # -81, 81
        full_value = -999
        with h5py.File(LON_LAT_LUT_FY4_4KM, 'r') as hdf:
            dataset = hdf.get('Latitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_longitude_4km():
        # 23, 186
        full_value = -639
        offset = 104.7
        with h5py.File(LON_LAT_LUT_FY4_4KM, 'r') as hdf:
            dataset = hdf.get('Longitude')[:]
            dataset[dataset == full_value] = np.nan
            dataset += offset  # 由于经纬度查找表的问题，这里有一个偏移量
            dataset[dataset > 180] -= 360  # 加上偏移量以后，原来的值会超过180，需要恢复其正常位置
            return dataset

    @staticmethod
    def get_latitude_1km():
        full_value = -999
        with h5py.File(LON_LAT_LUT_FY4_1KM, 'r') as hdf:
            dataset = hdf.get('Latitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_longitude_1km():
        full_value = -999
        with h5py.File(LON_LAT_LUT_FY4_1KM, 'r') as hdf:
            dataset = hdf.get('Longitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_ddem_1km():
        full_value = -999
        with h5py.File(LON_LAT_LUT_FY4_1KM, 'r') as hdf:
            dataset = hdf.get('D_DEM')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_sz(geo_file):
        full_value = 65535
        with h5py.File(geo_file, 'r') as hdf:
            dataset = hdf.get('NOMSunZenith')[:]
            dataset[dataset == full_value] = np.nan
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
    def get_longitude_proj_4km():
        full_value = -999
        with h5py.File(PROJ_LUT_FY4_4KM, 'r') as hdf:
            dataset = hdf.get('Longitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_longitude_proj_1km():
        full_value = -999
        with h5py.File(PROJ_LUT_FY4_1KM, 'r') as hdf:
            dataset = hdf.get('Longitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_latitude_proj_4km():
        full_value = -999
        with h5py.File(PROJ_LUT_FY4_4KM, 'r') as hdf:
            dataset = hdf.get('Latitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_latitude_proj_1km():
        full_value = -999
        with h5py.File(PROJ_LUT_FY4_1KM, 'r') as hdf:
            dataset = hdf.get('Latitude')[:]
            dataset[dataset == full_value] = np.nan
            return dataset

    @staticmethod
    def get_lonlat_projlut_4km():
        result = {}
        with h5py.File(PROJ_LUT_FY4_4KM, 'r') as hdf:
            for dataset in hdf:
                result[dataset] = hdf.get(dataset)[:]
            return result

    @staticmethod
    def get_lonlat_projlut_1km():
        result = {}
        with h5py.File(PROJ_LUT_FY4_1KM, 'r') as hdf:
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
