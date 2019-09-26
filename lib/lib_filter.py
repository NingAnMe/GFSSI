#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/10/17
@Author  : AnNing
"""
import numpy as np

from PB.pb_time import is_day_timestamp_and_lon


def filter_data_by_delta_sigma(x, y, w=None, n=8):
    """
    过滤正负 delta + n 倍的 std 的杂点
    :param x:
    :param y:
    :param w:
    :param n:
    :return:
    """
    c = np.polyfit(x, y, 1, w=w)
    k1 = c[0]
    k0 = c[1]
    regression_line = x * k1 + k0

    delta = np.abs(y - regression_line)
    delta_mean = np.nanmean(delta)
    delta_std = np.nanstd(delta)

    y_max = regression_line + delta_mean + delta_std * n
    y_min = regression_line - delta_mean - delta_std * n

    index = np.logical_and(y < y_max, y > y_min)

    return index


def filter_data_by_time(data, timestamp, longitude, time):
    index = get_time_index_by_timestamp_longitude(timestamp, longitude, time)
    if isinstance(data, dict):
        for k, d in data.items():
            data[k] = d[index]
    else:
        data = data[index]
    return data


def get_time_index_by_sun_zenith(zenith, time):
    """
    获取白天 晚上 全量的索引
    zenith >= 90是晚上，zenith < 90是白天
    :param zenith:
    :param time: day night all
    :return:
    """
    time = time.lower()
    if time == 'all':
        index = np.where(zenith)
    elif time == 'day':
        index = np.where(zenith < 90)
    elif time == 'night':
        index = np.where(zenith >= 90)
    else:
        raise KeyError('{} can not be handled.'.format(time))
    return index


def get_time_index_by_timestamp_longitude(timestamp, longitude, time):
    """
    获取白天 晚上 全量的索引
    :param timestamp:
    :param longitude:
    :param time: day night all
    :return:
    """
    time = time.lower()
    vectorize_is_day = np.vectorize(is_day_timestamp_and_lon)
    if time == 'all':
        index = np.where(timestamp)
    elif time == 'day':
        index = vectorize_is_day(timestamp, longitude)
    elif time == 'night':
        index = np.logical_not(vectorize_is_day(timestamp, longitude))
    else:
        raise KeyError('{} can not be handled.'.format(time))
    return index


def has_empty_data_or_not_equal_length(datas):

    length = set()

    for data in datas:
        if not data:
            return True
        else:
            length.add(len(data))

    if len(length) > 1:
        return True

    return False
