#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/2
@Author  : AnNing
"""
import os
from lib.lib_path import get_aid_path

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
DATABASE_URL = 'mysql+pymysql://hzqx:PassWord@1234@183.230.93.188:3306/solar'
