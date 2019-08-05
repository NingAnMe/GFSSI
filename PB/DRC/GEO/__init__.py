# -*- coding: utf-8 -*-
"""
@Time    : 2018/6/29 14:33
@Author  : AnNing
"""
import os


main_dir = os.path.dirname(os.path.abspath(__file__))


def get_fy4_lon_lat_lut():
    return os.path.join(main_dir, 'FY4X_LON_LAT_LUT.H5')
