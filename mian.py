#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/1
@Author  : AnNing
"""
import os
import sys


# -*- coding: utf-8 -*-

from configobj import ConfigObj
from PB.CSC.pb_csc_console import SocketServer
from PB.CSC.pb_csc_crontrol import *

# 获取程序所在目录位置
g_path, _ = os.path.split(os.path.realpath(__file__))
# 进入该目录
os.chdir(g_path)


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
