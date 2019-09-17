#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/16
@Author  : AnNing
"""
from __future__ import print_function


import os
import matplotlib
matplotlib.use('agg')
import numpy as np

from DV import dv_map

from lib.lib_read_ssi import FY4ASSI


def main():
    in_dir = '/home/gsics/anning/GFSSI'
    in_filename = 'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_2018_4000M_V0001.NC'
    in_file = os.path.join(in_dir, in_filename)

    out_dir = '/home/gsics/anning/GFSSI/FY4A_2018'
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    data_loader = FY4ASSI(in_file)
    datas = {
        'Bc': data_loader.get_ib(),
        'Gc': data_loader.get_itol(),
        'Dc': data_loader.get_id(),
    }

    lats = data_loader.get_latitude_4km()
    lons = data_loader.get_longitude_4km()


    for ssi_type in datas:
        date = '2018'
        ssi_type_dict = {
            'Bc': ('Ib', 0, 4000, 'KWh/m2'),
            'Gc': ('Itol', 0, 4000, 'KWh/m2'),
            'Dc': ('Id', 0, 4000, 'KWh/m2'),
            # 'Sz': ('Sz', 0, 90, '')
        }
        title, vmin, vmax, unit = ssi_type_dict[ssi_type]

        ssi = datas[ssi_type]
        # ssi = ssi[::3, ::3]
        # lons = lons[::3, ::3]
        # lats = lats[::3, ::3]

        out_file = os.path.join(out_dir, '{}_{}_FY4A.jpg'.format(ssi_type, date))
        plot_map_project(lats, lons, ssi, out_file, title='{} {}'.format(title, date),
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

    print(np.nanmin(value), np.nanmax(value))
    p = dv_map.dv_map()
    p.colorbar_fmt = '%d'
    p.delat = 10
    p.delon = 10
    p.show_china_boundary = True
    p.show_china_province = True

    box = [54., 18., 73., 135.]  # 经纬度范围 NSWE
    # box = [34., 31., 90., 93.]  # 经纬度范围 NSWE
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
