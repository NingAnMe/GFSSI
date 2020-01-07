#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/12/19 9:27
# @Author  : NingAnMe <ninganme@qq.com>
import argparse
from dateutil.relativedelta import relativedelta
import time
from datetime import datetime
import os

import requests


from lib.lib_cimiss import get_cimiss_ssi_ssh_tem_data
from config import DATA_OBS_DIR


def download_cimiss(ymd):
    print(f"({datetime.now()})开始下载CIMISS数据: {ymd}")
    out_dir = os.path.join(DATA_OBS_DIR, ymd)
    if not os.path.isdir(out_dir):
        print(f"创建文件夹： {out_dir}")
        os.makedirs(out_dir)
    elif len(os.listdir(out_dir)) >= 2000:
        print(f"文件数量超过2000个，不再重新下载: {out_dir}")
        return True
    else:
        print(f"文件数量少于2000个，删除原文件后重新下载:  {out_dir}")
        os.system("rm -rf {}".format(os.path.join(DATA_OBS_DIR, ymd)))
    success = False
    try_download = 0
    while not success:
        try_download += 1
        print(f"尝试第 {try_download} 次下载")
        try:
            success = get_cimiss_ssi_ssh_tem_data(ymd, out_dir, copy_file=False)
        except requests.exceptions.ReadTimeout as why:
            print(why)
            pass
        if try_download >= 3:
            os.system("rm -rf {}".format(os.path.join(DATA_OBS_DIR, ymd)))
            print(f"({datetime.now()})尝试下载CIMISS失败: {ymd}")
            break
    if success:
        print(f"({datetime.now()})成功下载CIMISS: {out_dir}")
    return success


def download_today():
    print(f"({datetime.now()})启动CIMISS实时下载")
    while True:
        date_now = datetime.now()
        ymd_now = date_now.strftime("%Y%m%d")
        if date_now.minute % 15 == 5:
            try:
                os.system("rm -rf {}".format(os.path.join(DATA_OBS_DIR, ymd_now)))
                success = download_cimiss(ymd_now)
                if success:
                    time.sleep(60)
            except Exception as why:
                print(why)
        else:
            time.sleep(60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download CIMISS')
    parser.add_argument('--datetime_start', '-s', help='开始时间，YYYYmmddHHMMSS(20190101000000)')
    parser.add_argument('--datetime_end', '-e', help='结束时间，YYYYmmddHHMMSS(20190101235959)')
    args = parser.parse_args()

    if args.datetime_start is not None and args.datetime_end is not None:
        datetime_start = datetime.strptime(args.datetime_start, "%Y%m%d%H%M%S")
        datetime_end = datetime.strptime(args.datetime_end, "%Y%m%d%H%M%S")
        datetime_now = datetime_start
        while datetime_now <= datetime_end:
            download_cimiss(datetime_now.strftime("%Y%m%d"))
            datetime_now += relativedelta(days=1)
    else:
        download_today()
