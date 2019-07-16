#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/10/15
@Author  : AnNing
"""
import os


CURRENT_FILE = os.path.realpath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE)
GSICS_DIR = os.path.dirname(CURRENT_DIR)


def get_cross_cfg_path():
    """
    获取gsics cfg目录的路径
    :return:
    """
    return os.path.join(GSICS_DIR, 'mod_cross', 'cfg')
