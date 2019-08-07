# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from multiprocessing import Pool

from dateutil.relativedelta import relativedelta

from PB import pb_io

python = 'python -W ignore'
mpi_run = 'mpirun'
mpi_main = 'mpi.py'
cores = 56


def get_args():
    # 输入
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', help='作业名称')
    parser.add_argument('-j', '--job', help='作业步骤')
    parser.add_argument('-t', '--time', help='开始时间-结束时间(yyymmdd)')
    parser.add_argument('-c', '--config', help='配置文件')
    parser.add_argument('-p', '--port', type=int, help='端口大于10000')
    parser.add_argument('-m', '--multiple', type=int, help='进程数量')
    args_ = parser.parse_args()

    name = args_.name
    job = args_.job
    time_ = args_.time
    cfg = args_.config
    port = args_.port
    threads = args_.multiple
    histdays = args_.histdays

    print(name, job, time_, cfg, port, threads, histdays)
    return name, job, time_, cfg, port, threads, histdays


def get_job_name_list(name, g_var_cfg):
    """
    u 获取参数中的作业名称
    return : list
    """

    if name.lower() == 'all':
        job_name_list = list(g_var_cfg['PAIRS'].keys())
    else:
        job_name_list = name.split(',')
    return job_name_list


def get_job_time_list(job_name_list, job_time, g_var_cfg):
    """
    u 获取参数中的时间范围,args_data 支持all 和 时间范围
    return : dict
    """
    job_time_list = dict()
    cfg_rolldays = g_var_cfg['CROND']['rolldays']

    # 从卫星对清单中获取每个卫星对，进行时间获取
    for job_name in job_name_list:
        # 时间字典的key用卫星对来标记
        if job_name not in job_time_list:
            job_time_list[job_name] = []

        if job_time.lower() == 'auto':  # 日期滚动
            for rday in cfg_rolldays:
                rd = int(rday)
                date_start = (datetime.utcnow() - relativedelta(days=rd))
                #                 date_end = datetime.utcnow()
                job_time_list[job_name].append((date_start, date_start))

        else:  # 手动输入的日期
            date_start, date_end = job_time.split('-')
            date_start = datetime.strptime(date_start, '%Y%m%d')
            date_end = datetime.strptime(date_end, '%Y%m%d')
            job_time_list[job_name].append((date_start, date_end))

    return job_time_list


def get_job_step_list(job_name_list, job_id, g_var_cfg):
    """
    u 获取参数中的作业编号,args_id支持all 和  自定义id(0310,0311)
    return: dict
    """
    job_id_list = dict()

    for pair in job_name_list:
        if pair not in job_id_list:
            job_id_list[pair] = []
        if job_id.lower() == 'all':  # 自动作业流
            # 若果是all就根据卫星对获取对应的作业流
            job_flow = g_var_cfg['PAIRS'][pair]['job_flow']
            job_flow_def = g_var_cfg['JOB_FLOW_DEF'][job_flow]
            job_id_list[pair] = job_flow_def
        else:  # 手动作业流
            job_id_list[pair] = ['job_%s' % id_ for id_ in job_id.split(',')]

    return job_id_list


def get_cmd_list(job_exe, job_name, job_id, date_s, date_e, g_path_interface):
    cmd_list = []
    while date_s <= date_e:
        ymd = date_s.strftime('%Y%m%d')
        date_s = date_s + relativedelta(days=1)
        path_yaml = os.path.join(g_path_interface, job_name, job_id, ymd)
        if os.path.isdir(path_yaml):
            file_list_yaml = pb_io.find_file(path_yaml, '.*.yaml')
            for file_yaml in file_list_yaml:
                cmd = '%s %s %s' % (python, job_exe, file_yaml)
                cmd_list.append(cmd)

    return cmd_list


def run_command(cmd_list, threads):
    # 开启进程池
    pool = Pool(processes=int(threads))
    for cmd in cmd_list:
        pool.apply_async(command, (cmd,))

    pool.close()
    pool.join()


def command(cmd):
    """
    args_cmd: python a.py 20180101  (完整的执行参数)
    """
    print(cmd)
    status = False
    try:
        p1 = subprocess.Popen(cmd.split(), stderr=subprocess.PIPE)
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
        time.sleep(0.1)
    _, stderr = p1.communicate()

    if p1.returncode == 0 and stderr is not None:
        status = True

    return status


def run_command_parallel(arg_list):
    arg_list = [each + '\n' for each in arg_list]
    fp = open('filelist.txt', 'w')
    fp.writelines(arg_list)
    fp.close()

    cmd = '%s -np %d -machinefile hostfile %s %s' % (
        mpi_run, cores, python, mpi_main)
    os.system(cmd)


if __name__ == '__main__':
    args = sys.argv[1:]

    get_args()
    pass
