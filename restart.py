#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/12/13 17:54
# @Author  : NingAnMe <ninganme@qq.com>
import os

keys = ["soloarTask", "restful", "download_cimiss"]

print("！！！！     ： 开始终止程序")
for key in keys:
    cmd = "ps -ef| grep gfssi | grep {}".format(key)
    r = os.popen(cmd).readlines()
    for line in r[:-2]:
        print(line)
        pid = line.split()[1]
        r = os.popen("kill -9 {}".format(pid))
        print("kill -9 {}".format(pid))

print("！！！！     ： 开始启动程序")
cmds = [
    "/home/gfssi/business/jetty-distribution-9.2.9.v20150224/bin/jetty.sh restart",  # 重启web
    "nohup java -jar /home/gfssi/business/tool/soloarTask-1.0-SNAPSHOT.jar > /GFData/TmpData/soloarTask.log 2>&1 &",  # 重启实时业务
    "nohup python /home/gfssi/Project/OM/gfssi/restful.py > /GFData/TmpData/restful.log 2>&1 &"  # 重启网站功能
    "nohup python /home/gfssi/Project/OM/gfssi/download_cimiss.py > /GFData/TmpData/download_cimiss.log 2>&1 &"  # 重启网站功能
]
for cmd in cmds:
    print(cmd)
    os.system(cmd)
