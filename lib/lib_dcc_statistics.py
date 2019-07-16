#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/6/22 16:15
@Author  : AnNing
"""
import numpy as np


def nanmode(data, bins_count=200):
    """
    :return:
    """
    mode = np.NaN
    if data is not None and len(data) != 0:
        data_min = np.nanmin(data)
        data_max = np.nanmax(data)
        bins = np.linspace(int(data_min), int(data_max), bins_count, endpoint=True)
        hist, bin_edges = np.histogram(data, bins=bins)
        idx = np.argmax(hist)
        mode = (bin_edges[idx] + bin_edges[idx + 1]) / 2.
    return mode
