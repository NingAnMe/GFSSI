#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/10/17
@Author  : AnNing
"""
import numpy as np
from datetime import datetime


def bias_information(x, y, boundary=None, range_rate=1.0):
    """
    # 过滤 range%10 范围的值，计算偏差信息
    # MeanBias( <= 10 % Range) = MD±Std @ MT
    # MeanBias( > 10 % Range) = MD±Std @ MT
    :param range_rate:
    :param x:
    :param y:
    :param boundary:
    :return: MD Std MT 偏差均值 偏差 std 样本均值
    """
    bias_info = {}

    if boundary is None:
        return bias_info
    # 计算偏差
    delta = x - y

    # 筛选大于界限值的数据
    idx_greater = np.where(x > boundary)
    delta_greater = delta[idx_greater]
    x_greater = x[idx_greater]
    # 筛选小于界限值的数据
    idx_lower = np.where(x <= boundary)
    delta_lower = delta[idx_lower]
    x_lower = x[idx_lower]

    # 计算偏差均值，偏差 std 和 样本均值
    md_greater = np.nanmean(delta_greater)  # 偏差均值
    std_greater = np.nanstd(delta_greater)  # 偏差 std
    mt_greater = np.nanmean(x_greater)  # 样本均值

    md_lower = np.nanmean(delta_lower)
    std_lower = np.nanstd(delta_lower)
    mt_lower = np.nanmean(x_lower)

    # 格式化数据
    info_lower = "MeanBias(<={:d}%Range)={:.4f}±{:.4f}@{:.4f}".format(
        int(range_rate * 100), md_lower, std_lower, mt_lower)
    info_greater = "MeanBias(>{:d}%Range) ={:.4f}±{:.4f}@{:.4f}".format(
        int(range_rate * 100), md_greater, std_greater, mt_greater)

    bias_info = {"md_greater": md_greater, "std_greater": std_greater,
                 "mt_greater": mt_greater,
                 "md_lower": md_lower, "std_lower": std_lower,
                 "mt_lower": mt_lower,
                 "info_lower": info_lower, "info_greater": info_greater}

    return bias_info


def get_abr(x, y, w):
    """
    获取 slope intercept count corrcoef
    :param x:
    :param y:
    :param w:
    :return:
    """
    # 计算回归系数
    p = np.polyfit(x, y, 1, w=w)
    k1, k0 = p[0], p[1]

    # 计算相关度
    r = np.corrcoef(x, y)
    rr = r[0, 1] * r[0, 1]

    return k1, k0, rr


def timestamp2hour(timestamp):
    """
    :param timestamp: (list_like)
    :return:
    """
    date = map(datetime.utcfromtimestamp, timestamp)
    hour = [d.hour for d in date]
    minute = [d.minute for d in date]
    minute = np.divide(minute, 60.)
    hours = np.add(hour, minute)
    return hours


def ymd2timestamp(ymd):
    """
    :param ymd: (str) or (list)
    :return:
    """
    if isinstance(ymd, str):
        date = datetime.strptime(ymd, '%Y%m%d')
        timestamp = (date - datetime(1970, 1, 1, 0, 0, 0)).total_seconds()
    else:
        timestamp = map(ymd2timestamp, ymd)
    return timestamp
