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
PROJ_LUT_4KM = os.path.join(aid_path, 'lonlat_projlut_4km.hdf')
BASEMAP_4KM = os.path.join(aid_path, 'ditu_4km.png')
FY4_LON_LAT_LUT = os.path.join(aid_path, 'FY4X_LON_LAT_LUT.H5')
EP_TXT = os.path.join(aid_path, 'ep.txt')
ER_TXT = os.path.join(aid_path, 'er.txt')

# 数据库
DATABASE_URL = 'mysql+pymysql://hzqx:PassWord@1234@183.230.93.188:3306/solar'
