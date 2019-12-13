#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/9/19 12:01
# @Author  : AnNing

# 参考
# https://matplotlib.org/3.1.1/tutorials/colors/colorbar_only.html

import matplotlib.pyplot as plt
import matplotlib as mpl
from lib_constant import *

aid_path = get_aid_path()

kwargs = {
    'Orbit_FY4A': COLORBAR_RANGE_ORBIT_FY4A,
    'Daily_FY4A': COLORBAR_RANGE_DAILY_FY4A,
    'Monthly_FY4A': COLORBAR_RANGE_MONTHLY_FY4A,
    'Yearly_FY4A': COLORBAR_RANGE_YEARLY_FY4A,
    'Daily_FY3D': COLORBAR_RANGE_DAILY_FY3D,
    'Monthly_FY3D': COLORBAR_RANGE_MONTHLY_FY3D,
    'Yearly_FY3D': COLORBAR_RANGE_YEARLY_FY3D,
}

# for k, r in kwargs.items():
#     fig, ax = plt.subplots(figsize=(1, 8))
#     fig.subplots_adjust(right=0.5)
#     cmap = plt.get_cmap('jet')
#     vmin, vmax = r
#     orientation = 'vertical'
#     # orientation = 'horizontal'
#     norm = plt.Normalize(vmin=vmin, vmax=vmax)
#     cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap,
#                                     norm=norm,
#                                     orientation=orientation)
#     # cb1.set_label('Kwh/m^2')
#     plt.tight_layout()
#     alpha = 0
#     fig.patch.set_alpha(alpha)
#     fig.savefig(os.path.join(aid_path, 'colormap_{}.png'.format(k)))


for k, r in kwargs.items():
    fig, ax = plt.subplots(figsize=(8, 1), dpi=1000)
    fig.subplots_adjust(bottom=0.5)
    cmap = plt.get_cmap('jet')
    vmin, vmax, label = r
    # orientation = 'vertical'
    orientation = 'horizontal'
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap,
                                    norm=norm,
                                    orientation=orientation)
    cb1.ax.tick_params(labelsize=16)
    font = {'family': 'serif',
            'weight': 'normal',
            'size': 16,
            }
    cb1.set_label(label, fontdict=font)
    plt.tight_layout()
    alpha = 0
    fig.patch.set_alpha(alpha)
    fig.savefig(os.path.join(aid_path, 'colormap_{}.png'.format(k)), dpi=1000)
