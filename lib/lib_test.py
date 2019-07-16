#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/10/22
@Author  : AnNing
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta

import numpy as np


def get_timeseries_test_data(n=100, ymd_start='20180101'):
    date = []
    date_start = datetime.strptime(ymd_start, '%Y%m%d')
    for i in xrange(n):
        date_tem = date_start + relativedelta(days=i)
        date.append(date_tem)
    data = np.random.randn(n)
    return date, data


def get_statistics_analysis_test_data(n=100):
    x_data = np.random.randn(n)
    y_data = np.random.randn(n) + 1
    return x_data, y_data


if __name__ == '__main__':
    t_date, t_data = get_timeseries_test_data()
    print t_date, len(t_data)
    print t_data, len(t_data)
