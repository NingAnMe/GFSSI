#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/2
@Author  : AnNing
"""
import os
from lib.lib_path import get_aid_path, GFSSI_DIR

aid_path = get_aid_path()

# 无效数据的填充值
FULL_VALUE = -999

# 辅助文件
BASEMAP_FY4_4KM = os.path.join(aid_path, 'ditu_fy4a_4km.png')
LON_LAT_LUT_FY4_4KM = os.path.join(aid_path, 'lonlat_lut_fy4_4km.hdf')  # FY4原始数据的经纬度查找表
LON_LAT_LUT_FY4_1KM = os.path.join(aid_path, 'lonlat_lut_fy4_1km.hdf')  # FY4原始数据的经纬度查找表
LON_LAT_LUT_FY3_1KM = os.path.join(aid_path, 'lonlat_lut_fy3_1km.hdf')  # FY3原始数据的经纬度查找表
PROJ_LUT_FY4_4KM = os.path.join(aid_path, 'lonlat_projlut_fy4_4km.hdf')  # FY4投影的经纬度查找表
PROJ_LUT_FY4_1KM = os.path.join(aid_path, 'lonlat_projlut_fy4_1km.hdf')  # FY4投影的经纬度查找表
KDTREE_LUT_FY4_4KM = os.path.join(aid_path, 'kdtree_lut_fy4_4km.hdf')  # FY4原始数据经纬度KDtree查找表
KDTREE_LUT_FY4_1KM = os.path.join(aid_path, 'kdtree_lut_fy4_1km.hdf')  # FY4原始数据经纬度KDtree查找表
KDTREE_LUT_FY3_1KM = os.path.join(aid_path, 'kdtree_lut_fy3_1km.hdf')  # FY3原始数据经纬度KDtree查找表
D_DEM_1KM = os.path.join(aid_path, 'D_DEM.txt')  # 1km校正文件
EP_TXT = os.path.join(aid_path, 'ep.txt')
ER_TXT = os.path.join(aid_path, 'er.txt')

# 数据库
DATABASE_URL = 'mysql+pymysql://root:root@cma07@127.0.0.1:3306/solar'

# 图例范围
COLORBAR_RANGE_ORBIT_FY4A = (0, 1000)
COLORBAR_RANGE_DAILY_FY4A = (0, 20)
COLORBAR_RANGE_MONTHLY_FY4A = (0, 600)
COLORBAR_RANGE_YEARLY_FY4A = (0, 4000)
COLORBAR_RANGE_DAILY_FY3D = (0, 1)
COLORBAR_RANGE_MONTHLY_FY3D = (0, 30)
COLORBAR_RANGE_YEARLY_FY3D = (0, 360)

# FY4A 1KM Correct程序的经纬度范围，需要和1KM对应
FY4A_1KM_CORRECT_LAT_LON_RANGE = [9.995, 55.01, 69.995, 140.01, 0.01]

# 预报程序
INTERP_EXE = os.path.join(GFSSI_DIR, 'step5', 'interp')
FORECAST_EXE = os.path.join(GFSSI_DIR, 'step5', 'forecast')
