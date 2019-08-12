#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/10/11
@Author  : AnNing
"""
import os


CURRENT_FILE = os.path.realpath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE)
GFSSI_DIR = os.path.dirname(CURRENT_DIR)


def get_cfg_path():
    """
    获取gfssi cfg目录的路径
    :return:
    """
    return os.path.join(GFSSI_DIR, 'cfg')


def get_lib_path():
    """
    获取gfssi lib目录的路径
    :return:
    """
    return os.path.join(GFSSI_DIR, 'lib')


def get_aid_path():
    """
    获取gfssi Aid目录的路径
    :return:
    """
    return os.path.join(GFSSI_DIR, 'Aid')
