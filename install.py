#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/15
@Author  : AnNing
"""
import tarfile
from aid_lonlat_projlut import make_disk_projlut_4km, make_disk_projlut_1km
from aid_basemap import make_basemap_fy4a
from aid_lonlat_lut import make_lonlat_lut_1km, make_lonlat_lut_fy3d_1km
from lib.lib_constant import *
from lib.lib_read_ssi import FY4ASSI
from lib.lib_get_index_by_lonlat import make_point_index_lut


if not os.path.isfile(PROJ_LUT_FY4_4KM):
    print('生成FY4 4KM投影经纬度文件')
    make_disk_projlut_4km(out_file=PROJ_LUT_FY4_4KM)
    print(PROJ_LUT_FY4_1KM)

if not os.path.isfile(BASEMAP_FY4_4KM):
    print('生成FY4 4KM背景图')
    make_basemap_fy4a(res='4km', out_file=BASEMAP_FY4_4KM)
    print(BASEMAP_FY4_4KM)

if not os.path.isfile(KDTREE_LUT_FY4_4KM):
    print('生成FY4 4KM查找表')
    lats = FY4ASSI.get_latitude_4km()
    lons = FY4ASSI.get_longitude_4km()
    make_point_index_lut(lons, lats, out_file=KDTREE_LUT_FY4_4KM)
    print(KDTREE_LUT_FY4_4KM)

if not os.path.isfile(LON_LAT_LUT_FY4_1KM):
    print('生成FY4 1KM经纬度文件')
    make_lonlat_lut_1km(D_DEM_1KM, out_file=LON_LAT_LUT_FY4_1KM)
    print(LON_LAT_LUT_FY4_1KM)

if not os.path.isfile(PROJ_LUT_FY4_1KM):
    print('生成FY4 1KM投影经纬度文件')
    # TODO 这里有一个问题，在Linux生成的查找表的prj_i和prj_j不正确
    make_disk_projlut_1km(out_file=PROJ_LUT_FY4_1KM)
    print(PROJ_LUT_FY4_1KM)

if not os.path.isfile(KDTREE_LUT_FY4_1KM):
    print('生成FY4 1KM查找表')
    lons = FY4ASSI.get_longitude_1km()
    lats = FY4ASSI.get_latitude_1km()
    make_point_index_lut(lons, lats, out_file=KDTREE_LUT_FY4_1KM)
    print(KDTREE_LUT_FY4_1KM)

if not os.path.isfile(D_DEM_1KM):
    print('解压D_DEM.txt')
    dir_path = get_aid_path()
    with tarfile.open('Aid/ddem.tar', 'r') as tar:
        tar.extract('D_DEM.txt', dir_path)
    print(D_DEM_1KM)

if not os.path.isfile(LON_LAT_LUT_FY3_1KM):
    print('生成FY3 1KM经纬度文件')
    fy3d_envi = os.path.join(get_aid_path(), 'Sz_20190531.dat')
    make_lonlat_lut_fy3d_1km(fy3d_envi, out_file=LON_LAT_LUT_FY3_1KM)
    print(LON_LAT_LUT_FY3_1KM)
