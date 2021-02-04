#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/10/15 11:00
# @Author  : AnNing
import os

# 是否开启DEBUG模式
DEBUG = False

# 数据根目录
DATA_ROOT_DIR = '/DISK/DATA03/KTS_WEBRUN/gfssi/GFData'

# SSI原始数据存放目录
DATA_SOURCE_DIR = os.path.join(DATA_ROOT_DIR, 'SourceData')

# 站点数据目录
DATA_OBS_DIR = os.path.join(DATA_SOURCE_DIR, 'OBS')

# 临时文件目录（此目录下的文件定时删除，也可以随时删除）
DATA_TMP_DIR = os.path.join(DATA_ROOT_DIR, 'TmpData')

# 数据库
DATABASE_URL = 'mysql+pymysql://root:root@cma07@222.128.59.164:3386/solar'
# DATABASE_URL = 'mysql+pymysql://root:gfssi@localhost:3306/solar'

# 补数据使用的并行数量
THREAD = 3
