#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/12/17 17:44
# @Author  : NingAnMe <ninganme@qq.com>
import argparse
from datetime import datetime
import os
from warnings import filterwarnings

from config import THREAD

filterwarnings("ignore")

gfssi_home = "/home/gfssi/Project/OM/gfssi"
thread = THREAD


frequencys = {
    'Orbit',
    'Daily',
    'Monthly'
    'Yearly',
}

cmds_orbit = [
    "python {home}/download_cimiss.py -s {d_s} -e {d_e}",
    "python {home}/run.py -f fy4a_save_4km_orbit_data_in_database -d {d_s} -a {d_e} -s FY4A_AGRI -r 4KM -e {f} -t {t}",
    "python {home}/run.py -f product_image -d {d_s} -a {d_e} -s FY4A_AGRI -r 4KM -e {f} -t {t}",
    "python {home}/run.py -f fy4a_save_4km_orbit_ref_data_in_database -d {d_s} -a {d_e} -s FY4A_AGRI -r 4KM -e {f} -t {t}",
    "python {home}/run.py -f product_cloud_image -d {d_s} -a {d_e} -s FY4A_AGRI -r 4KM -e {f} -t {t}",
    "python {home}/run.py -f product_fy4a_4kmcorrect_disk_full_data_orbit -d {d_s} -a {d_e} -s FY4A_AGRI -r 4KMCorrect -e {f} -t {t}",
    "python {home}/run.py -f product_image -d {d_s} -a {d_e} -s FY4A_AGRI -r 4KMCorrect -e {f} -t {t}",
    "python {home}/run.py -f product_fy4a_1km_disk_full_data_orbit -d {d_s} -a {d_e} -s FY4A_AGRI -r 1KM -e {f} -t {t}",
    "python {home}/run.py -f product_image -d {d_s} -a {d_e} -s FY4A_AGRI -r 1KM -e {f} -t {t}",
    "python {home}/run.py -f product_fy4a_1kmcorrect_disk_full_data_orbit -d {d_s} -a {d_e} -s FY4A_AGRI -r 1KMCorrect -e {f} -t {t}",
    "python {home}/run.py -f product_image -d {d_s} -a {d_e} -s FY4A_AGRI -r 1KMCorrect -e {f} -t {t}",
]


cmds_other = [
    "python run.py -f product_combine_data -d {d_s} -a {d_e} -s FY4A_AGRI -r 4KM -e {f} -t {t}",
    "python run.py -f product_image -d {d_s} -a {d_e} -s FY4A_AGRI -r 4KM -e {f} -t {t}",
    "python run.py -f product_combine_data -d {d_s} -a {d_e} -s FY4A_AGRI -r 4KMCorrect -e {f} -t {t}"
    "python run.py -f product_image -d {d_s} -a {d_e} -s FY4A_AGRI -r 4KMCorrect -e {f} -t {t}",
    "python run.py -f product_combine_data -d {d_s} -a {d_e} -s FY4A_AGRI -r 1KM -e {f} -t {t}",
    "python run.py -f product_image -d {d_s} -a {d_e} -s FY4A_AGRI -r 1KM -e {f} -t {t}",
    "python run.py -f product_combine_data -d {d_s} -a {d_e} -s FY4A_AGRI -r 1KMCorrect -e {f} -t {t}",
    "python run.py -f product_image -d {d_s} -a {d_e} -s FY4A_AGRI -r 1KMCorrect -e {f} -t {t}",
]


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='GFSSI Schedule')
    parser.add_argument('--datetime_start', '-s', help='开始时间，YYYYmmddHHMMSS(20190101000000)', required=True)
    parser.add_argument('--datetime_end', '-e', help='结束时间，YYYYmmddHHMMSS(20190101235959)', required=True)
    parser.add_argument('--frequency', '-f', help='时间分辨率，Orbit', required=True)
    args = parser.parse_args()

    assert args.frequency in frequencys, '{}'.format(frequencys)

    datetime_start = datetime.strptime(args.datetime_start, '%Y%m%d%H%M%S')
    datetime_end = datetime.strptime(args.datetime_end, '%Y%m%d%H%M%S')

    if args.frequency == "Orbit":
        cmds = cmds_orbit
    else:
        cmds = cmds_other

    for cmd in cmds:
        cmd = cmd.format(d_s=args.datetime_start, d_e=args.datetime_end, f=args.frequency, home=gfssi_home, t=thread)
        print(cmd)
        os.system(cmd)
