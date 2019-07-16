#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/9/20
@Author  : AnNing
"""
import numpy as np

from DP.dp_prj import prj_core, deg2meter


def create_lookup_table(resolution, shape):
    """
    根据分辨率创建查找表
    :return:
    """
    half_res = deg2meter(resolution)/2.
    proj_str = ("+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 "
                "+datum=WGS84 +x_0=-{res} +y_0={res}".format(**{'res': half_res})
                )

    row, col = shape
    lookup_table = prj_core(proj_str, resolution, unit='deg', row=row, col=col)
    return lookup_table


def count_ij_number(latitude, longitude, ij_count, lookup_table, shape):
    """
    计算行列号数量
    :return:
    """
    row, col = shape
    ii, jj = lookup_table.lonslats2ij(longitude, latitude)
    condition = np.logical_and.reduce((ii >= 0, ii < row,
                                       jj >= 0, jj < col))

    ii = ii[condition]
    jj = jj[condition]

    for ij in zip(ii, jj):
        ij_count[ij] = ij_count.get(ij, 0) + 1


def ij_count_to_ndarray(ij_count, shape):
    """
    字典转多维矩阵
    :param ij_count:
    :param shape:
    :return:
    """
    count = np.zeros(shape, dtype=np.float16)

    for ij, value in ij_count.iteritems():
        i, j = ij
        count[i, j] = value

    invalid_index = np.where(count == 0)
    count[invalid_index] = np.nan

    return count
