#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/12/13 17:54
# @Author  : NingAnMe <ninganme@qq.com>
"""
2020-05-15: 使用DATA_TMP_DIR代替绝对路径
"""
import os
from config import DATA_TMP_DIR

keys = ["soloarTask", "restful", "download_cimiss.py"]

print("！！！！     ： 开始终止程序")
for key in keys:
    cmd = "ps -ef| grep gfssi | grep {}".format(key)
    r = os.popen(cmd).readlines()
    for line in r:
        if 'grep' not in line:
            print(line)
            pid = line.split()[1]
            r = os.popen("kill -9 {}".format(pid))
            print("kill -9 {}".format(pid))
            print("===" * 10)

print("！！！！     ： 开始启动程序")
cmds = [
    "/home/gfssi/business/jetty-distribution-9.2.9.v20150224/bin/jetty.sh restart",  # 重启web
    "nohup java -jar /home/gfssi/business/tool/soloarTask-1.0-SNAPSHOT.jar > {}/soloarTask.log 2>&1 &".format(DATA_TMP_DIR),  # 重启实时业务
    "nohup python /home/gfssi/Project/OM/gfssi/restful.py > {}/restful.log 2>&1 &".format(DATA_TMP_DIR),  # 重启网站功能
    "nohup python /home/gfssi/Project/OM/gfssi/download_cimiss.py > {}/download_cimiss.log 2>&1 &".format(DATA_TMP_DIR)  # 重启网站功能
]
for cmd in cmds:
    print(cmd)
    os.system(cmd)
    print("===" * 10)
