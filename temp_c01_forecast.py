#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/9/26 15:15
# @Author  : AnNing

from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import sys

from lib.lib_forecast import forecast_ssi
from schedule import product_point_data
from restful import kdtree_idx_fy4_4km, kdtree_ck_fy4_4km

idx = kdtree_idx_fy4_4km
ck = kdtree_ck_fy4_4km


def forecast(date_start, date_end, hour_start, lon, lat, out_dir):
    hour_start = int(hour_start)
    lon = float(lon)
    lat = float(lat)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    date_now = date_start
    while date_now <= date_end:
        date_utc = date_now + relativedelta(hours=hour_start - 8)  # 变为世界时间
        date_s = (date_utc - relativedelta(hours=1)).strftime('%Y%m%d%H%M%S')
        date_e = date_utc.strftime('%Y%m%d%H%M%S')
        element = 'Itol'
        resultid = 'FY4A_AGRI_L2_SSI_Orbit'
        resolution_type = '4KMCorrect'
        sat_sensor = 'FY4A_AGRI'
        result = product_point_data(date_start=date_s, date_end=date_e, lon=lon, lat=lat,
                                    resolution_type=resolution_type, resultid=resultid,
                                    element=element,
                                    idx=idx, ck=ck,
                                    sat_sensor=sat_sensor)
        if result is not None:
            values = result.pop('values')
            forecast_dates, forecast_values = forecast_ssi(result['date'], values, lon, lat)

            out_file = os.path.join(out_dir, '{lon:0.4f}_{lat:0.4f}_{date}_{hour}.txt'.format(
                lon=lon, lat=lat, date=date_now.strftime('%Y%m%d'), hour=hour_start))

            with open(out_file, 'w') as fp:
                for date, value in zip(forecast_dates, forecast_values):
                    fp.write('{}\t{}\n'.format(date, value))
                print('OUTPUT >>> {}'.format(out_file))
        date_now += relativedelta(days=1)


if __name__ == '__main__':
    argv = sys.argv
    # if argv <= 1:
    #     print('datetime_start datetime_end hour lon lat out_dir      hour是北京时间')
    date_init = argv[1]
    date_finally = argv[2]
    hour = argv[3]
    # lon = argv[4]
    # lat = argv[5]
    # out_dir = argv[6]
    # date_init = '20190110'
    # date_finally = '20190120'
    # hour = 10
    lon = 120.165
    lat = 32.226
    out_dir = os.path.join('/home/gfssi/GFData/TmpData', '{}_{}_{}'.format(lon, lat, hour))
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    date_start = datetime.strptime(date_init[:8], '%Y%m%d')
    date_end = datetime.strptime(date_finally[:8], '%Y%m%d')
    forecast(date_start, date_end, hour, lon, lat, out_dir)

    outname = 'FY4A-_AGRI--_{lon:07.3f}N_DISK_{lat:07.3f}E_L2-_SSI-_MULT_NOM_' \
              '{date_start}_{date_end}_{resolution_type}_V0001_forecast.csv'.format(
        lon=lon, lat=lat, date_start=date_init, date_end=date_finally, resolution_type='4KMCorrect', site='')
    out_file = os.path.join(out_dir, outname)
    forecast_files = os.listdir(out_dir)
    forecast_files.sort()
    with open(out_file, 'w') as fp_out:
        for in_file in forecast_files:
            with open(os.path.join(out_dir, in_file), 'r') as fp:
                for row in fp.readlines():
                    date, value = row.split()
                    fp_out.write('{},{}\n'.format(date, value))
    print('OUTPUT >>> {}'.format(out_file))
