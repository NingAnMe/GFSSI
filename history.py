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
import re
import os
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

from lib.lib_read_ssi import FY4ASSI
from lib.lib_database import find_result_data, Session, ResultData
from lib.lib_get_index_by_lonlat import get_point_index
from lib.lib_constant import KDTREE_LUT_FY4_4KM

# 获取程序所在目录位置
g_path, _ = os.path.split(os.path.realpath(__file__))
# 进入该目录
os.chdir(g_path)

data_root_dir = '/home/gfssi/GFData/'

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


def fy4a_save_source_data_in_database():
    source_dir = os.path.join(data_root_dir, 'SourceData')
    ssi_dir = os.path.join(data_root_dir, 'SSIData')
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


def product_fy4a_4kmcorrect_disk_full_data_orbit(date_start=None, date_end=None, thread=2):
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
    resolution_type = '4KMCorrect'

    out_dir = os.path.join(data_root_dir, 'SSIData/FY4A/SSI_{resolution_type}/Full/{frequency}')
    out_dir = out_dir.format(resolution_type=resolution_type, frequency=frequency)

    planid = 1
    results = find_result_data(resultid=resultid_data, datatime_start=date_start, datatime_end=date_end,
                               resolution_type='4KM')
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
        out_file_name = in_file_name.replace('4KM', resolution_type)
        out_file = os.path.join(out_dir, date_time[:8], out_file_name)
        p.apply_async(itcal, args=(in_file, out_file, resultid_itcal, planid, datatime, resolution_type))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def product_fy4a_1km_disk_full_data_orbit(date_start=None, date_end=None, thread=2):
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
    resolution_type = '1KM'

    out_dir = os.path.join(data_root_dir, 'SSIData/FY4A/SSI_{resolution_type}/Full/{frequency}')
    out_dir = out_dir.format(resolution_type=resolution_type, frequency=frequency)

    planid = 1
    results = find_result_data(resultid=resultid_in, datatime_start=date_start, datatime_end=date_end,
                               resolution_type='4KMCorrect')
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
        out_file_name = in_file_name.replace('4KMCorrect', resolution_type)
        out_file = os.path.join(out_dir, date_time[:8], out_file_name)
        if DEBUG:
            fy4a_ssi_4km_to_1km(in_file, out_file, resultid_out, planid, datatime, resolution_type)
        else:
            p.apply_async(fy4a_ssi_4km_to_1km,
                          args=(in_file, out_file, resultid_out, planid, datatime, resolution_type))

    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def product_fy4a_disk_full_image_orbit(date_start=None, date_end=None, thread=2, resolution_type=None):
    """
    绘制原始4KM数据的图像
    3个产品，每个产品2张图像，共6张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :param thread:
    :param resolution_type:
    :return:
    """
    resultid_data = 'FY4A_AGRI_L2_SSI_Orbit'
    resultid_image = 'FY4A_AGRI_L2_SSI_Orbit_IMG'
    planid = 1
    vmin = 0
    vmax = 1000

    results = find_result_data(resultid=resultid_data, datatime_start=date_start, datatime_end=date_end,
                               resolution_type=resolution_type)
    in_files = [row.address for row in results]
    in_files.sort()
    in_files_length = len(in_files)
    print('找到的文件总数:{}'.format(in_files_length))

    print('开始绘图')
    p = Pool(thread)
    for in_file in in_files[:]:
        datatime = FY4ASSI.get_date_time_orbit(in_file)
        if DEBUG:
            plot_map_full(in_file, vmin, vmax, resultid_image, planid, datatime, resolution_type, )
        else:
            p.apply_async(plot_map_full, args=(in_file, vmin, vmax, resultid_image, planid, datatime, resolution_type,))

    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def product_fy4a_disk_full_data_and_image(date_start=None, date_end=None, frequency=None, thread=2,
                                          resolution_type=None):
    """
    4KM数据日合成
    绘制原始4KM数据的图像
    3个产品，每个产品2张图像，共6张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :param frequency:
    :param thread:
    :param resolution_type:
    :return:
    """
    out_dir = os.path.join(data_root_dir, 'SSIData/FY4A/SSI_{resolution_type}/Full/{frequency}')
    out_dir = out_dir.format(resolution_type=resolution_type, frequency=frequency)
    out_name = 'FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_{date}_{resolution_type}_V0001.NC'

    if frequency == 'Daily':
        resultid_data_in = 'FY4A_AGRI_L2_SSI_Orbit'
        strf_name = '%Y%m%d'
        strf_dir = '%Y%m'
        date_relativedelta = relativedelta(days=1)
        daily = True
        vmin = 0
        vmax = 20
        planid = 1
        get_date_time = FY4ASSI.get_date_time_daily
    elif frequency == 'Monthly':
        resultid_data_in = 'FY4A_AGRI_L3_SSI_Daily'
        out_dir = out_dir.format(resolution_type=resolution_type, frequency='Monthly')
        strf_name = '%Y%m'
        strf_dir = '%Y'
        date_relativedelta = relativedelta(months=1)
        daily = False
        vmin = 0
        vmax = 600
        planid = 1
        get_date_time = FY4ASSI.get_date_time_monthly
    elif frequency == 'Yearly':
        resultid_data_in = 'FY4A_AGRI_L3_SSI_Monthly'
        out_dir = out_dir.format(resolution_type=resolution_type, frequency='Yearly')
        strf_name = '%Y'
        strf_dir = None
        date_relativedelta = relativedelta(years=1)
        daily = False
        vmin = 0
        vmax = 7000
        planid = 1
        get_date_time = FY4ASSI.get_date_time_yearly
    else:
        raise ValueError('不支持的类型：{}'.format(frequency))

    resultid_image = 'FY4A_AGRI_L3_SSI_{frequency}_IMG'.format(frequency=frequency)
    resultid_combine = 'FY4A_AGRI_L3_SSI_{frequency}'.format(frequency=frequency)

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

    print('开始绘图')
    p = Pool(thread)
    for file_combine in files_combine[:]:
        time.sleep(0.5)
        datatime = get_date_time(file_combine)
        if DEBUG:
            plot_map_full(file_combine, vmin, vmax, resultid_image, planid, datatime, resolution_type)
        else:
            p.apply_async(plot_map_full,
                          args=(file_combine, vmin, vmax, resultid_image, planid, datatime, resolution_type))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def product_fy4a_disk_area_data(date_start=None, date_end=None, thread=3, left_up_lon=None, left_up_lat=None,
                                right_down_lon=None, right_down_lat=None, resolution_type=None, resultid=None):
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
    date_start = datetime.strptime(date_start, '%Y%m%d%H%M%S')
    date_end = datetime.strptime(date_end, '%Y%m%d%H%M%S')

    results = find_result_data(resultid=resultid, datatime_start=date_start, datatime_end=date_end,
                               resolution_type=resolution_type)
    in_files = [row.address for row in results]
    in_files.sort()
    in_files_length = len(in_files)
    print('找到的文件总数:{}'.format(in_files_length))

    out_dir = os.path.join(data_root_dir, 'SSIData/FY4A/SSI_{resolution_type}/Area/{frequency}'.format(
        resolution_type=resolution_type, frequency=frequency))

    print('开始生成区域数据')
    print(left_up_lon, left_up_lat, right_down_lon, right_down_lat)
    out_files = []
    p = Pool(thread)
    for in_file in in_files[:]:
        filename = os.path.basename(in_file)
        out_file = os.path.join(out_dir, filename)
        out_files.append(out_file)
        p.apply_async(area, args=(in_file, out_file, left_up_lon, left_up_lat, right_down_lon, right_down_lat,
                                  resolution_type))
    p.close()
    p.join()

    if len(out_files) > 0:
        return out_files
    else:
        return


def product_fy4a_disk_point_data(date_start=None, date_end=None, thread=30, lon=None, lat=None,
                                 resolution_type=None, resultid=None, element=None, idx=None, ck=None):
    lon = float(lon)
    lat = float(lat)
    date_s = datetime.strptime(date_start, '%Y%m%d%H%M%S')
    date_e = datetime.strptime(date_end, '%Y%m%d%H%M%S')
    out_dir = os.path.join(data_root_dir, 'TmpData')
    outname = 'FY4A-_AGRI--_{lon:07.3f}N_DISK_{lat:07.3f}E_L2-_SSI-_MULT_NOM_' \
              '{date_start}_{date_end}_{resolution_type}_V0001.TXT'

    if 'Orbit' in resultid:
        get_datetime = FY4ASSI.get_date_time_orbit
    elif 'Daily' in resultid:
        get_datetime = FY4ASSI.get_date_time_daily
    elif 'Monthly' in resultid:
        get_datetime = FY4ASSI.get_date_time_monthly
    elif 'Yearly' in resultid:
        get_datetime = FY4ASSI.get_date_time_yearly
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

    pre_dist = 0.08
    index = get_point_index(lon, lat, idx, ck, pre_dist)
    print(index)
    if index is None:
        print('没有找到最近点:lon {}   lat:{}'.format(lon, lat))
        return

    datas = []
    dates = []
    values = []
    count = 0
    thread_lock = threading.Lock()
    ts = []
    import time
    s = time.clock()
    for full_file in full_files:
        if not os.path.isfile(full_file):
            print('文件不存在: {}'.format(full_file))
            count += 1
            continue
        t = threading.Thread(target=_get_point_data, args=(full_file, element, index, get_datetime, resultid,
                                                           dates, datas, values, thread_lock))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()
    print(time.clock() - s)
    dates_new = []
    values_new = []
    for date, value in sorted(zip(dates, values), key=lambda x: x[0]):
        dates_new.append(date)
        values_new.append(value)

    out_file = os.path.join(out_dir, outname.format(lon=lon, lat=lat, date_start=date_start,
                                                    date_end=date_end, resolution_type=resolution_type))

    if element is None:
        header = """Date\t{}
""".format(element)
    elif resolution_type == '4KM':
        header = """Date\tItol\tIb\tId
"""
    else:
        header = """Date\tItol\tIb\tId\tG0\tGt\tDNI
"""

    if len(datas) > 0:
        if element is None:
            with open(out_file, 'w') as fp:
                fp.write(header)
                fp.writelines(datas)
            return out_file
        else:
            return {'date': dates_new, 'value': values_new}
    else:
        return


def _get_point_data(full_file, element, index, get_datetime, resultid,
                    dates, datas, values, thread_lock):
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
    if element is not None:
        elements = [element]
    else:
        elements = data_geter.keys()

    for element_ in elements:
        try:
            data_tmp = data_geter[element_]()[index]
        except Exception as why:
            print(why)
            print('读取数据错误:{}'.format(element_))
            continue
        if data_tmp is not None:
            print(datas_tmp)
            if np.isnan(data_tmp):
                datas_tmp[element_] = 0
            else:
                datas_tmp[element_] = data_tmp.item()

    date = get_datetime(full_file)
    if 'Orbit' in resultid:
        date += relativedelta(hours=8)
    date = date.strftime('%Y%m%d%H%M%S')

    if len(datas_tmp) == 1:
        data_str = '{}\t{:0.4f}\n'.format(
            date, datas_tmp[element]
        )
    elif len(datas_tmp) == 3:
        data_str = '{}\t{:0.4f}\t{:0.4f}\t{:0.4f}\n'.format(
            date, datas_tmp['Itol'], datas_tmp['Ib'], datas_tmp['Id']
        )
    elif len(datas_tmp) == 6:
        data_str = '{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
            date, datas_tmp['Itol'], datas_tmp['Ib'], datas_tmp['Id'],
            datas_tmp['G0'], datas_tmp['Gt'], datas_tmp['DNI']
        )
    else:
        return
    with thread_lock:
        dates.append(date)
        datas.append(data_str)
        if datas_tmp.get(element) is not None:
            values.append(datas_tmp[element])


def product_4km_disk_area_image(date_start=None, date_end=None, thread=3, frequency=None, resolution_type=None):
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

    in_dir = os.path.join(data_root_dir, 'SSIData/FY4A/SSI_{resolution_type}/Full/{frequency}'.format(
        resolution_type=resolution_type, frequency=frequency))
    out_dir = os.path.join(data_root_dir, 'SSIData/FY4A/SSI_{resolution_type}/China/{frequency}'.format(
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
    # fy4a_save_source_data_in_database()

    # start = datetime.strptime('20190629000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630235959', '%Y%m%d%H%M%S')
    #
    # start = datetime.strptime('20190629010000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190629010000', '%Y%m%d%H%M%S')

    # start = datetime.strptime('20190201000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190228235959', '%Y%m%d%H%M%S')
    #
    start = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    end = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')

    # =================================全圆盘==================================
    # 轨道：生产数据
    # start = datetime.strptime('20190601000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630235959', '%Y%m%d%H%M%S')
    product_fy4a_4kmcorrect_disk_full_data_orbit(start, end)  # 4KMCorrect
    # start = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630235959', '%Y%m%d%H%M%S')
    # product_fy4a_1km_disk_full_data_orbit(start, end)  # 1KM

    # 轨道：绘图
    # start = datetime.strptime('20190629000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630235959', '%Y%m%d%H%M%S')
    # product_fy4a_disk_full_image_orbit(start, end, resolution_type='4KM')  # 圆盘轨道
    product_fy4a_disk_full_image_orbit(start, end, resolution_type='4KMCorrect')  # 圆盘轨道
    # product_fy4a_disk_full_image_orbit(start, end, resolution_type='1KM')  # 圆盘轨道

    # 日：生产数据和绘图
    # start = datetime.strptime('20190601000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630235959', '%Y%m%d%H%M%S')
    # product_fy4a_disk_full_data_and_image(start, end, frequency='Daily', resolution_type='4KM')  # 圆盘日
    # product_fy4a_disk_full_data_and_image(start, end, frequency='Daily', resolution_type='4KMCorrect')  # 圆盘日
    # product_fy4a_disk_full_data_and_image(start, end, frequency='Daily', resolution_type='1KM')  # 圆盘日

    # 月：生产数据和绘图
    # start = datetime.strptime('20190601000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630235959', '%Y%m%d%H%M%S')
    # product_fy4a_disk_full_data_and_image(start, end, frequency='Monthly', resolution_type='4KM')  # 圆盘月
    # product_fy4a_disk_full_data_and_image(start, end, frequency='Monthly', resolution_type='4KMCorrect')  # 圆盘月
    # product_fy4a_disk_full_data_and_image(start, end, frequency='Monthly', resolution_type='1KM')  # 圆盘月

    # 年：生产数据和绘图
    # product_fy4a_disk_full_data_and_image(start, end, frequency='Yearly', resolution_type='4KM')  # 圆盘年

    # =================================中国区==================================
    # leftuplon = 70
    # leftuplat = 50
    # rightdownlon = 140
    # rightdownlat = 0
    # product_fy4a_disk_area_data(start, end, resolution_type='4KM', resultid='FY4A_AGRI_L2_SSI_Orbit',
    #                             left_up_lon=leftuplon, left_up_lat=leftuplat,
    #                             right_down_lon=rightdownlon, right_down_lat=rightdownlat)  # 区域轨道
    # product_fy4a_disk_area_data(start, end, frequency='Daily', resolution_type='4KM',
    #                             left_up_lon=leftuplon, left_up_lat=leftuplat,
    #                             right_down_lon=rightdownlon, right_down_lat=rightdownlat)  # 中国区日
    # product_fy4a_disk_area_data(start, end, frequency='Monthly', resolution_type='4KM',
    #                             left_up_lon=leftuplon, left_up_lat=leftuplat,
    #                             right_down_lon=rightdownlon, right_down_lat=rightdownlat)  # 中国区月
    # product_fy4a_disk_area_data(start, end, frequency='Yearly', resolution_type='4KM',
    #                             left_up_lon=leftuplon, left_up_lat=leftuplat,
    #                             right_down_lon=rightdownlon, right_down_lat=rightdownlat)  # 中国区年
