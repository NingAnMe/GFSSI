#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/8/29 10:43
@Author  : AnNing
"""
import os
from datetime import datetime

import numpy as np

from DV.dv_plot import plt, PlotAx
from PB.pb_io import make_sure_path_exists
from lib.lib_gsics_plot_core import (STYLE_PATH, REGRESSION_ANNOTATE_COLOR,
                                     REGRESSION_ANNOTATE_SIZE, TITLE_FONT, BOTTOM_FONT, BLUE,
                                     RED, ORG_NAME)

DEBUG = False
TIME_TEST = False


def plot_regression(
        line_data_x1=None,
        line_data_y1=None,
        line_data_x2=None,
        line_data_y2=None,
        scatter_data_x=None,
        scatter_data_y=None,
        scatter_label=None,
        scatter_color=None,
        out_file=None,
        title=None,
        x_label=None,
        y_label=None,
        x_range=None,
        y_range=None,
        x_interval=None,
        y_interval=None,
        ymd_start=None,
        ymd_end=None,
        ymd=None,
        annotate=None,):
    style_file_path = STYLE_PATH
    style_file = os.path.join(style_file_path, 'plot_regression.mplstyle')
    plt.style.use(style_file)
    fig = plt.figure(figsize=(5, 5))

    ax1 = plt.subplot2grid((1, 1), (0, 0))
    # 绘制6sv模拟数据回归线
    ax1.plot(line_data_x1, line_data_y1, '-', color='r', linewidth=1.2, zorder=90)
    # 绘制业务数据回归线
    ax1.plot(line_data_x2, line_data_y2, '--', color='k', linewidth=1.2, zorder=80)

    size = 6
    alpha = 1  # 透明度
    marker = "o"  # 形状
    for data_x, data_y, color, label in zip(scatter_data_x, scatter_data_y, scatter_color,
                                            scatter_label):
        ax1.scatter(data_x, data_y, s=size, marker=marker, c=color, lw=0, alpha=alpha, label=label,
                    zorder=100)
    ax1.legend(loc=4, frameon=True)

    plot_ax = PlotAx()
    # ##### 格式化图片
    format_kwargs = {}

    if x_range is not None:
        format_kwargs['x_axis_min'] = x_range[0]
        format_kwargs['x_axis_max'] = x_range[1]
    if y_range is not None:
        format_kwargs['y_axis_min'] = y_range[0]
        format_kwargs['y_axis_max'] = y_range[1]
    if x_label is not None:
        format_kwargs['x_label'] = x_label
    if y_label is not None:
        format_kwargs['y_label'] = y_label
    if x_interval is not None:
        x_major_count = (x_range[1] - x_range[0]) / x_interval + 1
        format_kwargs['x_major_count'] = x_major_count
        if x_major_count <= 11:
            x_minor_count = 4
        else:
            x_minor_count = 1
        format_kwargs['x_minor_count'] = x_minor_count
    if y_interval is not None:
        y_major_count = (y_range[1] - y_range[0]) / y_interval + 1
        format_kwargs['y_major_count'] = y_major_count
        if y_major_count <= 11:
            y_minor_count = 4
        else:
            y_minor_count = 1
        format_kwargs['y_minor_count'] = y_minor_count
    if annotate is not None:
        format_kwargs['annotate'] = annotate
        format_kwargs['annotate_color'] = REGRESSION_ANNOTATE_COLOR
        format_kwargs['annotate_font_size'] = REGRESSION_ANNOTATE_SIZE

    plot_ax.format_ax(ax1, **format_kwargs)

    # ##### 标题和底部文字
    plt.tight_layout()
    fig.suptitle(title, y=0.96, ha='center', fontproperties=TITLE_FONT)
    fig.subplots_adjust(bottom=0.15, top=0.85)

    if ymd_start and ymd_end:
        fig.text(0.5, 0.02, '%s-%s' % (ymd_start, ymd_end), fontproperties=BOTTOM_FONT)
    elif ymd:
        fig.text(0.5, 0.02, '%s' % ymd, fontproperties=BOTTOM_FONT)

    fig.text(0.75, 0.02, ORG_NAME, fontproperties=BOTTOM_FONT)

    # ##### 输出图片
    make_sure_path_exists(os.path.dirname(out_file))
    fig.savefig(out_file, dpi=100)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)


def plot_timeseries_pics(
        data_x=None,
        data_y1=None,
        data_y2=None,
        out_file=None,
        title=None,
        y_label=None,
        x_range=None,
        y_range=None,
        y_interval=None,
        ymd=None,
        ymd_start=None,
        ymd_end=None,
        annotate=None,
        plot_zeroline=True):
    style_path = STYLE_PATH
    style_file = os.path.join(style_path, 'plot_timeseries.mplstyle')
    plt.style.use(style_file)
    fig = plt.figure(figsize=(6, 4))
    ax1 = plt.subplot2grid((1, 1), (0, 0))

    plot_ax = PlotAx()

    # 配置属性
    if x_range is None:
        x_min = datetime.strptime(ymd_start, '%Y%m%d')
        x_max = datetime.strptime(ymd_end, '%Y%m%d')
        x_range = [x_min, x_max]
    elif ymd_start is None or ymd_end is None:
        x_min = np.nanmin(data_x)
        x_max = np.nanmax(data_x)
        x_range = [x_min, x_max]

    # 绘制日数据长时间序列
    plot_ax.plot_time_series(ax1, data_x, data_y1, marker='x', color=BLUE, line_width=None,
                             marker_size=5,
                             marker_edgecolor=BLUE, marker_edgewidth=0.3, alpha=0.8, zorder=80,
                             label="MS")

    plot_ax.plot_time_series(ax1, data_x, data_y2, marker='x', color=RED, line_width=None,
                             marker_size=5,
                             marker_edgecolor=RED, marker_edgewidth=0.3, alpha=0.8, zorder=80,
                             label="oper")
    ax1.legend(loc=2, frameon=True)

    # 绘制 y=0 线配置，在绘制之前设置x轴范围
    if plot_zeroline:
        plot_ax.plot_zero_line(ax1, data_x, x_range)

    format_kwargs = {
        'timeseries': True,
        'tick_font_size': 11,
    }
    if x_range is not None:
        format_kwargs['x_axis_min'] = x_range[0]
        format_kwargs['x_axis_max'] = x_range[1]
    if y_range is not None:
        format_kwargs['y_axis_min'] = y_range[0]
        format_kwargs['y_axis_max'] = y_range[1]
    if y_interval is not None and y_range is not None:
        y_major_count = (y_range[1] - y_range[0]) / y_interval + 1
        format_kwargs['y_major_count'] = y_major_count
        if y_major_count <= 11:
            y_minor_count = 4
        else:
            y_minor_count = 1
        format_kwargs['y_minor_count'] = y_minor_count
    if y_label is not None:
        format_kwargs['y_label'] = y_label
    if annotate is not None:
        format_kwargs['annotate'] = annotate

    plot_ax.format_ax(ax1, **format_kwargs)
    # --------------------
    plt.tight_layout()
    fig.suptitle(title, y=0.96, ha='center', fontproperties=TITLE_FONT)
    if '\n' in title:
        fig.subplots_adjust(bottom=0.2, top=0.82)
    else:
        fig.subplots_adjust(bottom=0.2, top=0.85)

    if ymd_start and ymd_end:
        fig.text(0.50, 0.02, '%s-%s' % (ymd_start, ymd_end), fontproperties=BOTTOM_FONT)
    elif ymd:
        fig.text(0.50, 0.02, '%s' % ymd, fontproperties=BOTTOM_FONT)

    fig.text(0.8, 0.02, ORG_NAME, fontproperties=BOTTOM_FONT)
    # ---------------
    make_sure_path_exists(os.path.dirname(out_file))
    fig.savefig(out_file, dpi=100)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)
