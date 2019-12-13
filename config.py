#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/10/15 11:00
# @Author  : AnNing

# 是否开启DEBUG模式
DEBUG = True

# 数据根目录
DATA_ROOT_DIR = '/home/gfssi/GFData/'

# SSI原始数据存放目录
DATA_SOURCE_DIR = '/home/gfssi/GFData/SourceData'

# 站点数据目录
DATA_OBS_DIR = '/home/gfssi/GFData/SourceData/OBS'

# 临时文件目录（此目录下的文件定时删除，也可以随时删除）
DATA_TMP_DIR = '/home/gfssi/GFData/TmpData'

# 数据库
# DATABASE_URL = 'mysql+pymysql://root:root@cma07@127.0.0.1:3306/solar'
DATABASE_URL = 'mysql+pymysql://root:gfssi@localhost:3306/solar'

# 生产使用的并行数量
THREAD = 10
