#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/2
@Author  : AnNing
"""
import os
from lib.lib_path import get_aid_path

aid_path = get_aid_path()

FULL_VALUE = -999

PROJ_LUT_4KM = os.path.join(aid_path, 'lonlat_projlut_4km.hdf')
BASEMAP_4KM = os.path.join(aid_path, 'ditu_4km.png')
FY4_LON_LAT_LUT = os.path.join(aid_path, 'FY4X_LON_LAT_LUT.H5')
EP_TXT = os.path.join(aid_path, 'ep.txt')
ER_TXT = os.path.join(aid_path, 'er.txt')
