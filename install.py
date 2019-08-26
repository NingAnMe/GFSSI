#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/15
@Author  : AnNing
"""
import os

from aid_lonlat_projlut import make_disk_projlut
from aid_basemap import make_basemap_fy4a
from lib.lib_constant import PROJ_LUT_4KM, BASEMAP_4KM, KDTREE_LUT_4KM
from lib.lib_read_ssi import FY4ASSI
from lib.lib_get_index_by_lonlat import make_point_index_lut


if not os.path.isfile(PROJ_LUT_4KM):
    make_disk_projlut(res='4km', out_file=PROJ_LUT_4KM)

if not os.path.isfile(BASEMAP_4KM):
    make_basemap_fy4a(res='4km', out_file=BASEMAP_4KM)

if not os.path.isfile(KDTREE_LUT_4KM):
    res_int = 4000
    lats = FY4ASSI.get_latitude()
    lons = FY4ASSI.get_longitude()
    make_point_index_lut(lons, lats, KDTREE_LUT_4KM)
