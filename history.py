#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/1
@Author  : AnNing
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
import os
import sys
from multiprocessing import Pool

from gfssi_p02_ssi_plot_map_full import plot_map_full
from gfssi_p01_ssi_plot_map_area import plot_map_area
from gfssi_e02_ssi_combine import combine_full
from gfssi_e03_ssi_area import area

# 获取程序所在目录位置
g_path, _ = os.path.split(os.path.realpath(__file__))
# 进入该目录
os.chdir(g_path)

data_root_dir = '/home/gfssi/GFData/'


def get_files_by_date(dir_path, time_start, time_end, ext=None, pattern=None):
    """
    :param dir_path: 文件夹
    :param time_start: 开始时间
    :param time_end: 结束时间
    :param ext: 后缀名, '.hdf5'
    :param pattern: 匹配时间的模式
    :return: list
    """
    files_found = []
    if pattern is not None:
        pattern = pattern
    else:
        pattern = r".*(\d{8})"

    for root, dirs, files in os.walk(dir_path):
        for file_name in files:
            if ext is not None:
                if '.' not in ext:
                    ext = '.' + ext
                if os.path.splitext(file_name)[1].lower() != ext.lower():
                    continue
            re_result = re.match(pattern, file_name)
            if re_result is not None:
                time_file = ''.join(re_result.groups())
            else:
                continue
            if int(time_start) <= int(time_file) <= int(time_end):
                files_found.append(os.path.join(root, file_name))
    files_found.sort()
    return files_found


def product_4km_disk_full_image_orbit(date_start=None, date_end=None, thread=3):
    """
    绘制原始4KM数据的图像
    3个产品，每个产品2张图像，共6张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :param thread:
    :return:
    """
    in_dir = os.path.join(data_root_dir, 'SSIData/FY4A/SSI_4KM/Full/Orbit')
    date_end_str = date_end.strftime('%Y%m%d%H%M%S')
    pattern = r'.*FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_(\d{14})_\d{14}_4000M_V0001.NC'
    in_files = []
    while date_start <= date_end:
        ymd = date_start.strftime('%Y%m%d')
        in_dir_tem = os.path.join(in_dir, ymd)
        date_start_str = date_start.strftime('%Y%m%d%H%M%S')
        in_files_tem = get_files_by_date(in_dir_tem, date_start_str, date_end_str, ext='.NC', pattern=pattern)
        in_files.extend(in_files_tem)
        date_start += relativedelta(days=1)
    in_files_length = len(in_files)
    print('找到的文件总数:{}'.format(in_files_length))

    print('开始绘图')
    p = Pool(thread)
    for in_file in in_files[:]:
        p.apply_async(plot_map_full, args=(in_file, '4km'))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def product_4km_disk_full_data_and_image(date_start=None, date_end=None, frequency='Daily'):
    """
    4KM数据日合成
    绘制原始4KM数据的图像
    3个产品，每个产品2张图像，共6张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :param frequency:
    :return:
    """
    in_dir = os.path.join(data_root_dir, 'SSIData/FY4A/SSI_4KM/Full/{}')
    out_dir = os.path.join(data_root_dir, 'SSIData/FY4A/SSI_4KM/Full/{}')
    out_name = 'FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_{name}_4000M_V0001.NC'

    if frequency == 'Daily':
        in_dir = in_dir.format('Orbit')
        out_dir = out_dir.format('Daily')
        strf_name = '%Y%m%d'
        strf_dir = '%Y%m'
        date_relativedelta = relativedelta(days=1)
        daily = True
        vmin = 0
        vmax = 20
    elif frequency == 'Monthly':
        in_dir = in_dir.format('Daily')
        out_dir = out_dir.format('Monthly')
        strf_name = '%Y%m'
        strf_dir = '%Y'
        date_relativedelta = relativedelta(months=1)
        daily = False
        vmin = 0
        vmax = 600
    elif frequency == 'Yearly':
        in_dir = in_dir.format('Monthly')
        out_dir = out_dir.format('Yearly')
        strf_name = '%Y'
        strf_dir = None
        date_relativedelta = None
        daily = False
        vmin = 0
        vmax = 7000
    else:
        raise ValueError('不支持的类型：{}'.format(frequency))

    in_files_all = []
    date_start_tem = date_start
    while date_start_tem <= date_end:
        if strf_dir is not None:
            date_dir = date_start_tem.strftime(strf_dir)
        else:
            date_dir = ''
        date_name = date_start_tem.strftime(strf_name)
        in_dir_tem = os.path.join(in_dir, date_name)
        filenames = os.listdir(in_dir_tem)
        in_files_tem = [os.path.join(in_dir_tem, i) for i in filenames if os.path.splitext(i)[1].lower() == '.nc']
        out_file = os.path.join(out_dir, date_dir, out_name.format(name=date_name))
        in_files_all.append((in_files_tem, out_file))
        if date_relativedelta is not None:
            date_start_tem += date_relativedelta
        else:
            break

    print('开始合成')
    p = Pool(4)
    for in_files, out_file in in_files_all:
        in_files_length = len(in_files)
        print('找到的文件总数:{}'.format(in_files_length))
        p.apply_async(combine_full, args=(in_files, out_file, daily))
    p.close()
    p.join()

    print('开始绘图')
    p = Pool(4)
    for in_files, out_file in in_files_all[:]:
        p.apply_async(plot_map_full, args=(out_file, '4km', vmin, vmax))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def product_4km_disk_china_data_and_image(date_start=None, date_end=None, thread=3, frequency='Orbit'):
    """
    生成原始数据的中国区时次数据
    3个产品，每个产品1张图像，共3张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :param thread:
    :param frequency:
    :return:
    """
    left_up_lon = 70
    left_up_lat = 50
    right_down_lon = 140
    right_down_lat = 0

    in_dir = os.path.join(data_root_dir, 'SSIData/FY4A/SSI_4KM/Full/{}'.format(frequency))
    out_dir = os.path.join(data_root_dir, 'SSIData/FY4A/SSI_4KM/China/{}'.format(frequency))

    if frequency == 'Orbit':
        pattern = r'.*FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_(\d{14})_\d{14}_4000M_V0001'
        strf_name = '%Y%m%d%H%M%S'
        date_end_str = date_end.strftime(strf_name)
        strf_dir = '%Y%m%d'
        date_relativedelta = relativedelta(days=1)
    elif frequency == 'Daily':
        pattern = r'.*FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_(\d{8})_4000M_V0001'
        strf_name = '%Y%m%d'
        date_end_str = date_end.strftime(strf_name)
        strf_dir = '%Y%m'
        date_relativedelta = relativedelta(months=1)
    elif frequency == 'Monthly':
        pattern = r'.*FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_(\d{6})_4000M_V0001'
        strf_name = '%Y%m'
        date_end_str = date_end.strftime(strf_name)
        strf_dir = '%Y'
        date_relativedelta = relativedelta(years=1)
    elif frequency == 'Yearly':
        pattern = r'.*FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_(\d{4})_4000M_V0001'
        strf_name = '%Y'
        date_end_str = date_end.strftime(strf_name)
        strf_dir = None
        date_relativedelta = None
    else:
        raise ValueError('不支持的类型：{}'.format(frequency))

    in_files = []
    date_start_tem = date_start
    while date_start_tem <= date_end:
        if strf_dir is not None:
            date_dir = date_start_tem.strftime(strf_dir)
        else:
            date_dir = ''
        in_dir_tem = os.path.join(in_dir, date_dir)
        date_start_str = date_start_tem.strftime(strf_name)
        in_files_tem = get_files_by_date(in_dir_tem, date_start_str, date_end_str, ext='.NC', pattern=pattern)
        in_files.extend(in_files_tem)
        if date_relativedelta is not None:
            date_start_tem += date_relativedelta
        else:
            break
    in_files_length = len(in_files)
    print('找到的文件总数:{}'.format(in_files_length))

    print('开始生成中国区数据')
    p = Pool(thread)
    for in_file in in_files[:]:
        out_file = in_file.replace(in_dir, out_dir)
        p.apply_async(area, args=(in_file, out_file, '4km', left_up_lon, left_up_lat, right_down_lon, right_down_lat))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))

    in_files = []
    date_start_tem = date_start
    while date_start_tem <= date_end:
        if strf_dir is not None:
            date_dir = date_start_tem.strftime(strf_dir)
        else:
            date_dir = ''
        in_dir_tem = os.path.join(in_dir, date_dir)
        date_start_str = date_start_tem.strftime(strf_name)
        in_files_tem = get_files_by_date(in_dir_tem, date_start_str, date_end_str, ext='.png', pattern=pattern)
        in_files.extend(in_files_tem)
        if date_relativedelta is not None:
            date_start_tem += date_relativedelta
        else:
            break
    in_files_length = len(in_files)
    print('找到的文件总数:{}'.format(in_files_length))

    print('开始中国区的绘图')
    p = Pool(thread)
    for in_file in in_files[:]:
        out_file = in_file.replace(in_dir, out_dir)
        p.apply_async(plot_map_area, args=(in_file, out_file, '4km', left_up_lon, left_up_lat, right_down_lon,
                                           right_down_lat))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


if __name__ == '__main__':
    # 测试生产4KM时次的绘图
    start = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    end = datetime.strptime('20190630235959', '%Y%m%d%H%M%S')

    # product_4km_disk_full_image_orbit(start, end)  # 圆盘轨道
    # product_4km_disk_full_data_and_image(start, end, frequency='Daily')  # 圆盘日
    # product_4km_disk_full_data_and_image(start, end, frequency='Monthly')  # 圆盘月
    # product_4km_disk_full_data_and_image(start, end, frequency='Yearly')  # 圆盘年
    #
    # product_4km_disk_china_data_and_image(start, end, frequency='Orbit')  # 中国区轨道
    # product_4km_disk_china_data_and_image(start, end, frequency='Daily')  # 中国区日
    # product_4km_disk_china_data_and_image(start, end, frequency='Monthly')  # 中国区月
    # product_4km_disk_china_data_and_image(start, end, frequency='Yearly')  # 中国区年
    # start = datetime.strptime('20190601000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190731000000', '%Y%m%d%H%M%S')
    # job_0210(start, end)
    # start = datetime.strptime('20190601000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190731000000', '%Y%m%d%H%M%S')
    # job_0310(start, end)
    # start = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    # job_0410(start, end)
    # start = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630235959', '%Y%m%d%H%M%S')
    # job_0510(start, end)
