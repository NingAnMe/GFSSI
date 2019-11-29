#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/11/29 10:45
# @Author  : NingAnMe <ninganme@qq.com>
import os
from shutil import copyfile


in_date = '20171013'
out_date = '20190605'

in_dir = '/home/gfssi/GFData/SourceData/OBS/{}'.format(in_date)
out_dir = '/home/gfssi/GFData/SourceData/OBS/{}'.format(out_date)

if not os.path.isdir(out_dir):
    os.makedirs(out_dir)

for r, ds, fs, in os.walk(in_dir):
    for f in fs:
        s_f = os.path.join(r, f)
        d_f = os.path.join(out_dir, f.replace(in_date, out_date))
        copyfile(s_f, d_f)
        print(d_f)
