#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/10/12 11:27
# @Author  : AnNing
import argparse
from warnings import filterwarnings

from schedule import *


filterwarnings("ignore")

resolution_types = {
    '1KM',
    '1KMCorrect',
    '4KM',
    '4KMCorrect',
}
functions = {
    'fy4a_save_4km_orbit_data_in_database',
    'product_fy3d_1km_daily_data',
    'product_fy4a_4kmcorrect_disk_full_data_orbit',
    'product_fy4a_1km_disk_full_data_orbit',
    'product_fy4a_1kmcorrect_disk_full_data_orbit',
    'product_fy4a_disk_full_image_orbit',
    'product_combine_data',
    'product_image',
}

sat_sensors = {
    'FY4A_AGRI',
    'FY3D_MERSI',
}

frequencys = {
    'Orbit',
    'Daily',
    'Monthly'
    'Yearly',
}

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='GFSSI Schedule')
    parser.add_argument('--function', '-f', help='程序名', required=True)
    parser.add_argument('--datetime_start', '-d', help='开始时间，YYYYmmddHHMMSS(20190101000000)', required=True)
    parser.add_argument('--datetime_end', '-a', help='结束时间，YYYYmmddHHMMSS(20190101235959)', required=True)
    parser.add_argument('--sat_sensor', '-s', help='卫星传感器，FY4A_AGRI', required=True)
    parser.add_argument('--resolution_type', '-r', help='空间分辨率，4KM', required=True)
    parser.add_argument('--frequency', '-e', help='时间分辨率，Orbit', required=True)
    parser.add_argument('--thread', '-t', help='线程数，thread', required=False)
    args = parser.parse_args()

    assert args.function.lower() in functions, '{}'.format(functions)
    assert args.resolution_type in resolution_types, '{}'.format(resolution_types)
    assert args.sat_sensor in sat_sensors, '{}'.format(sat_sensors)

    if args.thread is None:
        thread = 1
    else:
        thread = int(args.thread)

    datetime_start = datetime.strptime(args.datetime_start, '%Y%m%d%H%M%S')
    datetime_end = datetime.strptime(args.datetime_end, '%Y%m%d%H%M%S')

    eval(args.function)(date_start=datetime_start, date_end=datetime_end, resolution_type=args.resolution_type,
                        frequency=args.frequency, sat_sensor=args.sat_sensor, thread=thread)
