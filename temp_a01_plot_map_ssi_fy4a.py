#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/16
@Author  : AnNing
"""
from __future__ import print_function
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lib.lib_read_ssi import FY4ASSI
from lib.lib_proj import ProjCore, meter2degree

import os
import matplotlib
matplotlib.use('agg')
import gdal
import numpy as np

from DV import dv_map


def main():
    in_dir = '/home/gfssi/GFData/tem'
    # filename_in = 'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_20190530070000_20190530071459_4000M_V0001.NC'
    filename_in = 'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_20190530061500_20190530062959_4000M_V0001.NC'
    filename_geo = 'FY4A-_AGRI--_N_DISK_1047E_L1-_GEO-_MULT_NOM_20190530070000_20190530071459_4000M_V0001.HDF'
    in_file = os.path.join(in_dir, filename_in)
    in_file_geo = os.path.join(in_dir, filename_geo)

    out_dir = '/home/gfssi/GFData/fy3d_ssi_pic2'
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    data_loader = FY4ASSI(in_file)
    datas = {
        'Bc': data_loader.get_ib(),
        'Gc': data_loader.get_itol(),
        'Dc': data_loader.get_id(),
        'Sz': data_loader.get_sz(in_file_geo)
    }

    lats = data_loader.get_latitude()
    lons = data_loader.get_longitude()

    res_degree = meter2degree(4000)
    projstr = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
    proj = ProjCore(projstr, res_degree, unit="deg", pt_tl=(90, 34), pt_br=(93, 31))  # 角点也要放在格点中心位置
    row = proj.row
    col = proj.col
    proj_lut = proj.create_lut(lats=lats, lons=lons)
    proj_i = proj_lut['prj_i']
    proj_j = proj_lut['prj_j']
    pre_i = proj_lut['pre_i']
    pre_j = proj_lut['pre_j']
    valid_index = np.logical_and.reduce((proj_i >= 0, proj_i < row,
                                         proj_j >= 0, proj_j < col))
    proj_i = proj_i[valid_index]
    proj_j = proj_j[valid_index]
    pre_i = pre_i[valid_index]
    pre_j = pre_j[valid_index]

    proj.grid_lonslats()
    lons_proj = proj.lons
    lats_proj = proj.lats

    for ssi_type in datas:
        date = '20190530'
        ssi_type_dict = {
            'Bc': ('Ib', 0, 1400, 'w/m2'),
            'Gc': ('Itol', 0, 1400, 'w/m2'),
            'Dc': ('Id', 0, 1400, 'w/m2'),
            'Sz': ('Sz', 0, 90, '')
        }
        title, vmin, vmax, unit = ssi_type_dict[ssi_type]

        ssi = datas[ssi_type]

        ssi_proj = np.full_like(lons_proj, np.nan)
        ssi_proj[proj_i, proj_j] = ssi[pre_i, pre_j]
        # ssi = ssi[::3, ::3]
        # lons = lons[::3, ::3]
        # lats = lats[::3, ::3]
        print(np.nanmin(ssi_proj), np.nanmax(ssi_proj))
        print(np.nanmin(lons_proj), np.nanmax(lons_proj))
        print(np.nanmin(lats_proj), np.nanmax(lats_proj))
        out_file = os.path.join(out_dir, '{}_{}_FY4A.jpg'.format(ssi_type, date))
        plot_map_project(lats_proj, lons_proj, ssi_proj, out_file, title='{} {}'.format(title, date),
                         vmin=vmin, vmax=vmax, unit=unit)


def plot_map_project(
        latitude,
        longitude,
        value,
        out_file,
        vmin=0,
        vmax=500,
        title='title',
        ptype='pcolor',
        marker='.',
        markersize=3,
        unit=''):

    print(value.min(), value.max())
    p = dv_map.dv_map()
    p.colorbar_fmt = '%d'
    p.delat = 1
    p.delon = 1
    # box = [54., 18., 73., 135.]  # 经纬度范围 NSWE
    box = [34., 31., 90., 93.]  # 经纬度范围 NSWE
    index = np.logical_and.reduce((latitude > box[1], latitude < box[0], longitude > box[2], longitude < box[3]))
    latitude = latitude[index]
    longitude = longitude[index]
    value = value[index]
    p.easyplot(latitude, longitude, value, vmin=vmin, vmax=vmax,
               ptype=ptype, markersize=markersize, marker=marker, box=box)

    p.title = title
    p.colorbar_unit = unit
    p.savefig(out_file)
    print('>>> {}'.format(out_file))


if __name__ == '__main__':
    main()
