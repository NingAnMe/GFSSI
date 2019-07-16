#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/6/8 10:48
@Author  : AnNing
"""
from __future__ import print_function, division

import getopt
import os
import subprocess
import sys
from multiprocessing import Pool

import time
import yaml
from PB import pb_io
from configobj import ConfigObj
from datetime import datetime
from dateutil.relativedelta import relativedelta

# 并行参数，暂时放在这，后期放到配置中
python = 'python2.7 -W ignore'
mpi_run = 'mpirun'
mpi_main = 'mpi.py'
np = 56


def load_yaml_file(in_file):
    with open(in_file, 'r') as stream:
        config_data = yaml.load(stream)
    return config_data


def load_cfg_file(in_file):
    return ConfigObj(in_file)


def usage():
    print(u"""
    -h / --help :使用帮助
    -v / --verson: 显示版本号
    -j / --job : 作业步骤 -j 0110 or --job 0110
    -s / --sat : 卫星信息  -s FY3B+MERSI_AQUA+MODIS or --sat FY3B+MERSI_AQUA+MODIS
    -t / --time :日期   -t 20180101-20180101 or --time 20180101-20180101
    """)


def get_args():
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], "hv:j:s:t:", ["version", "help", "job=", "sat=" "time="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(1)

    for key, val in opts:
        if key in ('-v', '--version'):
            verbose = '1.0.1'
            print('Version: %s' % verbose)
            sys.exit()

        elif key in ("-h", "--help"):
            usage()
            sys.exit()
        elif key in ("-s", "--sat"):
            args_pair = val

        elif key in ("-j", "--job"):
            args_id = val

        elif key in ("-t", "--time"):
            args_date = val
        else:
            assert False, "unhandled option"

    return args_pair, args_id, args_date


def get_pair_list(args_pair, g_var_cfg):
    """
    u 获取参数中的卫星对
    return : list
    """

    if args_pair.lower() == 'all':
        args_pair_list = g_var_cfg['PAIRS'].keys()
    else:
        args_pair_list = args_pair.split(',')
    return args_pair_list


def get_date_list(args_pair_list, args_date, g_var_cfg):
    """
    u 获取参数中的时间范围,args_data 支持all 和 时间范围
    return : dict
    """
    args_date_list = dict()
    cfg_launch_date = g_var_cfg['LAUNCH_DATE']
    cfg_rolldays = g_var_cfg['CROND']['rolldays']

    # 从卫星对清单中获取每个卫星对，进行时间获取
    for pair in args_pair_list:
        # 时间字典的key用卫星对来标记
        short_sat = pair.split('+')[0]
        if pair not in args_date_list:
            args_date_list[pair] = []

        if args_date.lower() == 'all':  # 发星以来的日期
            date_start = cfg_launch_date[short_sat]
            date_end = datetime.utcnow()
            date_start = datetime.strptime(date_start, '%Y%m%d')
            args_date_list[pair].append((date_start, date_end))

        elif args_date.lower() == 'auto':  # 日期滚动
            for rday in cfg_rolldays:
                rd = int(rday)
                date_start = (datetime.utcnow() - relativedelta(days=rd))
                date_end = date_start
                args_date_list[pair].append((date_start, date_end))

        else:  # 手动输入的日期
            date_start, date_end = args_date.split('-')
            date_start = datetime.strptime(date_start, '%Y%m%d')
            date_end = datetime.strptime(date_end, '%Y%m%d')
            args_date_list[pair].append((date_start, date_end))

    return args_date_list


def get_job_id_list(args_pair_list, args_id, g_var_cfg):
    """
    u 获取参数中的作业编号,args_id支持all 和  自定义id(0310,0311)
    return: dict
    """
    args_id_list = dict()

    for pair in args_pair_list:
        if pair not in args_id_list:
            args_id_list[pair] = []
        if args_id.lower() == 'all':  # 自动作业流
            # 若果是all就根据卫星对获取对应的作业流
            job_flow = g_var_cfg['PAIRS'][pair]['job_flow']
            job_flow_def = g_var_cfg['JOB_FLOW_DEF'][job_flow]
            args_id_list[pair] = job_flow_def
        else:  # 手动作业流
            args_id_list[pair] = ['job_%s' % id_ for id_ in args_id.split(',')]

    return args_id_list


def run_command(cmd_list, threads):
    # 开启进程池

    if len(cmd_list) > 0:
        pool = Pool(processes=int(threads))
        for cmd in cmd_list:
            pool.apply_async(command, (cmd,))
        pool.close()
        pool.join()


def command(args_cmd):
    """
    args_cmd: python a.py 20180101  (完整的执行参数)
    """

    print(args_cmd)
    try:
        p1 = subprocess.Popen(args_cmd.split())
    except Exception as e:
        print(e)
        return

    timeout = 3600 * 5
    t_beginning = time.time()

    while p1.poll() is None:

        seconds_passed = time.time() - t_beginning

        if timeout and seconds_passed > timeout:
            print(seconds_passed)
            p1.kill()
        time.sleep(1)
    p1.wait()


def run_command_parallel(arg_list):
    arg_list = [each + '\n' for each in arg_list]
    fp = open('filelist.txt', 'w')
    fp.writelines(arg_list)
    fp.close()

    cmd = '%s -np %d -machinefile hostfile %s %s' % (
        mpi_run, np, python, mpi_main)
    os.system(cmd)


def get_cmd_list(job_exe, sat_pair, job_id, date_s, date_e, g_path_interface):
    cmd_list = []
    while date_s <= date_e:
        ymd = date_s.strftime('%Y%m%d')
        date_s = date_s + relativedelta(days=1)
        path_yaml = os.path.join(g_path_interface, sat_pair, job_id, ymd)
        if os.path.isdir(path_yaml):
            file_list_yaml = pb_io.find_file(path_yaml, '.*.yaml')
            for file_yaml in file_list_yaml:
                cmd = '%s %s %s' % (python, job_exe, file_yaml)
                cmd_list.append(cmd)

    return cmd_list
