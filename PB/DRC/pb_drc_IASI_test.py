# -*- coding: utf-8 -*-

from datetime import datetime
import os
import re
import time

import beatl2
import coda

from PB.pb_sat import planck_r2t, spec_interp, spec_convolution
from PB.pb_time import time_block
from pb_drc_base import ReadL1
import numpy as np


__description__ = u'IASI传感器读取'
__author__ = 'wangpeng'
__date__ = '2018-08-28'
__version__ = '1.0.0_beat'

g_main_path, g_main_file = os.path.split(os.path.realpath(__file__))


class ReadIasiL1(ReadL1):
    """
    读取 IASI 传感器的 L1 数据
    分辨率：24KM （4 x 12-km IFOV close to the centre of a 48 x 48 km2 cell (average sampling distance: 24 km)）
    卫星： [Metop-A Metop-B]
    通道数量：
    红外通道：8461
    """

    def __init__(self, in_file):
        sensor = 'IASI'
        super(ReadIasiL1, self).__init__(in_file, sensor)

    def set_resolution(self):
        """
        use filename set self.resolution
        """
        file_name = os.path.basename(self.in_file)
        if 'IASI' in file_name:
            self.resolution = 24000
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))

    def set_satellite(self):
        """
        use filename set self.satellite
        """
        file_name = os.path.basename(self.in_file)

        if 'M02' in file_name:
            self.satellite = 'METOP-A'
        elif 'M01' in file_name:
            self.satellite = 'METOP-B'
        else:
            raise ValueError('Cant get the satellite name from file name.')

    def set_ymd_hms(self):
        """
        use filename  set self.ymd self.hms
        """
        file_name = os.path.basename(self.in_file)
        pat = u'\w+_(\d{14})Z_(\d{14})Z_N_O_\d{14}Z__\d{14}$'
        g = re.match(pat, file_name)
        if g:
            self.ymd = g.group(1)[:8]
            self.hms = g.group(1)[8:]
        else:
            raise ValueError('Cant get the ymdhms from file name.')

    def set_file_attr(self):
        """
        seft self.file_att is dict 
        """
        data = dict()
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']
            if self.satellite in satellite_type1:

                try:
                    fp = coda.open(self.in_file)
                    product_class = coda.get_product_class(fp)
                    product_type = coda.get_product_type(fp)
                    product_version = coda.get_product_version(fp)
                    product_format = coda.get_product_format(fp)
                    product_size = coda.get_product_file_size(fp)
                    coda.close(fp)
                except Exception as e:
                    print str(e)
                    return

                data['class'] = product_class
                data['size'] = product_size
                data['type'] = product_type
                data['version'] = product_version
                data['format'] = product_format
                self.file_attr = data
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                "Cant handle this resolution: ".format(self.resolution))

    def set_channels(self):
        """
        return sensor channels
        """
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']
            if self.satellite in satellite_type1:
                self.channels = 8461
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))

    def set_data_shape(self):
        """
        set self.data_shape
        """
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']
            if self.satellite in satellite_type1:
                try:
                    self.record = beatl2.ingest(self.in_file)
                    # iasi 的观测点会变化 2640 2760等，所以根据数据长度获取，另外统一转成2维
                    self.data_shape = (self.record.time.shape[0], 1)
                except Exception as e:
                    print 'Open file error {}'.format(e)
                    return
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        # elif self.resolution == 250:
        else:
            raise ValueError(
                "Cant handle this resolution: ".format(self.resolution))

    def get_spectral_response(self):
        """
        return 光谱波数和响应值，1维，2维
        """
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']
            if self.satellite in satellite_type1:
                try:
                    # record = beatl2.ingest(self.in_file)
                    # 单位转换
                    response = self.record.spectral_radiance * 10 ** 7
                    s = response.shape
                    response = response.reshape(s[0], 1, s[1])
                    # 会随机产生nan值，(导致卷积)目前定位在投影代码段后，或是输出一次这个变量都会有影响
                    data_pre = np.nan_to_num(response)
                    condition = np.logical_or(data_pre < -10, data_pre > 200)
                    idx = np.where(condition)
#                     print len(idx[0])
                    if len(idx[0] > 0):
                        data_pre[idx] = 0.
                    response = data_pre
#                     idx = np.where(response < -10)
#                     print len(idx[0])
#                     if len(idx[0] > 0):
#                         response[idx] = 0.
                    # 暂时取一个观测的光谱波数
                    wave_number = self.record.wavenumber[0, :]

                except Exception as e:
                    print 'Open file error {}'.format(e)
                    return
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return wave_number, response

    def get_rad(self, wave_nums, wave_spec, band_list, central_wave_nums, a, b, lut):
        """
        wave_nums: 波数cm-1（字典形式，key是通道信息，针对FY数据）
        wave_spec: 响应0-1（字典形式，key是通道信息，针对FY数据）
        band_list： CH_20-CH_25
        center_wave_nums: 目前未用，只是为了和get_tbb统一
        a: 目前未用，只是为了和get_tbb统一
        b: 目前未用，只是为了和get_tbb统一
        return channel rad
        """
        data = dict()
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']

            if self.satellite in satellite_type1:
                # 获取iasi的光谱响应
                wave_nums2, response = self.get_spectral_response()
                for band in sorted(band_list):
                    wave_nums1 = wave_nums[band]
                    wave_spec1 = wave_spec[band]

                    # 插值 把FY插值到IASI上
                    wave_spec2 = spec_interp(
                        wave_nums1, wave_spec1, wave_nums2)
                    # 对应FY的响应值，大小一致就可以和FY比较了，响应是IASI的

                    rads = spec_convolution(wave_nums2, wave_spec2, response)
#                     print band, np.allclose(rads, np.nan, equal_nan=True)
                    # 过滤<=0的结果
                    idx = np.where(rads <= 0.)
                    if len(idx[0] > 0):
                        rads[idx] = np.nan

                    data[band] = rads  # .reshape(rads.size, 1)

            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

    def get_tbb(self, wave_nums, wave_spec, band_list, central_wave_nums, a, b, lut):
        """
        use 卫星1的光谱和响应wave_nums,wave_spec（字典形式，key是通道信息，针对FY数据）
        a,b 分别是红外tbb修正系数，字典 ，key是通道信息
        return channel rad
        """
        data = dict()
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']

            if self.satellite in satellite_type1:
                # 目标数据通道信息
                # 获取通道的rads
                rads = self.get_rad(
                    wave_nums, wave_spec, band_list, central_wave_nums, a, b, lut)
                for band in band_list:
                    rad = rads[band]
                    if lut:
                        print 'lut'
                        tbb = np.interp(rad, lut['rad'][band], lut['tbb'])
                        data[band] = tbb
                    else:
                        central_wave_number = central_wave_nums[band]
                        tbb = planck_r2t(rad, central_wave_number)
                        if a is not None:
                            k1 = a[band]
                            k0 = b[band]
                            data[band] = tbb * k1 + k0
                        else:
                            data[band] = tbb
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

    def get_longitude(self):
        """
        return longitude
        """
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']
            if self.satellite in satellite_type1:

                try:
                    # record = beatl2.ingest(self.in_file)
                    data_pre = self.record.longitude
                    invalid_index = np.logical_or(
                        data_pre < -180, data_pre > 180)
                    data_pre = data_pre.astype(np.float32)
                    data_pre[invalid_index] = np.nan
                    data = data_pre.reshape(data_pre.size, 1)

                except Exception as e:
                    print 'Open file error {}'.format(e)
                    return
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

    def get_latitude(self):
        """
        return latitude
        """
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']
            if self.satellite in satellite_type1:

                try:
                    #                     record = beatl2.ingest(self.in_file)
                    data_pre = self.record.latitude
                    invalid_index = np.logical_or(
                        data_pre < -90, data_pre > 90)
                    data_pre = data_pre.astype(np.float32)
                    data_pre[invalid_index] = np.nan
                    data = data_pre.reshape(data_pre.size, 1)

                except Exception as e:
                    print 'Open file error {}'.format(e)
                    return
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

    def get_sensor_azimuth(self):
        """
        return sensor_azimuth
        """
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']
            if self.satellite in satellite_type1:
                try:
                    fp = coda.open(self.in_file)
                    angle = coda.fetch(
                        fp, 'MDR', -1, 'MDR', 'GGeoSondAnglesMETOP')
                    coda.close(fp)

                    all_angle = []

                    for i in xrange(len(angle)):
                        tmp_angle = angle[i].reshape(-1)
                        if len(all_angle) == 0:
                            all_angle = tmp_angle
                        else:
                            all_angle = np.concatenate(
                                (all_angle, tmp_angle))

                    s0 = self.data_shape[0]
                    # 开始间隔一个取一个值，取奇数位
                    data_pre = (all_angle[1::2]).reshape(s0, 1)

                    # 过滤无效值
                    invalid_index = np.logical_or(
                        data_pre < 0, data_pre > 360)
                    data_pre = data_pre.astype(np.float32)
                    data_pre[invalid_index] = np.nan

                    data = data_pre

                except Exception as e:
                    print 'Open file error {}'.format(e)
                    return
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

    def get_sensor_zenith(self):
        """
        return sensor_zenith
        """
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']
            if self.satellite in satellite_type1:

                try:
                    fp = coda.open(self.in_file)
                    angle = coda.fetch(
                        fp, 'MDR', -1, 'MDR', 'GGeoSondAnglesMETOP')
                    coda.close(fp)

                    all_angle = []

                    for i in xrange(len(angle)):
                        tmp_angle = angle[i].reshape(-1)
                        if len(all_angle) == 0:
                            all_angle = tmp_angle
                        else:
                            all_angle = np.concatenate(
                                (all_angle, tmp_angle))

                    s0 = self.data_shape[0]
                    # 开始间隔一个取一个值，取偶数位
                    data_pre = (all_angle[0::2]).reshape(s0, 1)

                    # 过滤无效值
                    invalid_index = np.logical_or(
                        data_pre < -180, data_pre > 180)
                    data_pre = data_pre.astype(np.float32)
                    data_pre[invalid_index] = np.nan

                    data = data_pre

                except Exception as e:
                    print 'Open file error {}'.format(e)
                    return
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

    def get_solar_azimuth(self):
        """
        return solar_azimuth
        """
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']
            if self.satellite in satellite_type1:

                try:
                    fp = coda.open(self.in_file)
                    angle = coda.fetch(
                        fp, 'MDR', -1, 'MDR', 'GGeoSondAnglesSUN')
                    coda.close(fp)

                    all_angle = []

                    for i in xrange(len(angle)):
                        tmp_angle = angle[i].reshape(-1)
                        if len(all_angle) == 0:
                            all_angle = tmp_angle
                        else:
                            all_angle = np.concatenate(
                                (all_angle, tmp_angle))

                    s0 = self.data_shape[0]
                    # 开始间隔一个取一个值，取偶数位
                    data_pre = (all_angle[1::2]).reshape(s0, 1)

                    # 过滤无效值
                    invalid_index = np.logical_or(
                        data_pre < 0, data_pre > 360)
                    data_pre = data_pre.astype(np.float32)
                    data_pre[invalid_index] = np.nan
                    data = data_pre

                except Exception as e:
                    print 'Open file error {}'.format(e)
                    return
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

    def get_solar_zenith(self):
        """
        return solar_zenith
        """
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']
            if self.satellite in satellite_type1:

                try:
                    fp = coda.open(self.in_file)
                    angle = coda.fetch(
                        fp, 'MDR', -1, 'MDR', 'GGeoSondAnglesSUN')
                    coda.close(fp)

                    all_angle = []

                    for i in xrange(len(angle)):
                        tmp_angle = angle[i].reshape(-1)
                        if len(all_angle) == 0:
                            all_angle = tmp_angle
                        else:
                            all_angle = np.concatenate(
                                (all_angle, tmp_angle))

                    s0 = self.data_shape[0]
                    # 开始间隔一个取一个值，取偶数位
                    data_pre = (all_angle[0::2]).reshape(s0, 1)

                    # 过滤无效值
                    invalid_index = np.logical_or(
                        data_pre < -180, data_pre > 180)
                    data_pre = data_pre.astype(np.float32)
                    data_pre[invalid_index] = np.nan

                    data = data_pre

                except Exception as e:
                    print 'Open file error {}'.format(e)
                    return
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

    def get_timestamp(self):
        """
        return from 1970-01-01 00:00:00 seconds
        """
        if self.resolution == 24000:
            satellite_type1 = ['METOP-A', 'METOP-B']
            if self.satellite in satellite_type1:
                s = self.data_shape
                try:
                    #                     record = beatl2.ingest(self.in_file)
                    ary_time = self.record.time
                    # IASI 数据的时间单位是距离 2000年1月1日 UTC时间的秒
                    secs = int(
                        (datetime(2000, 1, 1, 0, 0, 0) - datetime(1970, 1, 1, 0, 0, 0)).total_seconds())

                    ary_time = ary_time + secs
                    data = ary_time.reshape(s)
                    data = data.astype(np.int32)

                except Exception as e:
                    print 'Open file error {}'.format(e)
                    return
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

if __name__ == '__main__':
    T1 = datetime.now()
    BandLst = ['CH_20', 'CH_21', 'CH_22', 'CH_23', 'CH_24', 'CH_25']
    L1File = '/nas02/METOP-B/IASI/L1/ORBIT/2018/20181201/IASI_xxx_1C_M01_20181201012359Z_20181201012655Z_N_O_20181201020428Z__20181201020817'
    iasi1 = ReadIasiL1(L1File)
#     L1File = 'D:/data/METOP/IASI_xxx_1C_M02_20180502061153Z_20180502061456Z_N_O_20180502072518Z__20180502072850'
#     iasi2 = ReadIasiL1(L1File)
    with time_block('>>>>>>>>>>>>read iasi', True):
        print iasi1.satellite  # 卫星名
        print iasi1.sensor  # 传感器名
        print iasi1.ymd  # L1 文件年月日 YYYYMMDD
        print iasi1.hms  # L1 文件时分秒 HHMMSS
        print iasi1.resolution  # 分辨率
        print iasi1.channels  # 通道数量
        print iasi1.data_shape
        print iasi1.file_attr

        def print_data_status(datas, name=None):
            data_shape = datas.shape
            data_min = np.nanmin(datas)
            data_max = np.nanmax(datas)
            data_mean = np.nanmean(datas)
            data_median = np.nanmedian(datas)
            print "{}: shape: {}, min: {}, max: {}, mean: {}, median: {}".format(
                name, data_shape, data_min, data_max, data_mean, data_median)

        print 'get_spectral_response:'
        wavenums, response = iasi1.get_spectral_response()

        print wavenums[0], wavenums[-1]

        import matplotlib
        matplotlib.use('agg')
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(6, 4))
        ax1 = plt.subplot2grid((1, 1), (0, 0))
        ax1.plot(wavenums, response[0,0,:])
        fig.savefig('test.png')

        print '222', response.shape
        print_data_status(wavenums)
        print_data_status(response)

#         print 'longitude:'
#         t_data = iasi1.get_longitude()
#         print_data_status(t_data)
#
#         print 'longitude:'
#         t_data = iasi1.get_latitude()
#         print_data_status(t_data)
#
#         print 'sensor_azimuth:'
#         t_data = iasi1.get_sensor_azimuth()
#         print_data_status(t_data)
#         print 'sensor_zenith:'
#         t_data = iasi1.get_sensor_zenith()
#         print_data_status(t_data)
#         print 'solar_azimuth:'
#         t_data = iasi1.get_solar_azimuth()
#         print_data_status(t_data)
#         print 'solar_zenith:'
#         t_data = iasi1.get_solar_zenith()
#         print_data_status(t_data)
#
#         print 'sv:'
#         t_data = iasi1.get_dn()
#
#         print 'timestamp:'
#         t_data = iasi1.get_timestamp()
#         print type(t_data)
#         print type(t_data[0, 0])
#         print time.gmtime(t_data[0, 0])
#         print time.gmtime(t_data[-1, -1])
#         print_data_status(t_data)
