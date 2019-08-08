#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/1
@Author  : AnNing
"""
from dateutil.relativedelta import relativedelta
import re
import os
import sys

from configobj import ConfigObj
from PB.CSC.pb_csc_console import SocketServer
from PB.CSC.pb_csc_crontrol import *

# 获取程序所在目录位置
g_path, _ = os.path.split(os.path.realpath(__file__))
# 进入该目录
os.chdir(g_path)


def date2ymdhms(date):
    return date.strftime('%Y%m%d%H%M%S')


def get_files_by_date(dir_path, time_start, time_end, ext=None, pattern=None):
    """
    :param dir_path: 文件夹
    :param time_start: 开始时间
    :param time_end: 结束时间
    :param ext: 后缀名, '.hdf5'
    :param pattern: 匹配时间的模式, 可以是 r".*(\d{8})_(\d{4})_"
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


def job_01(date_start=None, date_end=None):
    """
    绘制原始4KM数据的图像
    3个产品，每个产品2张图像，共6张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :return:
    """
    from gfssi_e01_ssi_plot_map_orbit import plot_map_orbit
    in_dir = '/home/gfssi/GFData/SSIData/FY4A/SSI_4KM/Full/Orbit'
    date_end_str = date2ymdhms(date_end)
    pattern = r'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_(\d{14})_\d{14}_4000M_V0001.NC'
    in_files = []
    while date_start <= date_end:
        ymd = date_start.strftime('%Y%m%d')
        in_dir_tem = os.path.join(in_dir, ymd)
        date_start_str = date2ymdhms(date_start)
        in_files_tem = get_files_by_date(in_dir_tem, date_start_str, date_end_str, ext='.NC', pattern=pattern)
        in_files.extend(in_files_tem)
        date_start += relativedelta(days=1)
    in_files_length = len(in_files)
    print('找到的文件总数:{}'.format(in_files_length))
    p = Pool(4)
    for in_file in in_files:
        p.apply_async(plot_map_orbit, args=(in_file, '4km'))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def job_02(date_start=None, date_end=None):
    """
    4KM数据日合成
    绘制原始4KM数据的图像
    3个产品，每个产品2张图像，共6张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :return:
    """
    from gfssi_e02_ssi_combine import combine
    in_dir = '/home/gfssi/GFData/SSIData/FY4A/SSI_4KM/Full/Orbit'

    out_dir = '/home/gfssi/GFData/SSIData/FY4A/SSI_4KM/Full/Daily/'
    out_name = 'FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_{ymd}_4000M_V0001.NC'

    in_files_all = []
    while date_start <= date_end:
        ymd = date_start.strftime('%Y%m%d')
        in_dir_tem = os.path.join(in_dir, ymd)
        filenames = os.listdir(in_dir_tem)
        in_files_tem = [os.path.join(in_dir_tem, i) for i in filenames if os.path.splitext(i)[1].lower() == '.nc']
        out_file = os.path.join(out_dir, ymd[:6], out_name.format(ymd=ymd))
        in_files_all.append((in_files_tem, out_file))
        date_start += relativedelta(days=1)

    p = Pool(4)
    for in_files, out_file in in_files_all:
        in_files_length = len(in_files)
        print('找到的文件总数:{}'.format(in_files_length))
        p.apply_async(combine, args=(in_files, out_file, True))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def job_03(date_start=None, date_end=None):
    """
    4KM数据月合成
    绘制原始4KM数据的图像
    3个产品，每个产品2张图像，共6张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :return:
    """
    from gfssi_e02_ssi_combine import combine
    in_dir = '/home/gfssi/GFData/SSIData/FY4A/SSI_4KM/Full/Daily'

    out_dir = '/home/gfssi/GFData/SSIData/FY4A/SSI_4KM/Full/Monthly/'
    out_name = 'FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_{ym}_4000M_V0001.NC'

    in_files_all = []
    while date_start <= date_end:
        ym = date_start.strftime('%Y%m')
        in_dir_tem = os.path.join(in_dir, ym)
        filenames = os.listdir(in_dir_tem)
        in_files_tem = [os.path.join(in_dir_tem, i) for i in filenames if os.path.splitext(i)[1].lower() == '.nc']
        out_file = os.path.join(out_dir, ym[:4], out_name.format(ym=ym))
        in_files_all.append((in_files_tem, out_file))
        date_start += relativedelta(months=1)

    p = Pool(4)
    for in_files, out_file in in_files_all:
        in_files_length = len(in_files)
        print('找到的文件总数:{}'.format(in_files_length))
        p.apply_async(combine, args=(in_files, out_file, True))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def job_04(date_start=None, date_end=None):
    """
    4KM数据年合成
    绘制原始4KM数据的图像
    3个产品，每个产品2张图像，共6张图像
    :param date_start: 开始日期 datetime
    :param date_end: 结束日期 datetime
    :return:
    """
    from gfssi_e02_ssi_combine import combine
    in_dir = '/home/gfssi/GFData/SSIData/FY4A/SSI_4KM/Full/Monthly'

    out_dir = '/home/gfssi/GFData/SSIData/FY4A/SSI_4KM/Full/Yearly/'
    out_name = 'FY4A-_AGRI--_N_DISK_1047E_L3-_SSI-_MULT_NOM_{y}_4000M_V0001.NC'

    in_files_all = []
    while date_start <= date_end:
        y = date_start.strftime('%Y')
        in_dir_tem = os.path.join(in_dir, y)
        filenames = os.listdir(in_dir_tem)
        in_files_tem = [os.path.join(in_dir_tem, i) for i in filenames if os.path.splitext(i)[1].lower() == '.nc']
        out_file = os.path.join(out_dir, out_name.format(y=y))
        in_files_all.append((in_files_tem, out_file))
        date_start += relativedelta(years=1)

    p = Pool(4)
    for in_files, out_file in in_files_all:
        in_files_length = len(in_files)
        print('找到的文件总数:{}'.format(in_files_length))
        p.apply_async(combine, args=(in_files, out_file, True))
    p.close()
    p.join()
    print('完成全部的任务:{}'.format(sys._getframe().f_code.co_name))


def get_job_id_func(job_id):
    """
    u 返回jobid对应的函数名称 ，jobid唯一性
    :return:
    """
    job_id_func = {
        "job_0110": job_0110,
        "job_0210": job_0210,
    }
    return job_id_func.get(job_id)


def main():
    # 获取必要的三个参数(卫星对，作业编号，日期范围 , 端口, 线程)
    job_name, job_step, job_time, job_cfg, job_port, threads, histdays = get_args()
    # 端口大于0 就开启
    if job_port > 0:
        sserver = SocketServer()
        if sserver.createSocket(job_port) is False:
            sserver.closeSocket(job_port)
            sys.exit(-1)

    # 读取模块配置文件内容
    job_cfg = ConfigObj(job_cfg)

    # 覆盖接口文件标记
    run_jobs = job_cfg['CROND']['run_jobs'].lower()
    run_mode = job_cfg['CROND']['run_mode']
    interface = job_cfg['PATH']['OUT']['interface']

    # 1 获取卫星对清单
    job_name_list = get_job_name_list(job_name, job_cfg)
    # 2 获取作业流清单
    job_step_list = get_job_step_list(job_name_list, job_step, job_cfg)
    # 3 获取日期的清单
    job_time_list = get_job_time_list(job_name_list, job_time, job_cfg)

    #  开始根据卫星对处理作业流
    for job_name in job_name_list:  # 卫星对
        for job_id in job_step_list[job_name]:  # 作业编号
            process_name = job_cfg['BAND_JOB_MODE'][job_id]  # 作业进程
            for date_s, date_e in job_time_list[job_name]:  # 处理时间
                get_job_id_func(job_id)(job_name, job_id, date_s, date_e, job_cfg, threads)

    # 开始获取执行指令信息
    if 'on' in run_jobs:
        for job_name in job_name_list:  # 卫星对
            for job_id in job_step_list[job_name]:  # 作业编号
                process_name = job_cfg['BAND_JOB_MODE'][job_id]  # 作业进程
                for date_s, date_e in job_time_list[job_name]:  # 处理时间
                    cmd_list = get_cmd_list(process_name, job_name, job_id, date_s, date_e, interface)

                    if 'onenode' in run_mode:
                        run_command(cmd_list, threads)
                    elif 'cluster' in run_mode:
                        run_command_parallel(cmd_list)
                    else:
                        print('error: parallel_mode args input onenode or cluster')
                        sys.exit(-1)
    else:
        print('run jobs off...')


if __name__ == '__main__':
    # start = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630005959', '%Y%m%d%H%M%S')
    # job_01(start, end)
    # start = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    # job_02(start, end)
    # start = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    # end = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    # job_03(start, end)
    start = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    end = datetime.strptime('20190630000000', '%Y%m%d%H%M%S')
    job_04(start, end)
