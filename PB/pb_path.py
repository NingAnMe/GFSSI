#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/3
@Author  : AnNing
"""
import os


g_main_path, g_main_file = os.path.split(os.path.realpath(__file__))


def get_pb_path():
    return g_main_path
