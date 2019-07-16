#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/10/11
@Author  : AnNing
"""
import os


CURRENT_FILE = os.path.realpath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE)
GSICS_DIR = os.path.dirname(CURRENT_DIR)


def get_gsics_cfg_path():
    """
    获取gsics cfg目录的路径
    :return:
    """
    return os.path.join(GSICS_DIR, 'cfg')


def get_gsics_lib_path():
    """
    获取gsics lib目录的路径
    :return:
    """
    return os.path.join(GSICS_DIR, 'lib_gsics')


def get_pics_cfg_path():
    """
    获取mod_pics cfg目录的路径
    :return:
    """
    return os.path.join(GSICS_DIR, 'mod_pics', 'cfg')


def get_proj_cfg_path():
    """
    获取mod_proj cfg目录的路径
    :return:
    """
    return os.path.join(GSICS_DIR, 'mod_proj', 'cfg')


def get_accurate_cfg_path():
    """
    获取mod_accurate cfg目录的路径
    :return:
    """
    return os.path.join(GSICS_DIR, 'mod_acosp', 'cfg')


def get_dcc_cfg_path():
    """
    获取mod_accurate cfg目录的路径
    :return:
    """
    return os.path.join(GSICS_DIR, 'mod_dcc', 'cfg')


def get_stdnc_cfg_path():
    """
    获取mod_accurate cfg目录的路径
    :return:
    """
    return os.path.join(GSICS_DIR, 'mod_stdnc', 'cfg')
