#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/1
@Author  : AnNing
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import hashlib
import zipfile
import sys
from multiprocessing import Pool
import numpy as np
import threading

from gfssi_p02_ssi_plot_map_full import plot_map_full
from gfssi_p01_ssi_plot_map_area import plot_map_area
from gfssi_e02_ssi_combine import combine_full
from gfssi_e03_ssi_area import area
from gfssi_b01_ssi_itcal import itcal
from gfssi_b02_ssi_1km import fy4a_ssi_4km_to_1km
from gfssi_b04_txt2hdf import fy4a_1km_correct_txt2hdf
from gfssi_b03_envi2hdf import fy3d_envi2hdf

from config import *

from lib.lib_read_ssi import FY4ASSI, FY3DSSI
from lib.lib_database import find_result_data, Session, ResultData
from lib.lib_get_index_by_lonlat import get_point_index
from lib.lib_constant import *
from lib.lib_io import get_files_by_date

# 获取程序所在目录位置
g_path, _ = os.path.split(os.path.realpath(__file__))
# 进入该目录
os.chdir(g_path)

DEBUG = True


def get_hash_utf8(str_hash):
    """
    获取字符串的hash值
    :param str_hash:
    :return:
    """
    if not isinstance(str_hash, str):
        str_hash = str(str_hash)
    md = hashlib.md5()
    md.update(str_hash.encode('utf-8'))
    return md.hexdigest()


def make_zip_file(out_file, in_files):
    out_dir = os.path.dirname(out_file)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with zipfile.ZipFile(out_file, 'w') as z:
        for in_file in in_files:
            if os.path.isfile(in_file):
                z.write(in_file, os.path.basename(in_file))
    print('生成zip文件：{}'.format(out_file))
    return out_file


def fy4a_save_4km_orbit_data_in_database(date_start=None, date_end=None, **kwargs):
    print(date_start)
    print(date_end)
    source_dir = os.path.join(DATA_ROOT_DIR, 'SourceData', 'FY4A', 'SSI_4KM')
    ssi_dir = os.path.join(DATA_ROOT_DIR, 'SSIData', 'FY4A', 'SSI_4KM')
    ext = '.NC'
    resultid = 'FY4A_AGRI_L2_SSI_Orbit'
    planid = 1

    session = Session()
    count = 0
    for root, dirs, files in os.walk(source_dir):
        for file_name in files:
            if ext is not None:
                if '.' not in ext:
                    ext = '.' + ext
                if os.path.splitext(file_name)[1].lower() != ext.lower():
                    continue
            src_file = os.path.join(root, file_name)
            dst_file = src_file.replace(source_dir, ssi_dir)
            dst_file = dst_file.replace('4000M', '4KM')
            if not os.path.isfile(dst_file):
                dst_dir = os.path.dirname(dst_file)
                if not os.path.isdir(dst_dir):
                    os.makedirs(dst_dir)
                os.symlink(src_file, dst_file)
                try:
                    datatime = FY4ASSI.get_date_time_orbit(dst_file)
                    result_data = ResultData()
                    result_data.resultid = resultid
                    result_data.planid = planid
                    result_data.address = dst_file
                    result_data.datatime = datatime
                    result_data.createtime = datetime.now()
                    result_data.resolution_type = '4KM'
                    result_data.area_type = 'Full_DISK'
                    result_data.element = None
                    session.add(result_data)
                    count += 1
                    print('{} -----> {}'.format(src_file, dst_file))
                    if count >= 500:
                        session.commit()
                        count = 0
                except Exception as why:
                    print(why)
                    os.remove(dst_file)
    session.commit()
    session.close()


def fy3d_product_1km_daily_data(date_start=None, date_end=None, thread=2, **kwargs):
    source_dir = os.path.join(DATA_ROOT_DIR, 'SourceData', 'FY3D', 'SSI_1KM')
    ext = '.dat'
    resultid = 'FY3D_MERSI_L3_SSI_Daily'
    planid = 1
    resolution_type = '1KM'
    filename_template = 'FY3D-_MERSI--_N_DISK_E_L3-_SSI-_MULT_NOM_{ymd}_{r}_V0001.NC'

    print('开始生产')
    p = Pool(thread)
    for root, dirs, files in os.walk(source_dir):
        for file_name in files:
            if ext is not None:
                if '.' not in ext:
                    ext = '.' + ext
                if os.path.splitext(file_name)[1].lower() != ext.lower():
                    continue
            src_file = os.path.join(root, file_name)
            ymd = file_name[3:11]
            datatime = datetime.strptime(ymd, "%Y%m%d")
            if (not date_start <= datatime <= date_end) or ('Gc' not in file_name):
                continue
            dst_dir = os.path.join(DATA_ROOT_DIR, 'SSIData', 'FY3D', 'SSI_1KM', 'Full', 'Daily', ymd[:6])
            filename_out = filename_template.format(ymd=ymd, r=resolution_type)
            dst_file = os.path.join(dst_dir, filename_out)
            # p.apply_async(fy3d_envi2hdf, args=(src_file, dst_file, resultid, planid, datatime, resolution_type))
            fy3d_envi2hdf(src_file, dst_file, resultid, planid, datatime, resolution_type)


def product_fy4a_4kmcorrect_disk_full_data_orbit(date_start=None, date_end=None, thread=2, **kwargs):
    """
    绘制原始4KM数据的图像
    3个产品，每个产品2张图像，共6张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :param thread:
    :return:
    """
    resultid_data = 'FY4A_AGRI_L2_SSI_Orbit'
    resultid_itcal = 'FY4A_AGRI_L2_SSI_Orbit'

    frequency = 'Orbit'
    resolution_type_in = '4KM'
    resolution_type = '4KMCorrect'

    out_dir = os.path.join(DATA_ROOT_DIR, 'SSIData/FY4A/SSI_{resolution_type}/Full/{frequency}')
    out_dir = out_dir.format(resolution_type=resolution_type, frequency=frequency)

    planid = 1
    results = find_result_data(resultid=resultid_data, datatime_start=date_start, datatime_end=date_end,
                               resolution_type=resolution_type_in)
    in_files = [row.address for row in results]
    in_files.sort()
    in_files_length = len(in_files)
    print('找到的文件总数:{}'.format(in_files_length))

    print('开始生产')
    p = Pool(thread)
    for in_file in in_files[:]:
        in_file_name = os.path.basename(in_file)
        datatime = FY4ASSI.get_date_time_orbit(in_file)
        if datatime.minute != 0:
            continue
        date_time = datatime.strftime('%Y%m%d%H%M%S')
        out_file_name = in_file_name.replace(resolution_type_in, resolution_type)
        out_file = os.path.join(out_dir, date_time[:8], out_file_name)
        p.apply_async(itcal, args=(in_file, out_file, resultid_itcal, planid, datatime, resolution_type))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def product_fy4a_1km_disk_full_data_orbit(date_start=None, date_end=None, thread=2, **kwargs):
    """
    绘制原始4KM数据的图像
    3个产品，每个产品2张图像，共6张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :param thread:
    :return:
    """
    resultid_in = 'FY4A_AGRI_L2_SSI_Orbit'
    resultid_out = 'FY4A_AGRI_L2_SSI_Orbit'

    frequency = 'Orbit'
    resolution_type_in = '4KMCorrect'
    resolution_type = '1KM'

    out_dir = os.path.join(DATA_ROOT_DIR, 'SSIData/FY4A/SSI_{resolution_type}/Full/{frequency}')
    out_dir = out_dir.format(resolution_type=resolution_type, frequency=frequency)

    planid = 1
    results = find_result_data(resultid=resultid_in, datatime_start=date_start, datatime_end=date_end,
                               resolution_type=resolution_type_in)
    in_files = [row.address for row in results]
    in_files.sort()
    in_files_length = len(in_files)
    print('找到的文件总数:{}'.format(in_files_length))

    print('开始生产')
    p = Pool(thread)
    for in_file in in_files[:]:
        in_file_name = os.path.basename(in_file)
        datatime = FY4ASSI.get_date_time_orbit(in_file)
        if datatime.minute != 0:
            continue
        date_time = datatime.strftime('%Y%m%d%H%M%S')
        out_file_name = in_file_name.replace(resolution_type_in, resolution_type)
        out_file = os.path.join(out_dir, date_time[:8], out_file_name)
        if DEBUG:
            fy4a_ssi_4km_to_1km(in_file, out_file, resultid_out, planid, datatime, resolution_type)
        else:
            p.apply_async(fy4a_ssi_4km_to_1km,
                          args=(in_file, out_file, resultid_out, planid, datatime, resolution_type))

    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def product_fy4a_1kmcorrect_disk_full_data_orbit(date_start=None, date_end=None, thread=2, **kwargs):
    """
    绘制原始4KM数据的图像
    3个产品，每个产品2张图像，共6张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :param thread:
    :return:
    """
    resultid_in = 'FY4A_AGRI_L2_SSI_Orbit'
    resultid_out = 'FY4A_AGRI_L2_SSI_Orbit'

    frequency = 'Orbit'
    resolution_type_in = '1KM'
    resolution_type = '1KMCorrect'

    out_dir = os.path.join(DATA_ROOT_DIR, 'SSIData/FY4A/SSI_{resolution_type}/Full/{frequency}')
    out_dir = out_dir.format(resolution_type=resolution_type, frequency=frequency)

    planid = 1
    # results = find_result_data(resultid=resultid_in, datatime_start=date_start, datatime_end=date_end,
    #                            resolution_type=resolution_type_in)
    # in_files = [row.address for row in results]

    in_dir = '/home/gfssi/Project/OM/gfssi/step4/RetData/20171015'
    in_files = os.listdir(in_dir)
    in_files = [os.path.join(in_dir, in_file) for in_file in in_files if 'finally' in in_file]

    in_files.sort()
    in_files_length = len(in_files)
    print('找到的文件总数:{}'.format(in_files_length))

    print('开始生产')
    p = Pool(thread)
    for in_file in in_files:
        in_file_name = os.path.basename(in_file)
        ymdhm = in_file_name[:12]
        datatime = datetime.strptime(ymdhm, '%Y%m%d%H%M') - relativedelta(hours=8)
        if not date_start <= datatime <= date_end:
            continue
        if datatime.minute != 0:
            continue
        date_time = datatime.strftime('%Y%m%d%H%M%S')
        out_file_name = 'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_{ymdh}0000_{ymdh}1459_{r}_V0001.NC'.format(
            ymdh=date_time[0:10], r=resolution_type)
        # out_file_name = in_file_name.replace(resolution_type_in, resolution_type)
        out_file = os.path.join(out_dir, date_time[:8], out_file_name)
        if DEBUG:
            fy4a_1km_correct_txt2hdf(in_file, out_file, resultid_out, planid, datatime, resolution_type)
        else:
            p.apply_async(fy4a_1km_correct_txt2hdf,
                          args=(in_file, out_file, resultid_out, planid, datatime, resolution_type))

    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def product_combine_data(date_start=None, date_end=None, frequency=None, thread=2,
                         resolution_type=None, sat_sensor=None):
    sat_sensor = sat_sensor.upper()
    sat, sensor = sat_sensor.split('_')
    out_dir = os.path.join(DATA_ROOT_DIR, 'SSIData/{sat}/SSI_{resolution_type}/Full/{frequency}')
    out_dir = out_dir.format(sat=sat, resolution_type=resolution_type, frequency=frequency)
    if sat == 'FY4A':
        out_name = 'FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_{date}_{resolution_type}_V0001.NC'
    elif sat == 'FY3D':
        out_name = 'FY3D-_MERSI--_N_DISK_E_L3-_SSI-_MULT_NOM_{date}_{resolution_type}_V0001.NC'
    else:
        print('不支持的卫星:sat_sensor={}'.format(sat_sensor))
        return

    if frequency == 'Daily':
        resultid_data_in = '{}_L2_SSI_Orbit'.format(sat_sensor)
        strf_name = '%Y%m%d'
        strf_dir = '%Y%m'
        date_relativedelta = relativedelta(days=1)
        daily = True
        planid = 1
        get_date_time = FY4ASSI.get_date_time_daily
    elif frequency == 'Monthly':
        resultid_data_in = '{}_L3_SSI_Daily'.format(sat_sensor)
        out_dir = out_dir.format(resolution_type=resolution_type, frequency='Monthly')
        strf_name = '%Y%m'
        strf_dir = '%Y'
        date_relativedelta = relativedelta(months=1)
        daily = False
        planid = 1
        get_date_time = FY4ASSI.get_date_time_monthly
    elif frequency == 'Yearly':
        resultid_data_in = '{}_L3_SSI_Monthly'.format(sat_sensor)
        out_dir = out_dir.format(resolution_type=resolution_type, frequency='Yearly')
        strf_name = '%Y'
        strf_dir = None
        date_relativedelta = relativedelta(years=1)
        daily = False
        planid = 1
        get_date_time = FY4ASSI.get_date_time_yearly
    else:
        raise ValueError('不支持的类型：{}'.format(frequency))

    resultid_combine = '{sat_sensor}_L3_SSI_{frequency}'.format(sat_sensor=sat_sensor, frequency=frequency)

    files_combine = []
    p = Pool(thread)
    date_tmp = date_start
    while date_tmp <= date_end:
        time.sleep(0.1)
        date_name = date_tmp.strftime(strf_name)
        if strf_dir is not None:
            date_dir = date_tmp.strftime(strf_dir)
        else:
            date_dir = ''

        date_s = datetime.strptime(date_name, strf_name)
        date_e = date_s + date_relativedelta - relativedelta(seconds=1)

        try:
            results = find_result_data(resultid=resultid_data_in, datatime_start=date_s, datatime_end=date_e,
                                       resolution_type=resolution_type)
        except Exception as why:
            print(why)
            continue
        in_files = [row.address for row in results]
        in_files.sort()
        in_files_length = len(in_files)
        print('找到的文件总数:{}'.format(in_files_length))

        out_name_tmp = out_name.format(date=date_name, resolution_type=resolution_type)
        out_file = os.path.join(out_dir, date_dir, out_name_tmp)
        datatime = get_date_time(out_file)
        if DEBUG:
            combine_full(in_files, out_file, daily, resultid_combine, planid, datatime,
                         resolution_type)
        else:
            p.apply_async(combine_full, args=(in_files, out_file, daily, resultid_combine, planid, datatime,
                                              resolution_type))
        files_combine.append(out_file)
        date_tmp += date_relativedelta
    p.close()
    p.join()


def product_image(date_start=None, date_end=None, frequency=None, thread=2,
                  resolution_type=None, sat_sensor=None, **kwargs):
    sat_sensor = sat_sensor.upper()
    sat, sensor = sat_sensor.split('_')

    if frequency == 'Orbit':
        resultid_data_in = '{}_L2_SSI_Orbit'.format(sat_sensor)
        if sat == 'FY4A':
            vmin, vmax = COLORBAR_RANGE_ORBIT_FY4A
        else:
            print('此时间分辨率={}不支持卫星={}'.format(frequency, sat_sensor))
            return
        planid = 1
        get_date_time = FY4ASSI.get_date_time_orbit
    elif frequency == 'Daily':
        resultid_data_in = '{}_L3_SSI_Daily'.format(sat_sensor)
        if sat == 'FY4A':
            vmin, vmax = COLORBAR_RANGE_DAILY_FY4A
        elif sat == 'FY3D':
            vmin, vmax = COLORBAR_RANGE_DAILY_FY3D
        else:
            print('此时间分辨率={}不支持卫星={}'.format(frequency, sat_sensor))
            return
        planid = 1
        get_date_time = FY4ASSI.get_date_time_daily
    elif frequency == 'Monthly':
        resultid_data_in = '{}_L3_SSI_Monthly'.format(sat_sensor)
        if sat == 'FY4A':
            vmin, vmax = COLORBAR_RANGE_MONTHLY_FY4A
        elif sat == 'FY3D':
            vmin, vmax = COLORBAR_RANGE_MONTHLY_FY3D
        else:
            print('此时间分辨率={}不支持卫星={}'.format(frequency, sat_sensor))
            return
        planid = 1
        get_date_time = FY4ASSI.get_date_time_monthly
    elif frequency == 'Yearly':
        resultid_data_in = '{}_L3_SSI_Yearly'.format(sat_sensor)
        if sat == 'FY4A':
            vmin, vmax = COLORBAR_RANGE_YEARLY_FY4A
        elif sat == 'FY3D':
            vmin, vmax = COLORBAR_RANGE_MONTHLY_FY3D
        else:
            print('此时间分辨率={}不支持卫星={}'.format(frequency, sat_sensor))
            return
        planid = 1
        get_date_time = FY4ASSI.get_date_time_yearly
    else:
        raise ValueError('不支持的类型：{}'.format(frequency))

    resultid_image = resultid_data_in + '_IMG'

    try:
        results = find_result_data(resultid=resultid_data_in, datatime_start=date_start, datatime_end=date_end,
                                   resolution_type=resolution_type)
    except Exception as why:
        print(why)
        return

    in_files = [row.address for row in results]
    in_files.sort()
    in_files_length = len(in_files)
    print('找到的文件总数:{}'.format(in_files_length))

    print('开始绘图')
    p = Pool(thread)
    for in_file in in_files[:]:
        datatime = get_date_time(in_file)
        if DEBUG:
            plot_map_full(in_file, vmin, vmax, resultid_image, planid, datatime, resolution_type)
        else:
            p.apply_async(plot_map_full,
                          args=(in_file, vmin, vmax, resultid_image, planid, datatime, resolution_type))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def product_area_data(date_start=None, date_end=None, thread=3, left_up_lon=None, left_up_lat=None,
                      right_down_lon=None, right_down_lat=None, resolution_type=None, resultid=None,
                      **kwargs):
    """
    生成原始数据的中国区时次数据
    3个产品，每个产品1张图像，共3张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :param thread:
    :param left_up_lon:
    :param left_up_lat:
    :param right_down_lon:
    :param right_down_lat:
    :param resolution_type:
    :param resultid:
    :return:
    """
    frequency = resultid.split('_')[-1]
    if isinstance(date_start, str):
        date_start = datetime.strptime(date_start, '%Y%m%d%H%M%S')
        date_end = datetime.strptime(date_end, '%Y%m%d%H%M%S')

    results = find_result_data(resultid=resultid, datatime_start=date_start, datatime_end=date_end,
                               resolution_type=resolution_type)
    in_files = [row.address for row in results]
    in_files.sort()
    in_files_length = len(in_files)
    print('找到的文件总数:{}'.format(in_files_length))

    sat, sensor = resultid.split('_')[:2]

    out_dir = os.path.join(DATA_ROOT_DIR, 'TmpData', '{sat}/SSI_{resolution_type}/Area/{frequency}'.format(
        sat=sat, resolution_type=resolution_type, frequency=frequency))
    out_dir = os.path.join(out_dir, '{:08.4f}_{:08.4f}_{:08.4f}_{:08.4f}'.format(left_up_lon, left_up_lat,
                                                                                 right_down_lon, right_down_lat))

    print('开始生成区域数据')
    print(left_up_lon, left_up_lat, right_down_lon, right_down_lat)
    out_files = []

    for in_file in in_files[:]:
        filename = os.path.basename(in_file)
        out_file = os.path.join(out_dir, filename)
        r = area(in_file, out_file, left_up_lon, left_up_lat, right_down_lon, right_down_lat, resolution_type, resultid)
        if r is not None:
            out_files.append(r)

    # p = Pool(thread)
    # for in_file in in_files[:]:
    #     filename = os.path.basename(in_file)
    #     out_file = os.path.join(out_dir, filename)
    #     out_files.append(out_file)
    #     p.apply_async(area, args=(in_file, out_file, left_up_lon, left_up_lat, right_down_lon, right_down_lat,
    #                               resolution_type, resultid))
    # p.close()
    # p.join()

    if len(out_files) > 0:
        return out_files
    else:
        return


def product_point_data(date_start=None, date_end=None, lon=None, lat=None, point_file=None,
                       resolution_type=None, resultid=None, element=None, idx=None, ck=None,
                       sat_sensor=None, **kwargs):
    sat_sensor = sat_sensor.upper()
    sat, sensor = sat_sensor.split('_')
    date_s = datetime.strptime(date_start, '%Y%m%d%H%M%S')
    date_e = datetime.strptime(date_end, '%Y%m%d%H%M%S')
    out_dir = os.path.join(DATA_ROOT_DIR, 'TmpData', '{}'.format(sat))
    outname = '{sat}-_{sensor}--_{lon:07.3f}N_DISK_{lat:07.3f}E_L2-_SSI-_MULT_NOM_' \
              '{date_start}_{date_end}_{resolution_type}_V0001_{site}.TXT'
    if 'fy3d' in sat.lower():
        loader = FY4ASSI
    elif 'fy4a' in sat.lower():
        loader = FY3DSSI
    else:
        raise ValueError('不支持的卫星：{}'.format(sat))

    if 'Orbit' in resultid:
        get_datetime = loader.get_date_time_orbit
    elif 'Daily' in resultid:
        get_datetime = loader.get_date_time_daily
    elif 'Monthly' in resultid:
        get_datetime = loader.get_date_time_monthly
    elif 'Yearly' in resultid:
        get_datetime = loader.get_date_time_yearly
    else:
        print('不支持的时间频率:{}'.format(resultid))
        return

    results = find_result_data(resultid=resultid, datatime_start=date_s, datatime_end=date_e,
                               resolution_type=resolution_type)
    full_files = [row.address for row in results]
    full_files.sort()
    in_files_length = len(full_files)
    print('找到的文件总数:{}'.format(in_files_length))
    if in_files_length <= 0:
        return

    if point_file is None:  # 单点数据
        lon = float(lon)
        lat = float(lat)
        pre_dist = 0.08
        index = get_point_index(lon, lat, idx, ck, pre_dist)
        print('index', index)
        if index is None:
            print('没有找到最近点:lon {}   lat:{}'.format(lon, lat))
            return

        datas = []
        dates = []
        values = []
        count = 0
        s = datetime.now()

        thread_lock = threading.Lock()
        for full_file in full_files:
            if not os.path.isfile(full_file):
                print('文件不存在: {}'.format(full_file))
                count += 1
                continue
            _get_point_data(full_file, element, index, get_datetime, resultid,
                            dates, datas, values, thread_lock)

        # thread_lock = threading.Lock()
        # ts = []
        # for full_file in full_files:
        #     if not os.path.isfile(full_file):
        #         print('文件不存在: {}'.format(full_file))
        #         count += 1
        #         continue
        #     t = threading.Thread(target=_get_point_data, args=(full_file, element, index, get_datetime, resultid,
        #                                                        dates, datas, values, thread_lock))
        #     t.start()
        #     ts.append(t)
        # for t in ts:
        #     t.join()
        print('获取{}数据消耗时间:{}'.format(in_files_length, datetime.now() - s))
        if len(datas) <= 0:
            print('没有找到有效的点数据')
            return

        if element is not None:  # 返回单点数据
            dates_new = []
            values_new = []

            for date, value in sorted(zip(dates, values), key=lambda x: x[0]):
                dates_new.append(date)
                values_new.append(float(value[element]))
            if len(values_new) > 0:
                return {'date': dates_new, 'value': values_new, 'values': values}
            else:
                print('没有找到有效的点数据')
                return
        else:  # 返回单点的TXT文件
            out_file = os.path.join(out_dir, outname.format(sat=sat, sensor=sensor, lon=lon, lat=lat,
                                                            date_start=date_start,
                                                            date_end=date_end, resolution_type=resolution_type,
                                                            site=''))
            if len(datas) > 0:
                with open(out_file, 'w') as fp:
                    header = "Date\tItol\tIb\tId\tG0\tGt\tDNI\n"
                    fp.write(header)
                    datas.sort()
                    fp.writelines(datas)
                return out_file
            else:
                print('没有找到有效的点数据')
                return
    else:  # 多点数据
        point_infos = []
        indexs = []
        with open(point_file, 'r') as fp:
            fp.readline()
            for row in fp.readlines():
                point_name, lon, lat = row.strip().split('\t')
                lon = float(lon)
                lat = float(lat)
                pre_dist = 0.08
                index = get_point_index(lon, lat, idx, ck, pre_dist)
                if index is None:
                    print('没有找到最近点:lon {}   lat:{}'.format(lon, lat))
                    continue
                else:
                    point_infos.append((point_name, lon, lat))
                    print(type(index[0]))
                    indexs.append([int(index[0]), int(index[1])])

        for info in point_infos:
            print(info)

        dates = []
        values = []
        count = 0
        s = datetime.now()
        thread_lock = threading.Lock()
        for full_file in full_files:
            if not os.path.isfile(full_file):
                print('文件不存在: {}'.format(full_file))
                count += 1
                continue
            _get_multi_point_data(full_file, indexs, get_datetime, resultid, dates, values, thread_lock)
        print('获取{}数据消耗时间:{}'.format(in_files_length, datetime.now() - s))
        print(values)

        out_files = []
        for i, info in enumerate(point_infos):  # i是站点的索引值
            point_name, lon, lat = info
            print('站点名: {}'.format(point_name))
            datas = []
            for j, date in enumerate(dates):  # j 是日期的索引值
                print('日期：{}'.format(date))
                datas_tmp = values[j]
                data_format = {'date': date}
                for element_ in datas_tmp:
                    data_ = datas_tmp[element_][i]
                    data_format[element_] = data_
                    # if data_ == 0:
                    #     data_format[element_] = data_
                    # else:
                    #     data_format[element_] = np.nan
                data_str = '{date}\t{Itol:0.4f}\t{Ib:0.4f}\t{Id:0.4f}\t{G0:0.4f}\t{Gt:0.4f}\t{DNI:0.4f}\n'.format(
                    **data_format)
                datas.append(data_str)
            out_file = os.path.join(out_dir, outname.format(sat=sat, sensor=sensor, lon=lon, lat=lat,
                                                            date_start=date_start,
                                                            date_end=date_end, resolution_type=resolution_type,
                                                            site=point_name))
            with open(out_file, 'w') as fp:
                header = "Date\tItol\tIb\tId\tG0\tGt\tDNI\n"
                fp.write(header)
                datas.sort()
                fp.writelines(datas)
            out_files.append(out_file)
        return out_files

        # for full_file in full_files:
        #     if not os.path.isfile(full_file):
        #         print('文件不存在: {}'.format(full_file))
        #         count += 1
        #         continue
        #     t = threading.Thread(target=_get_multi_point_data, args=(full_file, indexs, get_datetime,
        #                                                              dates, values, thread_lock))
        #     t.start()
        #     ts.append(t)
        # for t in ts:
        #     t.join()
        # print('获取{}数据消耗时间:{}'.format(in_files_length, datetime.now() - s))
        # if len(datas) <= 0:
        #     print('没有找到有效的点数据')
        #     return


def _get_multi_point_data(full_file, indexs, get_datetime, resultid,
                          dates, values, thread_lock, **kwargs):
    indexs = np.array(indexs, dtype=np.int)
    datas_tmp = {}
    length = len(indexs)
    loader = FY4ASSI(full_file)
    data_geter = {
        'Itol': loader.get_ssi,
        'Ib': loader.get_ib,
        'Id': loader.get_id,
        'G0': loader.get_g0,
        'Gt': loader.get_gt,
        'DNI': loader.get_dni,
    }
    elements = data_geter.keys()
    for element_ in elements:
        try:
            data_tmp = data_geter[element_]()[indexs[:, 0], indexs[:, 1]]
        except Exception:
            data_tmp = [np.nan for i in range(length)]
        datas_tmp[element_] = data_tmp
    date = get_datetime(full_file)
    if 'Orbit' in resultid:
        date += relativedelta(hours=8)
    date = date.strftime('%Y%m%d%H%M%S')
    with thread_lock:
        dates.append(date)
        values.append(datas_tmp)


def _get_point_data(full_file, element, index, get_datetime, resultid,
                    dates, datas, values, thread_lock, **kwargs):
    datas_tmp = {}

    loader = FY4ASSI(full_file)
    data_geter = {
        'Itol': loader.get_ssi,
        'Ib': loader.get_ib,
        'Id': loader.get_id,
        'G0': loader.get_g0,
        'Gt': loader.get_gt,
        'DNI': loader.get_dni,
    }

    elements = data_geter.keys()

    for element_ in elements:
        try:
            data_tmp = data_geter[element_]()[index]
            print(data_tmp)
            if np.isnan(data_tmp):
                datas_tmp[element_] = 0
            else:
                datas_tmp[element_] = data_tmp
        except Exception as why:
            datas_tmp[element_] = 0

    date = get_datetime(full_file)
    if 'Orbit' in resultid:
        date += relativedelta(hours=8)
    date = date.strftime('%Y%m%d%H%M%S')

    print(datas_tmp)

    data_format = {'date': date}
    for element_ in datas_tmp:
        data_ = datas_tmp[element_]
        if data_ != 0:
            data_format[element_] = data_
        else:
            data_format[element_] = np.nan
    data_str = '{date}\t{Itol:0.4f}\t{Ib:0.4f}\t{Id:0.4f}\t{G0:0.4f}\t{Gt:0.4f}\t{DNI:0.4f}\n'.format(
        **data_format)

    with thread_lock:
        dates.append(date)
        datas.append(data_str)
        if datas_tmp.get(element) is not None:
            values.append(datas_tmp)


def product_4km_disk_area_image(date_start=None, date_end=None, thread=3, frequency=None, resolution_type=None,
                                **kwargs):
    """
    生成原始数据的中国区时次数据
    3个产品，每个产品1张图像，共3张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :param thread:
    :param frequency:
    :param resolution_type:
    :return:
    """
    left_up_lon = 70
    left_up_lat = 50
    right_down_lon = 140
    right_down_lat = 0

    in_dir = os.path.join(DATA_ROOT_DIR, 'SSIData/FY4A/SSI_{resolution_type}/Full/{frequency}'.format(
        resolution_type=resolution_type, frequency=frequency))
    out_dir = os.path.join(DATA_ROOT_DIR, 'SSIData/FY4A/SSI_{resolution_type}/China/{frequency}'.format(
        resolution_type=resolution_type, frequency=frequency))

    if frequency == 'Orbit':
        pattern = r'.*FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_(\d{14})_\d{14}_4000M_V0001'
        strf_name = '%Y%m%d%H%M%S'
        date_end_str = date_end.strftime(strf_name)
        strf_dir = '%Y%m%d'
        date_relativedelta = relativedelta(days=1)
        resultid_image = 'FY4A_AGRI_L2_SSI_Orbit_IMG'
        resultid_data = 'FY4A_AGRI_L2_SSI_Orbit'
        planid = 1
        get_date_time = FY4ASSI.get_date_time_orbit
    elif frequency == 'Daily':
        pattern = r'.*FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_(\d{8})_4000M_V0001'
        strf_name = '%Y%m%d'
        date_end_str = date_end.strftime(strf_name)
        strf_dir = '%Y%m'
        date_relativedelta = relativedelta(months=1)
        resultid_image = 'FY4A_AGRI_L3_SSI_Daily_IMG'
        resultid_data = 'FY4A_AGRI_L3_SSI_Daily'
        planid = 1
        get_date_time = FY4ASSI.get_date_time_daily
    elif frequency == 'Monthly':
        pattern = r'.*FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_(\d{6})_4000M_V0001'
        strf_name = '%Y%m'
        date_end_str = date_end.strftime(strf_name)
        strf_dir = '%Y'
        date_relativedelta = relativedelta(years=1)
        resultid_image = 'FY4A_AGRI_L3_SSI_China_LATLON_4KM_1Month_{data_id}'
        resultid_data = 'FY4A_AGRI_L3_SSI_China_DISK_4KM_1Month'
        planid = 1
        get_date_time = FY4ASSI.get_date_time_monthly
    elif frequency == 'Yearly':
        pattern = r'.*FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_(\d{4})_4000M_V0001'
        strf_name = '%Y'
        date_end_str = date_end.strftime(strf_name)
        strf_dir = None
        date_relativedelta = None
        resultid_image = 'FY4A_AGRI_L3_SSI_China_LATLON_4KM_1Year_{data_id}'
        resultid_data = 'FY4A_AGRI_L3_SSI_China_DISK_4KM_1Year'
        planid = 1
        get_date_time = FY4ASSI.get_date_time_yearly
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
    in_files.sort()
    in_files_length = len(in_files)
    print('找到的文件总数:{}'.format(in_files_length))

    print('开始生成中国区数据')
    p = Pool(thread)
    for in_file in in_files[:]:
        out_file = in_file.replace(in_dir, out_dir)
        datatime = get_date_time(out_file)
        p.apply_async(area, args=(in_file, out_file, '4km', left_up_lon, left_up_lat, right_down_lon, right_down_lat,
                                  resultid_data, planid, datatime))
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
        datatime = get_date_time(out_file)
        p.apply_async(plot_map_area, args=(in_file, out_file, '4km', left_up_lon, left_up_lat, right_down_lon,
                                           right_down_lat, resultid_image, planid, datatime))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


if __name__ == '__main__':
    # 数据入库
    # fy4a_save_4km_orbit_data_in_database()  # FY4A 4KM原始数据入库

    # =================================生产数据==================================
    # 轨道：生产数据：FY4A
    # start = datetime.strptime('20170601000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20191231235959', '%Y%m%d%H%M%S')
    # product_fy4a_4kmcorrect_disk_full_data_orbit(start, end)  # FY4A 4KMCorrect
    # start = datetime.strptime('20190601000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190601235959', '%Y%m%d%H%M%S')
    # product_fy4a_1km_disk_full_data_orbit(start, end)  # FY4A 1KM
    # start = datetime.strptime('20171015000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20171015235959', '%Y%m%d%H%M%S')
    # product_fy4a_1kmcorrect_disk_full_data_orbit(start, end)  # FY4A 1KMCorrect

    # 日：生产数据：FY4A FY3D
    # start = datetime.strptime('20190601000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630235959', '%Y%m%d%H%M%S')
    # product_combine_data(start, end, frequency='Daily', resolution_type='4KM', sat_sensor='FY4A_AGRI')  # FY4A 4KM
    # start = datetime.strptime('20190601000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630235959', '%Y%m%d%H%M%S')
    # product_combine_data(start, end, frequency='Daily', resolution_type='4KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 4KMCorrect
    # start = datetime.strptime('20190601000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190602235959', '%Y%m%d%H%M%S')
    # product_combine_data(start, end, frequency='Daily', resolution_type='1KM', sat_sensor='FY4A_AGRI')  # FY4A 1KM
    # start = datetime.strptime('20171015000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20171015235959', '%Y%m%d%H%M%S')
    # product_combine_data(start, end, frequency='Daily', resolution_type='1KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 1KMCorrect
    # start = datetime.strptime('20190501000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190501235959', '%Y%m%d%H%M%S')
    # fy3d_product_1km_daily_data(start, end)  # FY3D 1KM
    #
    # # 月：生产数据：FY4A FY3D
    # start = datetime.strptime('20190601000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630235959', '%Y%m%d%H%M%S')
    # product_combine_data(start, end, frequency='Monthly', resolution_type='4KM', sat_sensor='FY4A_AGRI')  # FY4A 4KM
    # product_combine_data(start, end, frequency='Monthly', resolution_type='4KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 4KMCorrect
    # product_combine_data(start, end, frequency='Monthly', resolution_type='1KM', sat_sensor='FY4A_AGRI')  # FY4A 1KM
    # product_combine_data(start, end, frequency='Monthly', resolution_type='1KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 1KMCorrect
    # product_combine_data(start, end, frequency='Monthly', resolution_type='1KM', sat_sensor='FY3D_MERSI')  # FY3D 1KM
    #
    # # 年：生产数据：FY4A FY3D
    # start = datetime.strptime('20190601000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630235959', '%Y%m%d%H%M%S')
    # product_combine_data(start, end, frequency='Yearly', resolution_type='4KM', sat_sensor='FY4A_AGRI')  # FY4A 4KM
    # product_combine_data(start, end, frequency='Yearly', resolution_type='4KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 4KMCorrect
    # product_combine_data(start, end, frequency='Yearly', resolution_type='1KM', sat_sensor='FY4A_AGRI')  # FY4A 1KM
    # product_combine_data(start, end, frequency='Yearly', resolution_type='1KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 1KMCorrect
    # product_combine_data(start, end, frequency='Yearly', resolution_type='1KM', sat_sensor='FY3D_MERSI')  # FY3D 1KM
    #
    # # 轨道：绘图：FY4A
    # start = datetime.strptime('20190410000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190410235959', '%Y%m%d%H%M%S')
    # product_image(start, end, frequency='Orbit', resolution_type='4KM', sat_sensor='FY4A_AGRI')  # FY4A 4KM
    # product_image(start, end, frequency='Orbit', resolution_type='4KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 4KMCorrect
    # product_image(start, end, frequency='Orbit', resolution_type='1KM', sat_sensor='FY4A_AGRI')  # FY4A 1KM
    # product_image(start, end, frequency='Orbit', resolution_type='1KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 1KMCorrect
    #
    # # 日：绘图：FY4A FY3D
    # product_image(start, end, frequency='Daily', resolution_type='4KM', sat_sensor='FY4A_AGRI')  # FY4A 4KM
    # start = datetime.strptime('20180901000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20180902000000', '%Y%m%d%H%M%S')
    # product_image(start, end, frequency='Daily', resolution_type='4KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 4KMCorrect
    # product_image(start, end, frequency='Daily', resolution_type='1KM', sat_sensor='FY4A_AGRI')  # FY4A 1KM
    # product_image(start, end, frequency='Daily', resolution_type='1KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 1KMCorrect
    start = datetime.strptime('20190101000000', '%Y%m%d%H%M%S')
    end = datetime.strptime('20190101000000', '%Y%m%d%H%M%S')
    product_image(start, end, frequency='Daily', resolution_type='1KM', sat_sensor='FY3D_MERSI')  # FY3D 1KM
    #
    # # 月：绘图：FY4A FY3D
    # product_image(start, end, frequency='Monthly', resolution_type='4KM', sat_sensor='FY4A_AGRI')  # FY4A 4KM
    # product_image(start, end, frequency='Monthly', resolution_type='4KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 4KMCorrect
    # product_image(start, end, frequency='Monthly', resolution_type='1KM', sat_sensor='FY4A_AGRI')  # FY4A 1KM
    # product_image(start, end, frequency='Monthly', resolution_type='1KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 1KMCorrect
    # product_image(start, end, frequency='Monthly', resolution_type='1KM', sat_sensor='FY3D_MERSI')  # FY3D 1KM
    #
    # # 年：绘图：FY4A FY3D
    # product_image(start, end, frequency='Yearly', resolution_type='4KM', sat_sensor='FY4A_AGRI')  # FY4A 4KM
    # product_image(start, end, frequency='Yearly', resolution_type='4KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 4KMCorrect
    # product_image(start, end, frequency='Yearly', resolution_type='1KM', sat_sensor='FY4A_AGRI')  # FY4A 1KM
    # product_image(start, end, frequency='Yearly', resolution_type='1KMCorrect', sat_sensor='FY4A_AGRI')  # FY4A 1KMCorrect
    # product_image(start, end, frequency='Yearly', resolution_type='1KM', sat_sensor='FY3D_MERSI')  # FY3D 1KM

    # # 生产区域数据
    # start = datetime.strptime('20180901000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190930235959', '%Y%m%d%H%M%S')
    # # 江西
    # product_fy4a_disk_area_data(start, end, frequency='Daily', resolution_type='4KMCorrect', sat_sensor='FY4A_AGRI',
    #                             left_up_lon=113., left_up_lat=31., right_down_lon=119., right_down_lat=24,
    #                             resultid='FY4A_AGRI_L3_SSI_Daily')
    # # 浙江
    # product_fy4a_disk_area_data(start, end, frequency='Daily', resolution_type='4KMCorrect', sat_sensor='FY4A_AGRI',
    #                             left_up_lon=118., left_up_lat=32., right_down_lon=123., right_down_lat=27.,
    #                             resultid='FY4A_AGRI_L3_SSI_Daily')
    # # 湖北
    # product_fy4a_disk_area_data(start, end, frequency='Daily', resolution_type='4KMCorrect', sat_sensor='FY4A_AGRI',
    #                             left_up_lon=108., left_up_lat=34., right_down_lon=117., right_down_lat=29.,
    #                             resultid='FY4A_AGRI_L3_SSI_Daily')
