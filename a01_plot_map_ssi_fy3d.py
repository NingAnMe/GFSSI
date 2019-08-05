#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/26
@Author  : AnNing
"""
from __future__ import print_function
from datetime import datetime
from dateutil.relativedelta import relativedelta

import os
import sys
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import gdal
import numpy as np

from load import TanSatCO2

from DV import dv_map


class ReadFY3DNEVISSI:
    def __init__(self, in_file):
        self.in_file = in_file

        dataset = gdal.Open(self.in_file)
        self.XSize = dataset.RasterXSize
        self.YSize = dataset.RasterYSize
        self.GeoTransform = dataset.GetGeoTransform()
        self.ProjectionInfo = dataset.GetProjection()

    def get_ssi(self):
        dataset = gdal.Open(self.in_file)
        band = dataset.GetRasterBand(1)
        data = band.ReadAsArray(0, 0, self.XSize, self.YSize).astype(np.float32)
        return data

    def get_lon_lat(self):
        gtf = self.GeoTransform
        x_range = range(0, self.XSize)
        y_range = range(0, self.YSize)
        x, y = np.meshgrid(x_range, y_range)
        lon = gtf[0] + x * gtf[1] + y * gtf[2]
        lat = gtf[3] + x * gtf[4] + y * gtf[5]
        return lon, lat


def main():
    in_dir = '/home/gfssi/GFData/tem'
    out_dir = '/home/gfssi/GFData/fy3d_ssi_pic'
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    file_names = os.listdir(in_dir)
    file_names.sort()
    for file_name in file_names:
        if 'dat' not in file_name:
            continue
        name, ext = os.path.splitext(file_name)
        ssi_type, date = name.split('_')
        ssi_type_dict = {
            'Bc': ('Ib', 0, 1500),
            'Gc': ('Itol', 0, 3000),
            'Dc': ('Id', 0, 500)
        }
        ssi_type, vmin, vmax = ssi_type_dict[ssi_type]
        in_file = os.path.join(in_dir, file_name)
        print(in_file)
        data_loader = ReadFY3DNEVISSI(in_file)
        ssi = data_loader.get_ssi()

        lons, lats = data_loader.get_lon_lat()
        ssi = ssi[::3, ::3]
        lons = lons[::3, ::3]
        lats = lats[::3, ::3]
        print(ssi.min(), ssi.max())
        print(lons.min(), lons.max())
        print(lats.min(), lats.max())
        out_file = os.path.join(out_dir, file_name + '.jpg')
        plot_map_project(lats, lons, ssi, out_file, title='{} {}'.format(ssi_type, date),
                         vmin=vmin, vmax=vmax)


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
        markersize=3):

    print(value.min(), value.max())
    p = dv_map.dv_map()
    p.colorbar_fmt = '%d'
    box = [54., 18., 73., 135.]  # 经纬度范围 NSWE
    p.easyplot(latitude, longitude, value, vmin=vmin, vmax=vmax,
               ptype=ptype, markersize=markersize, marker=marker, box=box)
    p.title = title
    p.colorbar_unit = 'w/m2'
    p.savefig(out_file)
    print('>>> {}'.format(out_file))


if __name__ == '__main__':
    main()
