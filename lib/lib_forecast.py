#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/9/24 14:14
# @Author  : AnNing
import os

from datetime import datetime
from dateutil.relativedelta import relativedelta

from lib.lib_constant import INTERP_EXE, FORECAST_EXE
from config import DATA_TMP_DIR

TMP_PATH = DATA_TMP_DIR

INTERP_IN_TMP = os.path.join(TMP_PATH, 'interp_in.txt')
INTERP_OUT_TMP = os.path.join(TMP_PATH, 'interp_out.txt')
FORECAST_IN_TMP = os.path.join(TMP_PATH, 'forecast_in.txt')
FORECAST_OUT_TMP = os.path.join(TMP_PATH, 'forecast_out.txt')


def _clear_tmp():
    os.system('rm -rf {}'.format(INTERP_IN_TMP))
    os.system('rm -rf {}'.format(INTERP_OUT_TMP))
    os.system('rm -rf {}'.format(FORECAST_IN_TMP))
    os.system('rm -rf {}'.format(FORECAST_OUT_TMP))


def forecast_ssi(dates, values, lon, lat):
    print(dates)
    print(values)
    _clear_tmp()
    # try:
    print('开始生成INTERP_IN_TMP文件')
    with open(INTERP_IN_TMP, 'w') as fp:
        fp.write('%target\n')
        fp.write('%Time Itotal\n')
        for j, date in enumerate(dates):  # j 是日期的索引值
            print('日期：{}'.format(date))
            datas_tmp = values[j]
            date = datetime.strptime(date, '%Y%m%d%H%M%S') - relativedelta(hours=8)
            data_format = {'date': date.strftime('%Y%m%d%H%M')}
            for element_ in datas_tmp:
                data_ = datas_tmp[element_]
                data_format[element_] = data_
            data_str = '{date}\t{Itol:0.4f}\t{Ib:0.4f}\t{Id:0.4f}\t{G0:0.4f}\t{Gt:0.4f}\t{DNI:0.4f}\n'.format(
                **data_format)
            fp.write(data_str)
            print(data_str)
    print('开始插值，生成INTERP_OUT_TMP')
    print('cmd: {} {} {}'.format(INTERP_EXE, INTERP_IN_TMP, INTERP_OUT_TMP))
    os.system('{} {} {}'.format(INTERP_EXE, INTERP_IN_TMP, INTERP_OUT_TMP))
# except:
    print('ERROR：运行forecast插值程序错误')
    FORECAST_IN_TMP = INTERP_OUT_TMP
    try:
        print('开始运行预报程序')
        print('cmd: {} {} {} {} {}'.format(FORECAST_EXE, FORECAST_IN_TMP, FORECAST_OUT_TMP, lon, lat))
        os.system('{} {} {} {} {}'.format(FORECAST_EXE, FORECAST_IN_TMP, FORECAST_OUT_TMP, lon, lat))
    except:
        print('ERROR：运行forecast程序错误')
    date_start = datetime.strptime(dates[-1], '%Y%m%d%H%M%S')
    dates = []
    values = []
    try:
        print('开始读取预报结果')
        with open(FORECAST_OUT_TMP, 'r') as fp:
            fp.readline()
            for row in fp.readlines():
                date_start += relativedelta(minutes=15)
                if date_start.minute != 0:
                    continue
                value = float(row.strip())
                date = date_start.strftime('%Y%m%d%H%M%S')
                print(date, value)
                dates.append(date)
                values.append(value)
    except:
        print('读取forecast结果文件错误')
    return dates, values
