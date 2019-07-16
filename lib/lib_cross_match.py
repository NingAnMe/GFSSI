# -*- coding: utf-8 -*-

import numpy as np

__description__ = u'静止和极轨通用匹配程序'
__author__ = 'wangpeng'
__date__ = '2018-09-06'
__version__ = '1.0.0_beat'


class CrossMatching():
    """
    u 交叉匹配类
    """

    def __init__(self, row, col):
        self.row = row
        self.col = col

        self.MaskRough = None  # 粗掩码
        self.MaskFine = {}   # 精掩码
        self.MaskFine1 = {}  # 晴空掩码
        self.MaskFine2 = {}  # 云区掩码

    def set_mask_rough(self, mask):
        """
        u 粗掩码记录表生成，默认值和公共掩码一致，根据过滤条件更新
        """
        # 记录经过全局过滤的掩码
        if self.MaskRough is None:
            self.MaskRough = np.full((self.row, self.col), 0, 'i2')

        # 设置有效标志位1
        idx = np.where(mask == 1)
        self.MaskRough[idx] = 1

    def set_mask_fine(self, band_list):
        """
        u 精掩码记录表生成，默认值和过滤后的粗掩码一致
        """
        idx = np.where(self.MaskRough == 1)

        if not self.MaskFine:
            for band in band_list:
                if band not in self.MaskFine.keys():
                    self.MaskFine[band] = np.full(
                        (self.row, self.col), 0, 'i2')
                    self.MaskFine1[band] = np.full(
                        (self.row, self.col), 0, 'i2')
                    self.MaskFine2[band] = np.full(
                        (self.row, self.col), 0, 'i2')

                self.MaskFine[band][idx] = 1
                self.MaskFine1[band][idx] = 1
                self.MaskFine2[band][idx] = 1

    def distance_filter(self, mask, value, threshold):
        '''
        update mask
        '''

        # 距离阈值过滤后不符合条件的设置0
        idx1 = np.logical_and(True, np.isnan(value))
        mask[idx1] = 0
        idx2 = np.logical_and(mask == 1, value > threshold)
        mask[idx2] = 0

        # 剩余有效位置
        idx = np.where(mask == 1)
        print '距离过滤后剩余点: ', len(idx[0])

    def times_filter(self, mask, value, threshold):
        '''
        update mask
        '''
        idx1 = np.logical_and(True, np.isnan(value))
        mask[idx1] = 0
        idx2 = np.logical_and(mask == 1, value > threshold)
        mask[idx2] = 0

        # 剩余有效位置
        idx = np.where(mask == 1)
        print '时间过滤后剩余点: ', len(idx[0])

    def sensor_zenith_filter(self, mask, value, threshold):
        '''
        update mask
        '''
        idx1 = np.logical_and(True, np.isnan(value))
        mask[idx1] = 0
        idx2 = np.logical_and(mask == 1, value > threshold)
        mask[idx2] = 0
        # 剩余有效位置
        idx = np.where(mask == 1)
        print '卫星天顶角过滤后剩余点: ', len(idx[0])

    def solar_zenith_filter(self, mask, value, threshold):
        '''
        update self.MaskRough
        '''
        idx1 = np.logical_and(True, np.isnan(value))
        mask[idx1] = 0
        idx2 = np.logical_and(mask == 1, value > threshold)
        mask[idx2] = 0
        # 剩余有效位置
        idx = np.where(mask == 1)
        print '太阳天顶角过滤后剩余点: ', len(idx[0])

    def glint_filter(self, mask, value, threshold):
        '''
        update self.MaskRough
        '''
        idx1 = np.logical_and(True, np.isnan(value))
        mask[idx1] = 0
        idx2 = np.logical_and(mask == 1, value <= threshold)
        mask[idx2] = 0

        # 剩余有效位置
        idx = np.where(mask == 1)
        print '耀斑角过滤后剩余点: ', len(idx[0])

    def sensor_zenith_homo_filter(self, mask, value, threshold):
        '''
        update mask
        '''
        idx1 = np.logical_and(True, np.isnan(value))
        mask[idx1] = 0
        idx2 = np.logical_and(mask == 1, value > threshold)
        mask[idx2] = 0
        # 剩余有效位置
        idx = np.where(mask == 1)
        print '卫星天顶均匀性过滤后剩余点: ', len(idx[0])

    def clear_cloud_filter(self, mask1, mask2, value, value_th, flag):
        """
        u 根据 tbb进行云检测tbb >= tbb_th 是晴空。
        u 根据 ref进行云检测ref < ref_th 是晴空。
        mask1 存放晴空
        mask2 存放云
        """
        if 'Ref' in flag:
            idx1 = np.logical_and(True, np.isnan(value))
            mask1[idx1] = 0
            idx2 = np.logical_and(mask1 == 1, value <= value_th)
        elif ('Tbb' in flag) or ('Rad' in flag):
            idx1 = np.logical_and(True, np.isnan(value))
            mask1[idx1] = 0
            idx2 = np.logical_and(mask1 == 1, value >= value_th)
        mask1[~idx2] = 0
        mask2[idx2] = 0
        idx1 = np.where(mask1 == 1)
        print '晴空点数 : ', len(idx1[0])
        idx1 = np.where(mask2 == 1)
        print '云区点数: ', len(idx1[0])

    def max_value_filter(self, mask, value, value_th):
        """
        u 饱和值过滤，超过的值会过滤掉 value > value_th
        """
        idx1 = np.logical_and(True, np.isnan(value))
        mask[idx1] = 0
        idx2 = np.logical_and(mask == 1, value > value_th)
        mask[idx2] = 0
        idx = np.where(mask == 1)
        print '饱和值过滤后: ', len(idx[0])

    def fov_homo_filter(self, mask, value, value_th):
        idx1 = np.logical_and(True, np.isnan(value))
        mask[idx1] = 0
        idx2 = np.logical_and(mask == 1, value > value_th)
        mask[idx2] = 0
        idx = np.where(mask == 1)
        print '靶区均匀性过滤后: ', len(idx[0])

    def env_homo_filter(self, mask, value, value_th):
        idx1 = np.logical_and(True, np.isnan(value))
        mask[idx1] = 0
        idx2 = np.logical_and(mask == 1, value > value_th)
        mask[idx2] = 0
        idx = np.where(mask == 1)
        print '环境均匀性过滤后: ', len(idx[0])

    def fov_env_homo_filter(self, mask, value, value_th):
        idx1 = np.logical_and(True, np.isnan(value))
        mask[idx1] = 0
        idx2 = np.logical_and(mask == 1, value > value_th)
        mask[idx2] = 0
        idx = np.where(mask == 1)
        print '靶区和环境均匀性过滤后: ', len(idx[0])

    def mask_fine_all_filter(self, m1, mask, mode, band, clm_flag, var_flag):
        # 取值

        s1_fov_mean = eval('m1.S1_Fov%sMean' % var_flag)
        s1_fov_std = eval('m1.S1_Fov%sStd' % var_flag)
        s1_env_mean = eval('m1.S1_Env%sMean' % var_flag)
        s1_env_std = eval('m1.S1_Env%sStd' % var_flag)

        s2_fov_mean = eval('m1.S2_Fov%sMean' % var_flag)
        s2_fov_std = eval('m1.S2_Fov%sStd' % var_flag)
        s2_env_mean = eval('m1.S2_Env%sMean' % var_flag)
        s2_env_std = eval('m1.S2_Env%sStd' % var_flag)

        # 饱和值
        value_max1 = s1_fov_mean[band]
        value_max2 = s2_fov_mean[band]

        # 角度均匀性
        sz1 = np.cos(m1.S1_SatZ * np.pi / 180.)
        sz2 = np.cos(m1.S2_SatZ * np.pi / 180.)
        angle_max = np.abs(sz1 / sz2 - 1.)

        # 靶区均匀性
        fov_value1 = s1_fov_std[band] / s1_fov_mean[band]
        fov_value2 = s2_fov_std[band] / s2_fov_mean[band]

        # 环境均匀性
        env_value1 = s1_env_std[band] / s1_env_mean[band]
        env_value2 = s2_env_std[band] / s2_env_mean[band]

        # 靶区 和 环境均匀性
        fov_env_value1 = s1_fov_mean[band] / s1_env_mean[band] - 1
        fov_env_value2 = s2_fov_mean[band] / s2_env_mean[band] - 1

        # 阈值
        value_max_th = mode.bands[band]['value_max']
        if 'clear' in clm_flag:
            angledif_max_th = mode.bands[band]['angledif_max']
            fov_max_th = mode.bands[band]['homodif_fov_max']
            env_max_th = mode.bands[band]['homodif_env_max']
            fov_env_max_th = mode.bands[band]['homodif_fov_env_max']
        elif 'cloud' in clm_flag:
            angledif_max_th = mode.bands[band]['cld_angledif_max']
            fov_max_th = mode.bands[band]['cld_homodif_fov_max']
            env_max_th = mode.bands[band]['cld_homodif_env_max']
            fov_env_max_th = mode.bands[band]['cld_homodif_fov_env_max']

        # 开始过滤
        self.max_value_filter(mask, value_max1, value_max_th)
        self.max_value_filter(mask, value_max2, value_max_th)
        self.sensor_zenith_homo_filter(mask, angle_max, angledif_max_th)
        self.fov_homo_filter(mask, fov_value1, fov_max_th)
        self.fov_homo_filter(mask, fov_value2, fov_max_th)
        self.env_homo_filter(mask, env_value1, env_max_th)
        self.env_homo_filter(mask, env_value2, env_max_th)
        self.fov_env_homo_filter(mask, fov_env_value1, fov_env_max_th)
        self.fov_env_homo_filter(mask, fov_env_value2, fov_env_max_th)
