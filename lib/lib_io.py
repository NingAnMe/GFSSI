#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/10/11 11:53
# @Author  : AnNing
import os
import re


def get_files_by_date(dir_path, time_start=None, time_end=None, ext=None, pattern=None):
    """
    :param dir_path: 文件夹
    :param time_start: 开始时间
    :param time_end: 结束时间
    :param ext: 后缀名, '.hdf5'
    :param pattern: 匹配时间的模式
    :return: list
    """
    files_found = []

    for root, dirs, files in os.walk(dir_path):
        for file_name in files:
            if ext is not None:
                if '.' not in ext:
                    ext = '.' + ext
                if os.path.splitext(file_name)[1].lower() != ext.lower():
                    continue
            if pattern is not None:
                re_result = re.match(pattern, file_name)
                if re_result is None:
                    continue
                if time_start is not None:
                    time_file = ''.join(re_result.groups())
                    if not int(time_start) <= int(time_file) <= int(time_end):
                        continue
            files_found.append(os.path.join(root, file_name))
    files_found.sort()
    return files_found
