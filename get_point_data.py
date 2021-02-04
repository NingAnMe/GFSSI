#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2020-12-11 16:54
# @Author  : NingAnMe <ninganme@qq.com>
import os
import pickle
from schedule import product_point_data
from lib.lib_constant import KDTREE_LUT_FY4_4KM, KDTREE_LUT_FY4_1KM

print('读取查找表文件： {}'.format('*' * 10))
print(':{}'.format(KDTREE_LUT_FY4_4KM))
print(':{}'.format(KDTREE_LUT_FY4_1KM))

if not os.path.isfile(KDTREE_LUT_FY4_4KM):
    raise FileExistsError('{} is not exit'.format(KDTREE_LUT_FY4_4KM))
if not os.path.isfile(KDTREE_LUT_FY4_1KM):
    raise FileExistsError('{} is not exit'.format(KDTREE_LUT_FY4_1KM))

with open(KDTREE_LUT_FY4_4KM, 'rb') as fp:
    kdtree_idx_fy4_4km, kdtree_ck_fy4_4km = pickle.load(fp)
with open(KDTREE_LUT_FY4_1KM, 'rb') as fp:
    kdtree_idx_fy4_1km, kdtree_ck_fy4_1km = pickle.load(fp)


date_s = "20190101000000"
date_e = "20190102235959"
lon = 117.3
lat = 31.78
resolution_type = '4KM'
resultid = 'FY4A_AGRI_L2_SSI_Orbit'  # 小时数据 'FY4A_AGRI_L2_SSI_Orbit'， 日数据 'FY4A_AGRI_L2_SSI_Daily'
idx = kdtree_idx_fy4_4km
ck = kdtree_ck_fy4_4km
sat_sensor = 'FY4A_AGRI'
out_file = product_point_data(date_start=date_s, date_end=date_e, lon=lon, lat=lat,
                              resolution_type=resolution_type, resultid=resultid,
                              idx=idx, ck=ck,
                              sat_sensor=sat_sensor)
print(out_file)
