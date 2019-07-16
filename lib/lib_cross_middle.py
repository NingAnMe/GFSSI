# -*- coding: utf-8 -*-

import gc
import sys

import h5py

from DP.dp_2d import rolling_2d_window_pro
from PB import DRC as drc
import numpy as np


__description__ = u'静止和极轨通用匹配程序'
__author__ = 'wangpeng'
__date__ = '2018-09-06'
__version__ = '1.0.0_beat'

high_spec_sensor = ['IASI', 'CRIS', 'HIRAS', 'AIRS']


class GetMiddleDataFromFile():

    def __init__(self, in_file):
        self.load_data(in_file)

    def load_data(self, in_file):

        with h5py.File(in_file, 'r') as h5file_r:
            for key in h5file_r.keys():
                pre_rootgrp = h5file_r.get(key)  # 获取根下名字
                if type(pre_rootgrp).__name__ == "Group":
                    # 组下的所有数据集
                    for key_grp in pre_rootgrp.keys():
                        if not hasattr(self, key_grp):
                            self.__dict__[key_grp] = {}
                        dset_path = '/' + key + '/' + key_grp
                        self.__dict__[key_grp][
                            key] = h5file_r.get(dset_path)[:]

                # 根下的数据集
                else:
                    self.__dict__[key] = h5file_r.get(key)[:]


class GetMiddleData():
    """
    u 中间投影数据获取类,根据投影查找表对L1数据进行读取
    """

    def __init__(self, mode, p1, p2):

        self.mode = mode
        self.row = p1.row
        self.col = p1.col
        self.lut1 = p1.lut_dict
        self.lut2 = p2.lut_dict
        self.sensor1 = mode.sensor1
        self.sensor2 = mode.sensor2

        self.fill = -999.
        self.dtype = 'f4'
        self.MaskPub = None   # 公共区域掩码
        self.set_mask_pub()

    def mask_wind_public_areas(self):
        # 原始网格大小
        row, col = self.MaskPub.shape

        # 掩模窗口大小
        m_row, m_col = self.mode.mask_wind

        # 掩模窗口中心位置
        m_row_idx, m_col_idx = (m_row / 2, m_col / 2)

        # 按照窗口分块后新数据的大小
        n_row, n_col = (row // m_row, col // m_col)

        # 把数据拆成多个8*8
        new_mask_shape = (n_row, m_row, n_col, m_col)
        new_mask = self.MaskPub.reshape(new_mask_shape)

        # 记录新维度数据的索引号
        l1 = []
        l2 = []
        l3 = []
        l4 = []

        for i in xrange(n_row):
            for j in xrange(n_col):
                c = new_mask[i, :, j, :]
                idx = np.where(c == 1)
                if len(idx[0]) > 0:
                    pass
                else:
                    continue
                x, y = np.where(c == 1)
                a = np.power(x - m_row_idx, 2)
                b = np.power(y - m_col_idx, 2)
                dis = np.sqrt(a + b)
                min_idx = np.argmin(dis)
                l1.append(i)
                l2.append(x[min_idx])
                l3.append(j)
                l4.append(y[min_idx])

        # 把4维索引转1维，在转2维
        mask_idx = (np.array(l1, dtype=np.int64), np.array(
            l2, dtype=np.int64), np.array(l3), np.array(l4))
        i = np.ravel_multi_index(mask_idx, new_mask_shape)
        ix, jy = np.unravel_index(i, (row, col))

        # 清零
        self.MaskPub[:] = 0

        # 置位
        self.MaskPub[ix, jy] = 1

        idx = np.where(self.MaskPub == 1)
        print u'mask wind 后公共区域匹配点个数: %d' % len(idx[0])

    def save_only_public_areas(self):
        """
        True 保留公共区域的投影数据
        False 要保留所有投影数据
        """
        pub_idx = np.where(self.MaskPub == 1)
        pub_pij = zip(pub_idx[0], pub_idx[1])
        # 公共区域位置
        for in_file in self.lut1.keys():
            pi = self.lut1[in_file][0]
            pj = self.lut1[in_file][1]
            # 转元组，设置集合,取投影交集的行列
            pij = zip(pi, pj)
            p_ij = set(pub_pij) & set(pij)
            # 没有交集
            if not p_ij:
                self.lut1.pop(in_file)
                continue
            idx1 = np.array(list(p_ij))
            p_i = idx1[:, 0]
            p_j = idx1[:, 1]
            # 根据投影交集的行列取数据行列
            di = self.mask_pub1_i[p_i, p_j]
            dj = self.mask_pub1_j[p_i, p_j]
            self.lut1[in_file] = [p_i, p_j, di, dj]
        for in_file in self.lut2.keys():
            pi = self.lut2[in_file][0]
            pj = self.lut2[in_file][1]
            # 转元组，设置集合,取投影交集的行列
            pij = zip(pi, pj)
            p_ij = set(pub_pij) & set(pij)
            # 没有交集
            if not p_ij:
                self.lut2.pop(in_file)
                continue
            idx1 = np.array(list(p_ij))
            p_i = idx1[:, 0]
            p_j = idx1[:, 1]
            # 根据投影交集的行列取数据行列
            di = self.mask_pub2_i[p_i, p_j]
            dj = self.mask_pub2_j[p_i, p_j]
            self.lut2[in_file] = [p_i, p_j, di, dj]

    def set_mask_pub(self):

        # 公共区域的掩码
        if self.MaskPub is None:
            # 用来记录数据1,2的投影位置
            self.mask_pub1_i = np.full((self.row, self.col), -1, 'i2')
            self.mask_pub1_j = np.full((self.row, self.col), -1, 'i2')
            self.mask_pub2_i = np.full((self.row, self.col), -1, 'i2')
            self.mask_pub2_j = np.full((self.row, self.col), -1, 'i2')
            self.MaskPub = np.full((self.row, self.col), 0, 'i2')

        # 开始对数据1投影位置做标记
        for in_file in sorted(self.lut1.keys()):
            pi = self.lut1[in_file][0]
            pj = self.lut1[in_file][1]
            di = self.lut1[in_file][2]
            dj = self.lut1[in_file][3]
            self.mask_pub1_i[pi, pj] = di
            self.mask_pub1_j[pi, pj] = dj
        # 开始对数据2投影位置做标记
        for in_file in sorted(self.lut2.keys()):
            pi = self.lut2[in_file][0]
            pj = self.lut2[in_file][1]
            di = self.lut2[in_file][2]
            dj = self.lut2[in_file][3]
            self.mask_pub2_i[pi, pj] = di
            self.mask_pub2_j[pi, pj] = dj

        # 数据1，2的公共区域位置记录
        idx1 = np.where(self.mask_pub1_i >= 0)
        idx2 = np.where(self.mask_pub2_i >= 0)
        condition = np.logical_and(
            self.mask_pub1_i >= 0, self.mask_pub2_i >= 0)
        idx = np.where(condition)
        print u'数据1投影点数: %d' % len(idx1[0])
        print u'数据2投影点数: %d' % len(idx2[0])
        print u'公共区域匹配点个数: %d' % len(idx[0])

        if len(idx1[0]) == 0 or len(idx2[0]) == 0:
            print 'exit'
            sys.exit(1)

        # 公共区域标志位设置成1
        self.MaskPub[condition] = 1

    def correct_target_ref_data(self):
        '''
        u 订正第二颗传感器可见光通道的ref值
        '''
        coeff = np.cos(np.deg2rad(self.S1_SolZ)) / \
            np.cos(np.deg2rad(self.S2_SolZ))
        for band in sorted(self.S1_FovRefMean.keys()):
            if self.S2_FovRefMean[band] is not None:
                print '订正 sensor2 ref band %s' % band
                idx = np.where(self.S2_FovRefMean[band] > 0)
                self.S2_FovRefMean[band][idx] = self.S2_FovRefMean[
                    band][idx] * coeff[idx]
                idx = np.where(self.S2_EnvRefMean[band] > 0)
                self.S2_EnvRefMean[band][idx] = self.S2_EnvRefMean[
                    band][idx] * coeff[idx]

    def get_longitude(self):
        fname = sys._getframe().f_code.co_name
        self.S1_Lon = self.__get_data_dim2(fname, self.lut1, self.sensor1)
        self.S2_Lon = self.__get_data_dim2(fname, self.lut2, self.sensor2)

    def get_latitude(self):
        fname = sys._getframe().f_code.co_name
        self.S1_Lat = self.__get_data_dim2(fname, self.lut1, self.sensor1)
        self.S2_Lat = self.__get_data_dim2(fname, self.lut2, self.sensor2)

    def get_timestamp(self):
        fname = sys._getframe().f_code.co_name
        self.S1_Time = self.__get_data_dim2(fname, self.lut1, self.sensor1)
        self.S2_Time = self.__get_data_dim2(fname, self.lut2, self.sensor2)

    def get_sensor_zenith(self):
        fname = sys._getframe().f_code.co_name
        self.S1_SatZ = self.__get_data_dim2(fname, self.lut1, self.sensor1)
        self.S2_SatZ = self.__get_data_dim2(fname, self.lut2, self.sensor2)

    def get_sensor_azimuth(self):
        fname = sys._getframe().f_code.co_name
        self.S1_SatA = self.__get_data_dim2(fname, self.lut1, self.sensor1)
        self.S2_SatA = self.__get_data_dim2(fname, self.lut2, self.sensor2)

    def get_solar_zenith(self):
        fname = sys._getframe().f_code.co_name
        self.S1_SolZ = self.__get_data_dim2(fname, self.lut1, self.sensor1)
        self.S2_SolZ = self.__get_data_dim2(fname, self.lut2, self.sensor2)

    def get_solar_azimuth(self):
        fname = sys._getframe().f_code.co_name
        self.S1_SolA = self.__get_data_dim2(fname, self.lut1, self.sensor1)
        self.S2_SolA = self.__get_data_dim2(fname, self.lut2, self.sensor2)

    def get_dn(self):
        fname = sys._getframe().f_code.co_name
        fov_wind1 = self.mode.fov_wind1
        env_wind1 = self.mode.env_wind1
        fov_wind2 = self.mode.fov_wind2
        env_wind2 = self.mode.env_wind2
        band_list1 = self.mode.chan1
        mean1, std1, mean2, std2 = self.__get_data_dim3_mean_std(
            fname, band_list1, fov_wind1, env_wind1, self.lut1, self.sensor1)

        # 增加类成员
        self.S1_FovDnMean = mean1
        self.S1_FovDnStd = std1
        self.S1_EnvDnMean = mean2
        self.S1_EnvDnStd = std2

        band_list2 = self.__band2band(band_list1)
        mean1, std1, mean2, std2 = self.__get_data_dim3_mean_std(
            fname, band_list2, fov_wind2, env_wind2, self.lut2, self.sensor2)

        if mean1 is not None:
            # 交换使用
            mean11 = {}
            std11 = {}
            mean22 = {}
            std22 = {}
            # 通道对等到风云
            for band1, band2 in zip(band_list1, band_list2):
                mean11[band1] = mean1[band2]
                std11[band1] = std1[band2]
                mean22[band1] = mean2[band2]
                std22[band1] = std2[band2]

            # 增加类成员
            self.S2_FovDnMean = mean11
            self.S2_FovDnStd = std11
            self.S2_EnvDnMean = mean22
            self.S2_EnvDnStd = std22

    def get_rad(self):

        fname = sys._getframe().f_code.co_name
        fov_wind1 = self.mode.fov_wind1
        env_wind1 = self.mode.env_wind1
        fov_wind2 = self.mode.fov_wind2
        env_wind2 = self.mode.env_wind2

        # 红外通道
        band_list1 = self.mode.band_ir
        mean1, std1, mean2, std2 = self.__get_data_dim3_mean_std(
            fname, band_list1, fov_wind1, env_wind1, self.lut1, self.sensor1)
        self.S1_FovRadMean = mean1
        self.S1_FovRadStd = std1
        self.S1_EnvRadMean = mean2
        self.S1_EnvRadStd = std2

        # 获取数据1的信息

        if self.sensor2 in high_spec_sensor:
            in_file = self.lut1.keys()[0]
            sensor1 = self.sensor1.capitalize()
            d1 = eval('drc.Read%sL1' % sensor1)(in_file)
            wave_nums, wave_spec = d1.get_spectral_response()
            central_wave_numbers = d1.get_central_wave_number()
            a = d1.get_tbb_k1()
            b = d1.get_tbb_k0()
            lut_bt = d1.get_lut_bt()
#             lut_bt = None
        else:
            wave_nums = None
            wave_spec = None
            central_wave_numbers = None
            a = None
            b = None
            lut_bt = None

        # 红外通道
        band_list2 = self.__band2band(band_list1)

        mean1, std1, mean2, std2 = self.__get_data_dim3_mean_std(
            fname, band_list2, fov_wind2, env_wind2, self.lut2, self.sensor2,
            wave_nums, wave_spec, central_wave_numbers, a, b, lut_bt)
        if mean1 is not None:
            # 交换使用
            mean11 = {}
            std11 = {}
            mean22 = {}
            std22 = {}
            # 通道对等到风云
            for band1, band2 in zip(band_list1, band_list2):
                mean11[band1] = mean1[band2]
                std11[band1] = std1[band2]
                mean22[band1] = mean2[band2]
                std22[band1] = std2[band2]

            self.S2_FovRadMean = mean11
            self.S2_FovRadStd = std11
            self.S2_EnvRadMean = mean22
            self.S2_EnvRadStd = std22

    def get_tbb(self):
        fname = sys._getframe().f_code.co_name
        fov_wind1 = self.mode.fov_wind1
        env_wind1 = self.mode.env_wind1
        fov_wind2 = self.mode.fov_wind2
        env_wind2 = self.mode.env_wind2

        # 红外通道
        band_list1 = self.mode.band_ir
        mean1, std1, mean2, std2 = self.__get_data_dim3_mean_std(
            fname, band_list1, fov_wind1, env_wind1, self.lut1, self.sensor1)

        self.S1_FovTbbMean = mean1
        self.S1_FovTbbStd = std1
        self.S1_EnvTbbMean = mean2
        self.S1_EnvTbbStd = std2

        # 获取数据1的信息
        if self.sensor2 in high_spec_sensor:
            in_file = self.lut1.keys()[0]
            sensor1 = self.sensor1.capitalize()
            d1 = eval('drc.Read%sL1' % sensor1)(in_file)
            wave_nums, wave_spec = d1.get_spectral_response()
            central_wave_numbers = d1.get_central_wave_number()
            a = d1.get_tbb_k1()
            b = d1.get_tbb_k0()
            lut_bt = d1.get_lut_bt()
#             lut_bt = None
        else:
            wave_nums = None
            wave_spec = None
            central_wave_numbers = None
            a = None
            b = None
            lut_bt = None

        # 红外通道
        band_list2 = self.__band2band(band_list1)

        mean1, std1, mean2, std2 = self.__get_data_dim3_mean_std(
            fname, band_list2, fov_wind2, env_wind2, self.lut2, self.sensor2,
            wave_nums, wave_spec, central_wave_numbers, a, b, lut_bt)

        if mean1 is not None:
            # 交换使用
            mean11 = {}
            std11 = {}
            mean22 = {}
            std22 = {}
            # 通道对等到风云
            for band1, band2 in zip(band_list1, band_list2):
                mean11[band1] = mean1[band2]
                std11[band1] = std1[band2]
                mean22[band1] = mean2[band2]
                std22[band1] = std2[band2]

            self.S2_FovTbbMean = mean11
            self.S2_FovTbbStd = std11
            self.S2_EnvTbbMean = mean22
            self.S2_EnvTbbStd = std22

    def get_ref(self):
        fname = sys._getframe().f_code.co_name
        fov_wind1 = self.mode.fov_wind1
        env_wind1 = self.mode.env_wind1
        fov_wind2 = self.mode.fov_wind2
        env_wind2 = self.mode.env_wind2

        band_list1 = self.mode.band_vis
        mean1, std1, mean2, std2 = self.__get_data_dim3_mean_std(
            fname, band_list1, fov_wind1, env_wind1, self.lut1, self.sensor1)

        # 增加类成员
        self.S1_FovRefMean = mean1
        self.S1_FovRefStd = std1
        self.S1_EnvRefMean = mean2
        self.S1_EnvRefStd = std2

        band_list2 = self.__band2band(band_list1)

        mean1, std1, mean2, std2 = self.__get_data_dim3_mean_std(
            fname, band_list2, fov_wind2, env_wind2, self.lut2, self.sensor2)

        if mean1 is not None:
            # 交换使用
            mean11 = {}
            std11 = {}
            mean22 = {}
            std22 = {}
            # 通道对等到风云
            for band1, band2 in zip(band_list1, band_list2):
                mean11[band1] = mean1[band2]
                std11[band1] = std1[band2]
                mean22[band1] = mean2[band2]
                std22[band1] = std2[band2]
            # 增加类成员
            self.S2_FovRefMean = mean11
            self.S2_FovRefStd = std11
            self.S2_EnvRefMean = mean22
            self.S2_EnvRefStd = std22

    def get_land_sea_mask(self):
        fname = sys._getframe().f_code.co_name
        data = self.__get_data_dim2(fname, self.lut1, self.sensor1)
        if data is not None:
            self.S1_LandSeaMask = data
        data = self.__get_data_dim2(fname, self.lut2, self.sensor2)
        if data is not None:
            self.S2_LandSeaMask = data

    def get_land_cover(self):
        fname = sys._getframe().f_code.co_name
        data = self.__get_data_dim2(fname, self.lut1, self.sensor1)
        if data is not None:
            self.S1_LandSeaMask = data
        data = self.__get_data_dim2(fname, self.lut2, self.sensor2)
        if data is not None:
            self.S2_LandSeaMask = data

    def get_sv(self):
        fname = sys._getframe().f_code.co_name
        band_list1 = self.mode.chan1
        band_list2 = self.mode.chan2
        data = self.__get_data_dim3(fname, band_list1, self.lut1, self.sensor1)

        if data is not None:
            self.S1_SV = data

        data = self.__get_data_dim3(fname, band_list2, self.lut2, self.sensor2)

        if data is not None:
            data1 = {}
            for band1, band2 in zip(band_list1, band_list2):
                data1[band1] = data[band2]

            self.S2_SV = data1

    def get_bb(self):
        fname = sys._getframe().f_code.co_name
        band_list1 = self.mode.chan1
        band_list2 = self.mode.chan2
        data = self.__get_data_dim3(fname, band_list1, self.lut1, self.sensor1)

        if data is not None:
            self.S1_BB = data

        data = self.__get_data_dim3(fname, band_list2, self.lut2, self.sensor2)

        if data is not None:
            data1 = {}
            for band1, band2 in zip(band_list1, band_list2):
                data1[band1] = data[band2]

            self.S2_BB = data1

    def get_spectral_response(self, mask):
        """
        u 目前只获取s2的光谱响应值，返回所有投影后位置的光谱
        u lut查找表是公共区域的就保留公共的，是各自的就保留s2的投影后光谱
        """
        fname = sys._getframe().f_code.co_name
        data_pre = {}  # 存放需要的光谱 字典 无顺序
        data_pre_list = []  # 存放需要的光谱
        # 根据mask找公共区域
        pub_idx = np.where(mask == 1)
        pub_pij = set(zip(pub_idx[0], pub_idx[1]))

        # 对投影后位置的实际经纬度赋值
        for in_file in sorted(self.lut2.keys()):
            pi = self.lut2[in_file][0]
            pj = self.lut2[in_file][1]
            di = self.lut2[in_file][2]
            dj = self.lut2[in_file][3]
            sensor = self.sensor2.capitalize()
            d1 = eval('drc.Read%sL1' % sensor)(in_file)
            _, response = eval('d1.%s()' % fname)

            for i in xrange(len(pi)):
                x1 = pi[i]
                y1 = pj[i]
                x2 = di[i]
                y2 = dj[i]
                pij = (x1, y1)
                if pij in pub_pij:
                    data_pre[pij] = response[x2, y2, :]
        # 排序
        for ij in sorted(data_pre.keys()):
            data_pre_list.append(data_pre[ij])

        self.S2_Spec = (np.array(data_pre_list)).astype('float32')
        self.S2_SpecRow = pub_idx[0].astype('uint16')
        self.S2_SpecCol = pub_idx[1].astype('uint16')

    def __get_data_dim2(self, name, lut, sensor):

        return_value = None
        data_pre = np.full((self.row, self.col), self.fill, self.dtype)
        # 对投影后位置的实际经纬度赋值
        for in_file in sorted(lut.keys()):
            pi = lut[in_file][0]
            pj = lut[in_file][1]
            di = lut[in_file][2]
            dj = lut[in_file][3]
            sensor = sensor.capitalize()
            d1 = eval('drc.Read%sL1' % sensor)(in_file)
            in_data = eval('d1.%s()' % name)
            if in_data is None:
                return return_value
            data_pre[pi, pj] = in_data[di, dj]
            del in_data
            gc.collect()

        return data_pre

    def __get_data_dim3(self, name, band_list, lut, sensor):

        return_value = None
        # 开辟空间
        data_pre = dict()
        for band in band_list:
            data_pre[band] = np.full(
                (self.row, self.col), self.fill, self.dtype)
        # 对投影后位置的实际经纬度赋值
        for in_file in sorted(lut.keys()):
            pi = lut[in_file][0]
            pj = lut[in_file][1]
            di = lut[in_file][2]
            dj = lut[in_file][3]
            sensor = sensor.capitalize()
            d1 = eval('drc.Read%sL1' % sensor)(in_file)
            in_data = eval('d1.%s()' % name)
            if not in_data:
                return return_value
            for band in band_list:
                if band in in_data.keys():
                    data_pre[band][pi, pj] = in_data[band][di, dj]
                    del in_data[band]
                    gc.collect()
        return data_pre

    def __get_data_dim3_mean_std(self, name, band_list, wind1, wind2,
                                 lut, sensor, wave_nums=None, wave_spec=None,
                                 central_wave_nums=None, a=None, b=None, lut_bt=None):

        # 开辟空间
        mean1 = dict()
        std1 = dict()
        mean2 = dict()
        std2 = dict()

        return_value = [None, None, None, None]

        for band in band_list:
            mean1[band] = np.full((self.row, self.col), self.fill, self.dtype)
            std1[band] = np.full((self.row, self.col), self.fill, self.dtype)
            mean2[band] = np.full((self.row, self.col), self.fill, self.dtype)
            std2[band] = np.full((self.row, self.col), self.fill, self.dtype)

        for in_file in sorted(lut.keys()):
            pi = lut[in_file][0]
            pj = lut[in_file][1]
            di = lut[in_file][2]
            dj = lut[in_file][3]
            sensor = sensor.capitalize()
            d1 = eval('drc.Read%sL1' % sensor)(in_file)
            if wave_nums is None:
                in_data = eval('d1.%s()' % name)
            else:
                in_data = eval('d1.%s' % name)(
                    wave_nums, wave_spec, band_list, central_wave_nums, a, b, lut_bt)
            if not in_data:
                return return_value
            # 获取要获取的通道的值
            for band in band_list:
                if band in in_data.keys():
                    # 靶区
                    mean, std, pii, pjj = rolling_2d_window_pro(
                        in_data[band], wind1, di, dj, pi, pj)
                    mean1[band][pii, pjj] = mean
                    std1[band][pii, pjj] = std

                    # 环境
                    mean, std, pii, pjj = rolling_2d_window_pro(
                        in_data[band], wind2, di, dj, pi, pj)
                    mean2[band][pii, pjj] = mean
                    std2[band][pii, pjj] = std
                    del in_data[band]
                    gc.collect()

        return mean1, std1, mean2, std2

    def __band2band(self, band_list1):
        band_list2 = []
        for band1 in band_list1:
            index = self.mode.chan1.index(band1)
            band2 = self.mode.chan2[index]
            band_list2.append(band2)
        return band_list2
