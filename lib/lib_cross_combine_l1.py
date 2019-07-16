# -*- coding: utf-8 -*-

import gc
import sys

import h5py

from DP.dp_2d import rolling_2d_window_pro
from PB import DRC as drc
import numpy as np


__description__ = u'静止和极轨通用匹配程序'
__author__ = 'wangpeng'
__date__ = '2018-09-06'
__version__ = '1.0.0_beat'

high_spec_sensor = ['IASI', 'CRIS', 'HIRAS', 'AIRS']


class CombineL1File():

    def __init__(self, in_file, sensor):
        drc = eval('drc.Read%sL1' % sensor)(in_file)

    def combine_all_var(self):
        pass


if __name__ == '__main__':
    idx = np.arange(0, 100)
    i2, j2 = np.unravel_index(idx, (10, 10))
    print i2, j2
    print i2.shape
    c = np.full((4, ), 100)
    a = np.array([11, 12, 13, 14])
    b = np.array([0, 13, 14, 15])
    idx = b < a
    print idx
    print c
    c[idx] = a[idx]
    print c
    dict_a = {}
    dict_a[1] = [a, b]
    print len(dict_a[1])

    d = np.full((3, 3), 9)

    print d.shape
    d = d.reshape(-1)
    print d.shape
