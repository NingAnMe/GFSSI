#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/6/19 10:31
@Author  : AnNing
"""
from datetime import datetime

import numpy as np
import h5py
from scipy.interpolate import interpn


class ORG2SLT(object):
    """
    percent:数据集中的dcc_percent
    dn:数据集中的DN_ADMS
    ref:数据集中的REF_ADMS
    """
    def __init__(self):
        self.window = None
        self.error = False

        self.org_file = None

        # 读取数据集
        self.Azimuth = []
        self.BT_Avg_Std = []
        self.DCC_Percent = []
        self.DN_Avg_Std = []
        self.IR_Avg_Std = []
        self.IR_CAL = []
        self.LandCover = []
        self.Latitude = []
        self.Line_Num = []
        self.Longitude = []
        self.Ref_Avg_Std = []
        self.SatelliteAzimuth = []
        self.SatelliteZenith = []
        self.SunAzimuth = []
        self.SunGlint = []
        self.SunZenith = []
        self.TIME = []
        self.VIS_CAL = []

        self.tbb_range = None
        self.ref_range = None
        self.tbb_std_range = None
        self.ref_std_range = None
        self.percent_range = None
        self.ra_range = None
        self.vza_range = None
        self.sza_range = None
        self.saa_range = None
        self.sga_range = None
        self.lat_range = None
        self.lon_range = None

        self.idx = None
        self.ADMs = None
        self.DN_ADMs = None
        self.Ref_ADMs = None
        self.ADMs_pixle1 = None

    def load_org_data(self, org_file):
        """
        加载 ORG 数据
        :param org_file:
        :return:
        """
        if self.error:
            return
        self.org_file = org_file
        try:
            with h5py.File(org_file, 'r') as h5:
                self.Azimuth = h5.get('Azimuth')[:]
                self.BT_Avg_Std = h5.get('BT_Avg_Std')[:]
                self.DCC_Percent = h5.get('DCC_Percent')[:]
                self.DN_Avg_Std = h5.get('DN_Avg_Std')[:]
                self.IR_Avg_Std = h5.get('IR_Avg_Std')[:]
                self.IR_CAL = h5.get('IR_CAL')[:]
                self.LandCover = h5.get('LandCover')[:]
                self.Latitude = h5.get('Latitude')[:]
                self.Line_Num = h5.get('Line_Num')[:]
                self.Longitude = h5.get('Longitude')[:]
                self.Ref_Avg_Std = h5.get('Ref_Avg_Std')[:]
                self.SatelliteAzimuth = h5.get('SatelliteAzimuth')[:]
                self.SatelliteZenith = h5.get('SatelliteZenith')[:]
                self.SunAzimuth = h5.get('SunAzimuth')[:]
                self.SunGlint = h5.get('SunGlint')[:]
                self.SunZenith = h5.get('SunZenith')[:]
                self.TIME = h5.get('TIME')[:]
                self.VIS_CAL = h5.get('VIS_CAL')[:]
        except Exception as why:
            self.error = True
            print why

    def load_amds_data(self, amds_file):
        """
        加载 ADMs 数据
        :param amds_file:
        :return:
        """
        if self.error:
            return
        try:
            with h5py.File(amds_file) as h5:
                self.ADMs = h5.get("ADMs")[:]
        except Exception as why:
            self.error = True
            print why

    def load_filter_range(self, lon_range=None, lat_range=None, tbb_range=None, tbb_std_range=None,
                          ref_range=None, ref_std_range=None, percent_range=None, ra_range=None,
                          sza_range=None, saa_range=None,
                          vza_range=None, sga_range=None, window=None):
        """
        加载过滤范围配置
        :return:
        """
        if self.error:
            return
        self.tbb_range = tbb_range
        self.ref_range = ref_range
        self.tbb_std_range = tbb_std_range
        self.ref_std_range = ref_std_range
        self.percent_range = percent_range
        self.ra_range = ra_range
        self.vza_range = vza_range
        self.sza_range = sza_range
        self.saa_range = saa_range
        self.sga_range = sga_range
        self.lat_range = lat_range
        self.lon_range = lon_range
        self.window = window

    @staticmethod
    def get_condition(data, data_range):
        """
        通过数据和范围获取筛选条件
        :return:
        """
        range_min, range_max = [float(x) for x in data_range]
        condition = np.logical_and(data > range_min, data < range_max)
        return condition

    def filter_data(self):
        """
        对数据进行过滤
        :return:
        """
        if self.error:
            return
        # TODO 过滤不同的参数选取的维度要写为配置，或者不同的卫星使用不通的 filter_data 方法
        # ########### 总点数
        condition = np.logical_not(self.Longitude == -999)
        idx = np.where(condition)
        print u'总点数 = %d' % len(idx[0])

        # ########### Tbb过滤，使用5通道(11nm通道) 5*5 的 Avg 和 5*5 的 Std
        condition1 = self.get_condition(self.BT_Avg_Std[:, 3], self.tbb_range)
        condition2 = self.get_condition(self.BT_Avg_Std[:, 4], self.tbb_std_range)
        condition3 = np.logical_and(condition1, condition2)
        condition = np.logical_and(condition, condition3)
        idx = np.where(condition)
        print u'Tbb过滤 = %d' % len(idx[0])

        # ########### Ref过滤  用13通道(0.66nm通道) 5*5 的 Avg 和 5*5 的 Std
        condition1 = self.get_condition(self.Ref_Avg_Std[11, :, 3], self.ref_range)
        condition2 = self.get_condition(self.Ref_Avg_Std[11, :, 4], self.ref_std_range)
        condition3 = np.logical_and(condition1, condition2)
        condition = np.logical_and(condition, condition3)
        idx = np.where(condition)
        print u'Ref过滤 = %d' % len(idx[0])

        # ########### 相对方位角(RelativeAngle)过滤，5*5 的 Avg
        condition1 = self.get_condition(self.Azimuth[:, 3], self.ra_range)
        condition = np.logical_and(condition, condition1)
        idx = np.where(condition)
        print u'相对方位角(RelativeAngle)过滤 = %d' % len(idx[0])

        # ########### Percent 过滤，F4 多1个维度6个通道，F3 只有2维，使用 5*5
        condition1 = self.get_condition(self.DCC_Percent[3, :, 2], self.percent_range)
        condition = np.logical_and(condition, condition1)
        idx = np.where(condition)
        print u'Percent 过滤 = %d' % len(idx[0])

        # ########### 经纬度过滤，静止取卫星星下点 ±20 度，极轨卫星 ±180
        condition1 = self.get_condition(self.Latitude, self.lat_range)
        condition2 = self.get_condition(self.Longitude, self.lon_range)
        condition3 = np.logical_and(condition1, condition2)
        condition = np.logical_and(condition, condition3)
        idx = np.where(condition)
        print u'经纬度过滤 = %d' % len(idx[0])

        # ########### 太阳天顶角(SunZenith)过滤，5*5 的 Avg
        condition1 = self.get_condition(self.SunZenith[:, 3], self.sza_range)
        condition = np.logical_and(condition, condition1)
        idx = np.where(condition)
        print u'太阳天顶角(SunZenith)过滤 = %d' % len(idx[0])

        # ########### 太阳方位角(SunAzimuth)过滤，5*5 的 Avg
        condition1 = self.get_condition(self.SunAzimuth[:, 3], self.saa_range)
        condition = np.logical_and(condition, condition1)
        idx = np.where(condition)
        print u'太阳方位角(SunAzimuth)过滤 = %d' % len(idx[0])

        # ########### 观测天顶角(SatelliteZenith)过滤，5*5 的 Avg
        condition1 = self.get_condition(self.SatelliteZenith[:, 3], self.vza_range)
        condition = np.logical_and(condition, condition1)
        idx = np.where(condition)
        print u'观测天顶角(SatelliteZenith)过滤 = %d' % len(idx[0])

        # ########### 耀斑角(SunGlint)过滤，5*5 的 Avg
        condition1 = self.get_condition(self.SunGlint, self.sga_range)
        condition = np.logical_and(condition, condition1)
        idx = np.where(condition)
        print u'耀斑角(SunGlint)过滤 = %d' % len(idx[0])

        self.idx = idx
        if len(self.idx[0]) == 0:
            print "Data count equal to 0."
            self.error = True
            return

    @staticmethod
    def dcc_cal_des(ymd):
        # des=（当前日期的日地距离/平均日地距离）的平方
        #     year=2016
        #     month=10day=08;
        #     yd = dayofyear(year, month, day);  # 该天为一年中的第几天
        yd = int((datetime.strptime(ymd, '%Y%m%d')).strftime('%j'))

        date_s = datetime.strptime('%s0101' % ymd[:4], '%Y%m%d')
        date_e = datetime.strptime('%s1231' % ymd[:4], '%Y%m%d')
        days_year = (date_e - date_s).days

        x = 2 * np.pi * (yd - 1) / float(days_year)  # / daysinyear(year);  # % 该年有多少天

        des = 1.000109 + 0.033494 * np.cos(x) + 0.001472 * np.sin(x) + 0.000768 * np.cos(
            2 * x) + 0.000079 * np.sin(2 * x)
        return 1. / des

    def cal_adms(self, ymd):
        """
        计算Adms
        :return:
        """
        if self.error:
            return

        X = np.arange(5, 176)
        Y = np.arange(5, 86)
        Z = np.arange(5, 46)

        n_adms = np.swapaxes(self.ADMs, 0, -1)

        RA = self.Azimuth[self.idx, 3] / 100.
        SZA = self.SunZenith[self.idx, 3] / 100.
        VZA = self.SatelliteZenith[self.idx, 3] / 100.
        listASV = []

        for i in range(len(RA)):
            listASV.append(VZA[i])
            listASV.append(RA[i])
            listASV.append(SZA[i])
        self.ADMs_pixle1 = interpn((Y, X, Z), n_adms, listASV)

        # 计算des
        des = self.dcc_cal_des(ymd)

        # TODO 计算 ADMs，目前的方法不正确
        DN_ADMs = self.DN_Avg_Std[:, self.idx[0], 5] / 100. / np.cos(
            np.deg2rad(SZA)) * des / self.ADMs_pixle1
        DN5_ADMs = self.IR_Avg_Std[self.idx[0], 5] / np.cos(
            np.deg2rad(SZA)) * des / self.ADMs_pixle1
        self.DN_AMDs = np.insert(DN_ADMs, 4, DN5_ADMs, 0)
        self.DN_AMDs = np.swapaxes(self.DN_AMDs, 0, 1)

        self.Ref_ADMs = self.Ref_Avg_Std[:, self.idx[0], 5] / np.cos(
            np.deg2rad(SZA)) * des / self.ADMs_pixle1
        self.Ref_ADMs = np.swapaxes(self.Ref_ADMs, 0, 1)

        # * 100 取整

    def write_slt(self, out_file):
        """
        输出slt精提取文件
        :param out_file:
        :return:
        """
        with h5py.File(out_file, 'w') as h5:
            h5.create_dataset('ADMs', dtype='f4', data=self.ADMs, compression='gzip',
                              compression_opts=5,
                              shuffle=True)
            h5.create_dataset('BT_Avg_Std', dtype='i4', data=self.BT_Avg_Std[self.idx, :],
                              compression='gzip', compression_opts=5, shuffle=True)
            h5.create_dataset('DCC_Percent', dtype='i4', data=self.DCC_Percent[self.idx, :],
                              compression='gzip', compression_opts=5, shuffle=True)
            h5.create_dataset('DN_ADMs', dtype='i4', data=self.DN_ADMs, compression='gzip',
                              compression_opts=5, shuffle=True)
            h5.create_dataset('DN_Avg_Std', dtype='i4', data=self.DN_Avg_Std[:, self.idx, :],
                              compression='gzip', compression_opts=5, shuffle=True)
            h5.create_dataset('IR_Avg_Std', dtype='i4', data=self.IR_Avg_Std[self.idx, :],
                              compression='gzip', compression_opts=5, shuffle=True)
            h5.create_dataset('IR_CAL', dtype='f4', data=self.IR_CAL[self.idx, :],
                              compression='gzip',
                              compression_opts=5, shuffle=True)
            h5.create_dataset('REF_ADMs', dtype='i4', data=self.Ref_ADMs, compression='gzip',
                              compression_opts=5, shuffle=True)
            h5.create_dataset('Ref_Avg_Std', dtype='i4', data=self.Ref_Avg_Std[:, self.idx, :],
                              compression='gzip', compression_opts=5, shuffle=True)
            h5.create_dataset('Longitude', dtype='i4', data=self.Longitude[self.idx],
                              compression='gzip',
                              compression_opts=5, shuffle=True)
            h5.create_dataset('Latitude', dtype='i4', data=self.Latitude[self.idx],
                              compression='gzip',
                              compression_opts=5, shuffle=True)
            h5.create_dataset('LandCover', dtype='i4', data=self.LandCover[self.idx],
                              compression='gzip',
                              compression_opts=5, shuffle=True)
            h5.create_dataset('Line_Num', dtype='i4', data=self.Line_Num[self.idx],
                              compression='gzip',
                              compression_opts=5, shuffle=True)

            h5.create_dataset('SatelliteAzimuth', dtype='i4',
                              data=self.SatelliteAzimuth[self.idx, :],
                              compression='gzip', compression_opts=5, shuffle=True)
            h5.create_dataset('SatelliteZenith', dtype='i4', data=self.SatelliteZenith[self.idx, :],
                              compression='gzip', compression_opts=5, shuffle=True)
            h5.create_dataset('SunAzimuth', dtype='i4', data=self.SunAzimuth[self.idx, :],
                              compression='gzip', compression_opts=5, shuffle=True)
            h5.create_dataset('SunGlint', dtype='i4', data=self.SunGlint[self.idx],
                              compression='gzip',
                              compression_opts=5, shuffle=True)
            h5.create_dataset('Azimuth', dtype='i4', data=self.Azimuth[self.idx],
                              compression='gzip',
                              compression_opts=5, shuffle=True)
            h5.create_dataset('SunZenith', dtype='i4', data=self.SunZenith[self.idx, :],
                              compression='gzip',
                              compression_opts=5, shuffle=True)
            h5.create_dataset('TIME', dtype='i4', data=self.TIME[self.idx, :], compression='gzip',
                              compression_opts=5, shuffle=True)
            h5.create_dataset('VIS_CAL', dtype='f4', data=self.VIS_CAL[:, self.idx, :],
                              compression='gzip',
                              compression_opts=5, shuffle=True)
