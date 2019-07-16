#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/6/28 17:33
@Author  : AnNing
"""
import os

import numpy as np

from PB.pb_io import make_sure_path_exists
from DV import dv_map
from DV.dv_plot import plt, FONT0, PlotAx, get_month_avg_std, mpatches

from lib.lib_gsics_plot_core import ORG_NAME, RED, BLUE, GRAY


def plot_time_series(day_data_x=None, day_data_y=None, plot_month=False,
                     out_file=None, title=None,
                     x_range=None, y_range=None,
                     y_label=None, y_major_count=None, y_minor_count=None,
                     ymd_start=None, ymd_end=None, ymd=None, annotate=None):
    main_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    style_file = os.path.join(main_path, "cfg", 'time_series.mplstyle')
    plt.style.use(style_file)
    fig = plt.figure(figsize=(6, 4))
    ax1 = plt.subplot2grid((1, 1), (0, 0))

    plot_ax = PlotAx()

    # 配置属性
    if x_range is None:
        x_range = [np.nanmin(day_data_x), np.nanmax(day_data_x)]
    x_axis_min = x_range[0]
    x_axis_max = x_range[1]

    # 绘制日数据长时间序列
    plot_ax.plot_time_series(ax1, day_data_x, day_data_y, marker='x', color=BLUE, line_width=None,
                             marker_size=6,
                             marker_edgecolor=BLUE, marker_edgewidth=0.3, alpha=0.8, zorder=100,
                             label="Daily")

    if plot_month:
        month_data_x, month_data_y, month_data_std = get_month_avg_std(day_data_x, day_data_y)

        # 绘制月数据长时间序列
        if month_data_x is not None and month_data_y is not None:
            plot_ax.plot_time_series(ax1, month_data_x, month_data_y, marker='o-', color=RED,
                                     line_width=0.6, marker_size=5,
                                     marker_edgecolor=RED, marker_edgewidth=0, alpha=0.8, zorder=80,
                                     label="Monthly")

            # 绘制背景填充
            if month_data_std is not None:
                plot_ax.plot_background_fill(ax1, x=month_data_x,
                                             y1=month_data_y - month_data_std,
                                             y2=month_data_y + month_data_std,
                                             color=RED,
                                             alpha=0.1,
                                             )
    # 绘制 y=0 线配置，在绘制之间设置x轴范围
    plot_ax.plot_zero_line(ax1, x_axis_min=x_axis_min, x_axis_max=x_axis_max)

    if y_major_count is None:
        y_major_count = 9
    if y_minor_count is None:
        y_minor_count = 1

    format_kwargs = {
        'timeseries': True,
        'y_major_count': y_major_count,
        'y_minor_count': y_minor_count,
    }
    if x_range is not None:
        format_kwargs['x_axis_min'] = x_range[0]
        format_kwargs['x_axis_max'] = x_range[1]
    if y_range is not None:
        format_kwargs['y_axis_min'] = y_range[0]
        format_kwargs['y_axis_max'] = y_range[1]
    if y_label is not None:
        format_kwargs['y_label'] = y_label
    if annotate is not None:
        format_kwargs['annotate'] = annotate

    plot_ax.format_ax(ax1, **format_kwargs)
    # --------------------
    plt.tight_layout()
    fig.suptitle(title, fontsize=11, fontproperties=FONT0)
    fig.subplots_adjust(bottom=0.2, top=0.88)

    if ymd_start and ymd_end:
        circle1 = mpatches.Circle((74, 15), 6, color=BLUE, ec=GRAY, lw=0)
        circle2 = mpatches.Circle((164, 15), 6, color=RED, ec=GRAY, lw=0)
        fig.patches.extend([circle1, circle2])

        fig.text(0.15, 0.02, 'Daily', color=BLUE, fontproperties=FONT0)
        fig.text(0.3, 0.02, 'Monthly', color=RED, fontproperties=FONT0)
        fig.text(0.50, 0.02, '%s-%s' % (ymd_start, ymd_end), fontproperties=FONT0)
    elif ymd:
        fig.text(0.50, 0.02, '%s' % ymd, fontproperties=FONT0)

    fig.text(0.8, 0.02, ORG_NAME, fontproperties=FONT0)
    # ---------------
    make_sure_path_exists(os.path.dirname(out_file))
    fig.savefig(out_file)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)


def plot_map(latitude, longitude,
             count, out_file,
             title=None, ptype=None,
             vmin=None, vmax=None,
             marker=None, markersize=None):
    if title is not None:
        title = title
    else:
        title = "Map"

    if vmin is not None:
        vmin = vmin

    if vmax is not None:
        vmax = vmax

    if marker is not None:
        marker = marker
    else:
        marker = 's'

    if markersize is not None:
        markersize = markersize
    else:
        markersize = 5

    p = dv_map.dv_map()
    p.easyplot(latitude, longitude, count, vmin=vmin, vmax=vmax,
               ptype=ptype, markersize=markersize, marker=marker)
    p.title = title
    p.savefig(out_file)
    print '>>> {}'.format(out_file)


def plot_histogram(out_file=None, data=None,
                   bins_count=200, title=None,
                   x_label=None, y_label=None,
                   x_range=None, y_range=None,
                   hist_label=None, annotate=None,
                   ymd_start=None, ymd_end=None,
                   ymd=None,):
    main_path = os.path.dirname(os.path.dirname(__file__))
    style_file = os.path.join(main_path, "cfg", 'histogram.mplstyle')
    plt.style.use(style_file)
    fig = plt.figure(figsize=(6, 4))

    ax1 = plt.subplot2grid((1, 1), (0, 0))

    ax1.hist(data,
             bins=bins_count,
             range=x_range,
             histtype="bar",
             color='b',
             label=hist_label,
             alpha=1,)
    ax1.legend(loc=1, prop={"size": 10})

    plot_ax = PlotAx()

    format_kwargs = {
        'x_major_count': 11,
        'x_minor_count': 1,
    }

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
    if annotate is not None:
        format_kwargs['annotate'] = annotate

    plot_ax.format_ax(ax1, **format_kwargs)

    # --------------------
    plt.tight_layout()
    fig.suptitle(title, y=0.94, ha='center', fontsize=11, fontproperties=FONT0)
    fig.subplots_adjust(bottom=0.15, top=0.90)

    if ymd_start and ymd_end:
        fig.text(0.50, 0.02, '%s-%s' % (ymd_start, ymd_end), fontproperties=FONT0)
    elif ymd:
        fig.text(0.50, 0.02, '%s' % ymd, fontproperties=FONT0)

    fig.text(0.8, 0.02, ORG_NAME, fontproperties=FONT0)
    # ---------------
    make_sure_path_exists(os.path.dirname(out_file))
    fig.savefig(out_file, dpi=200)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)
