#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/10/11
@Author  : AnNing
"""
from datetime import datetime
import os

import numpy as np
from PIL import Image, ImageEnhance

from DV import dv_map
from DV.dv_plt import dv_hist
from DV.dv_plot import (plt, FONT0, PlotAx, PlotFigure, get_month_avg_std, mpatches, Basemap,
                        colorbar, get_bar_data, add_annotate)
from PB.pb_io import make_sure_path_exists
from lib_gsics_path import get_gsics_lib_path


# ########## 绘图常量 ##########
ORG_NAME = 'NSMC-GPRC'  # 没有填None
LOGO_LEFT = os.path.join(get_gsics_lib_path(), 'logoL.jpg')  # 没有填None
LOGO_RIGHT = os.path.join(get_gsics_lib_path(), 'logoR.jpg')  # 没有填None

RED = '#f63240'
BLUE = '#1c56fb'
GRAY = '#c0c0c0'
EDGE_GRAY = '#303030'

LINE_WIDTH = 0.5

TICKER_FONT = FONT0.copy()
TICKER_FONT.set_size(11)

TITLE_FONT = FONT0.copy()
TITLE_FONT.set_size(14)

LABEL_FONT = FONT0.copy()
LABEL_FONT.set_size(12)

BOTTOM_FONT = FONT0.copy()
BOTTOM_FONT.set_size(13)


REGRESSION_ANNOTATE_SIZE = 13
REGRESSION_ANNOTATE_COLOR = 'red'


# ########## 全局常量 ##########
STYLE_PATH = get_gsics_lib_path()


def plot_regression(
        x, y, w=None,
        out_file=None,
        title=None,
        x_label=None,
        y_label=None,
        x_range=None,
        y_range=None,
        x_interval=None,
        y_interval=None,
        annotate=None,
        ymd_start=None,
        ymd_end=None,
        ymd=None,
        density=False, ):
    style_path = STYLE_PATH
    style_file = os.path.join(style_path, 'plot_regression.mplstyle')
    plt.style.use(style_file)
    figsize = (5, 5)
    dpi = 100
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax1 = plt.subplot2grid((1, 1), (0, 0))

    plot_ax = PlotAx()

    # ##### 画散点
    marker_size = 5
    if density:
        marker = 'o'
        alpha = 0.8
        zorder = 90
        plot_ax.plot_density_scatter(ax1, x, y, marker=marker, alpha=alpha, marker_size=marker_size,
                                     zorder=zorder)
    else:
        alpha = 0.8  # 透明度
        marker = "o"  # 形状
        color = "b"  # 颜色
        ax1.scatter(x, y, s=marker_size, marker=marker, c=color, lw=0, alpha=alpha, zorder=90)

    # ##### 画回归线
    color = 'r'
    linewidth = 1.2
    zorder = 80
    plot_ax.plot_regression_line(ax1, x, y, w, x_range, color=color, linewidth=linewidth,
                                 zorder=zorder)

    # ##### 画对角线
    color = '#808080'
    linewidth = 1.2
    zorder = 70
    plot_ax.plot_diagonal_line(ax1, x, y, x_range, y_range, color, linewidth, zorder=zorder)

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

    # ##### 标题 底部文字 LOGO
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.15, top=0.85)

    if '\n' in title:
        title_y = 0.96
    else:
        title_y = 0.94
    fig.suptitle(title, y=title_y, ha='center', fontproperties=TITLE_FONT)

    bottom_text = ''
    bottom_text_l = 0.7
    bottom_text_b = 0.02
    if ymd_start and ymd_end:
        bottom_text = bottom_text + '%s-%s' % (ymd_start, ymd_end)
    elif ymd:
        bottom_text = bottom_text + '%s' % ymd
    if ORG_NAME is not None:
        bottom_text = bottom_text + '   ' + ORG_NAME
    if bottom_text:
        fig.text(bottom_text_l, bottom_text_b, bottom_text, fontproperties=BOTTOM_FONT)

    # # ##### LOGO
    # plot_fig = PlotFigure()
    # img_width = 0.1
    # img_high = float(figsize[0]) / float(figsize[1]) * img_width
    # img_size = (img_width, img_high)
    # if LOGO_LEFT:
    #     plot_fig.add_image(fig, img_size, LOGO_LEFT, position='LB')
    # if LOGO_RIGHT:
    #     plot_fig.add_image(fig, img_size, LOGO_RIGHT, position='RB')

    # ##### 输出图片
    make_sure_path_exists(os.path.dirname(out_file))
    fig.savefig(out_file, dpi=dpi)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)


def plot_regression_3ax(
        x, y, w=None,
        out_file=None,
        title=None,
        x_label1=None,
        y_label1=None,
        x_label2=None,
        y_label2=None,
        x_label3=None,
        y_label3=None,
        x_range1=None,
        y_range1=None,
        x_range2=None,
        y_range2=None,
        x_range3=None,
        y_range3=None,
        x_interval1=None,
        y_interval1=None,
        x_interval2=None,
        y_interval2=None,
        x_interval3=None,
        y_interval3=None,
        annotate1=None,
        annotate2=None,
        annotate3=None,
        ymd_start=None,
        ymd_end=None,
        ymd=None,
        density=False,
        hist_label1=None,
        hist_label2=None,):
    if annotate3 is None:
        annotate3 = {}
    style_path = STYLE_PATH
    style_file = os.path.join(style_path, 'plot_regression.mplstyle')
    plt.style.use(style_file)
    figsize = (15, 5)
    dpi = 100
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax1 = plt.subplot2grid((1, 3), (0, 0))
    ax2 = plt.subplot2grid((1, 3), (0, 1))
    ax3 = plt.subplot2grid((1, 3), (0, 2))

    plot_ax = PlotAx()

    # ##############################  回归图  #################################
    # ##### 画散点
    marker_size = 5
    if density:
        marker = 'o'
        alpha = 0.8
        zorder = 90
        plot_ax.plot_density_scatter(ax1, x, y, marker=marker, alpha=alpha, marker_size=marker_size,
                                     zorder=zorder)
    else:
        alpha = 0.8  # 透明度
        marker = "o"  # 形状
        color = "b"  # 颜色
        ax1.scatter(x, y, s=marker_size, marker=marker, c=color, lw=0, alpha=alpha, zorder=90)

    # ##### 画回归线
    color = 'r'
    linewidth = 1.2
    zorder = 80
    plot_ax.plot_regression_line(ax1, x, y, w, x_range1, color=color, linewidth=linewidth,
                                 zorder=zorder)

    # ##### 画对角线
    color = '#808080'
    linewidth = 1.2
    zorder = 70
    plot_ax.plot_diagonal_line(ax1, x, y, x_range1, y_range1, color, linewidth, zorder=zorder)

    # ##############################  偏差图  #################################
    # ##### 画散点
    alpha = 0.8  # 透明度
    marker = "o"  # 形状
    color = "b"  # 颜色
    bias = x - y
    ax2.scatter(x, bias, s=marker_size, marker=marker, c=color, lw=0, alpha=alpha, zorder=90)

    # ##### 画回归线
    color = 'r'
    linewidth = 1.2
    zorder = 80
    bias = x - y
    plot_ax.plot_regression_line(ax2, x, bias, w, x_range1, color=color, linewidth=linewidth,
                                 zorder=zorder)

    # ##############################  柱状图  #################################
    color1 = 'red'
    color2 = 'blue'
    alpha = 0.6
    bins = 100
    label_font_size = 13

    datas = [x, y]
    colors = [color1, color2]
    hist_labels = [hist_label1, hist_label2]

    if x_range3 is not None:
        x_min, x_max = x_range3
    else:
        x_min, x_max = np.nanmin(x), np.nanmax(x)

    for data, hist_color, hist_label in zip(datas, colors, hist_labels):
        ax3.hist(data, bins, range=(x_min, x_max), histtype="bar",
                 color=hist_color,
                 label=hist_label, alpha=alpha)
    ax3.legend(loc=1, prop={"size": label_font_size})

    # ############################## 格式化图片 #################################
    axs = [ax1, ax2, ax3]
    x_ranges = [x_range1, x_range2, x_range3]
    y_ranges = [y_range1, y_range2, y_range3]
    x_labels = [x_label1, x_label2, x_label3]
    y_labels = [y_label1, y_label2, y_label3]
    x_interval = [x_interval1, x_interval2, x_interval3]
    y_interval = [y_interval1, y_interval2, y_interval3]
    annotates = [annotate1, annotate2, annotate3]
    for ax, x_range, y_range, x_label, y_label, x_interval, y_interval, annotate \
            in zip(axs, x_ranges, y_ranges, x_labels, y_labels, x_interval, y_interval, annotates):
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
        if x_interval is not None and x_range is not None:
            x_major_count = (x_range[1] - x_range[0]) / x_interval + 1
            format_kwargs['x_major_count'] = x_major_count
            if x_major_count <= 11:
                x_minor_count = 4
            else:
                x_minor_count = 1
            format_kwargs['x_minor_count'] = x_minor_count
        if y_interval is not None and y_range is not None:
            y_major_count = (y_range[1] - y_range[0]) / y_interval + 1
            format_kwargs['y_major_count'] = y_major_count
            if y_major_count <= 11:
                y_minor_count = 4
            else:
                y_minor_count = 1
            format_kwargs['y_minor_count'] = y_minor_count
        if annotate is not None:
            format_kwargs['annotate'] = annotate
            format_kwargs['annotate_font_color'] = REGRESSION_ANNOTATE_COLOR
            format_kwargs['annotate_font_size'] = REGRESSION_ANNOTATE_SIZE

        plot_ax.format_ax(ax, **format_kwargs)

    # ##### 标题和底部文字
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.15, top=0.85)

    if '\n' in title:
        title_y = 0.96
    else:
        title_y = 0.94
    fig.suptitle(title, y=title_y, ha='center', fontproperties=TITLE_FONT)

    if ymd_start and ymd_end:
        fig.text(0.65, 0.02, '%s-%s' % (ymd_start, ymd_end), fontproperties=BOTTOM_FONT)
    elif ymd:
        fig.text(0.65, 0.02, '%s' % ymd, fontproperties=BOTTOM_FONT)

    fig.text(0.9, 0.02, ORG_NAME, fontproperties=BOTTOM_FONT)

    # ##### 输出图片
    make_sure_path_exists(os.path.dirname(out_file))
    fig.savefig(out_file, dpi=100)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)


def plot_statistics_analysis(
        out_file=None,
        title=None,
        x_data=None,
        y_data=None,
        x_label1=None,
        x_label2=None,
        y_label1=None,
        y_label2=None,
        x_range1=None,
        x_range2=None,
        y_range1=None,
        y_range2=None,
        x_interval1=None,
        x_interval2=None,
        y_interval1=None,
        y_interval2=None,
        bar_step=None,
        bar_width=None,
        ymd=None, ymd_start=None, ymd_end=None,
        annotate1=None,
        annotate2=None,
        plot_background_fill=True,
        reference=None,
        regression=False):
    style_path = STYLE_PATH
    style_file = os.path.join(style_path, 'plot_regression.mplstyle')
    plt.style.use(style_file)
    figsize = (10, 5)
    dpi = 100
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax1 = plt.subplot2grid((1, 2), (0, 0))
    ax2 = plt.subplot2grid((1, 2), (0, 1))

    plot_ax = PlotAx()

    bar_x, bar_mean, bar_std, bar_count = get_bar_data(x_data, y_data, x_range1, bar_step)

    # -------------------------ax1------------------------
    marker_size = 5
    alpha = 0.8  # 透明度
    marker = "o"  # 形状
    color = "b"  # 颜色
    ax1.scatter(x_data, y_data, s=marker_size, marker=marker, c=color,
                lw=0, alpha=alpha, zorder=80)

    if plot_background_fill:
        plot_ax.plot_time_series(ax1, bar_x, bar_mean, marker='o-', color=RED,
                                 line_width=0.6, marker_size=5,
                                 marker_edgecolor=RED, marker_edgewidth=0, alpha=0.8, zorder=90,
                                 label="Monthly")
        plot_ax.plot_background_fill(ax1, x=bar_x,
                                     y1=bar_mean - bar_std,
                                     y2=bar_mean + bar_std,
                                     color=RED,
                                     alpha=0.2,)

    # ##### 画回归线
    if regression:
        color = 'r'
        linewidth = 1.2
        zorder = 80
        plot_ax.plot_regression_line(ax1, x_data, y_data, None, x_range1, color=color, linewidth=linewidth,
                                     zorder=zorder)

    if reference is not None:
        color = '#4cd964'
        word_local = (reference, y_range1[1] * -0.9)
        ax1.axvline(x=reference, color=color, lw=0.7)
        ax1.annotate(reference, word_local,
                     va="top", ha="center", color=color,
                     size=6, fontproperties=FONT0)

    # -------------------------ax2------------------------
    bar_count_log10 = np.log10(bar_count)
    width = bar_width
    color = BLUE
    plot_ax.plot_bar(ax2, bar_x, bar_count_log10, bar_count, width=width, color=color)

    # ############################## 格式化图片 #################################
    axs = [ax1, ax2]
    x_ranges = [x_range1, x_range2]
    y_ranges = [y_range1, y_range2]
    x_labels = [x_label1, x_label2]
    y_labels = [y_label1, y_label2]
    x_interval = [x_interval1, x_interval2]
    y_interval = [y_interval1, y_interval2]
    annotates = [annotate1, annotate2]
    for ax, x_range, y_range, x_label, y_label, x_interval, y_interval, annotate \
            in zip(axs, x_ranges, y_ranges, x_labels, y_labels, x_interval, y_interval, annotates):

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
        if x_interval is not None and x_range is not None:
            x_major_count = (x_range[1] - x_range[0]) / x_interval + 1
            format_kwargs['x_major_count'] = x_major_count
            if x_major_count <= 11:
                x_minor_count = 4
            else:
                x_minor_count = 1
            format_kwargs['x_minor_count'] = x_minor_count
        if y_interval is not None and y_range is not None:
            y_major_count = (y_range[1] - y_range[0]) / y_interval + 1
            format_kwargs['y_major_count'] = y_major_count
            if y_major_count <= 11:
                y_minor_count = 4
            else:
                y_minor_count = 1
            format_kwargs['y_minor_count'] = y_minor_count
        if annotate is not None:
            format_kwargs['annotate'] = annotate
            format_kwargs['annotate_font_color'] = REGRESSION_ANNOTATE_COLOR
            format_kwargs['annotate_font_size'] = REGRESSION_ANNOTATE_SIZE

        plot_ax.format_ax(ax, **format_kwargs)

    # ##### 标题和底部文字
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.15, top=0.85)

    if '\n' in title:
        title_y = 0.96
    else:
        title_y = 0.94
    fig.suptitle(title, y=title_y, ha='center', fontproperties=TITLE_FONT)

    if ymd_start and ymd_end:
        fig.text(0.65, 0.02, '%s-%s' % (ymd_start, ymd_end), fontproperties=BOTTOM_FONT)
    elif ymd:
        fig.text(0.65, 0.02, '%s' % ymd, fontproperties=BOTTOM_FONT)

    fig.text(0.87, 0.02, ORG_NAME, fontproperties=BOTTOM_FONT)

    # ##### 输出图片
    make_sure_path_exists(os.path.dirname(out_file))
    fig.savefig(out_file, dpi=100)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)


def plot_hour_analysis(
        out_file=None,
        title=None,
        x_data1=None,
        x_data2=None,
        x_data3=None,
        y_data1=None,
        y_data2=None,
        y_data3=None,
        x_label1=None,
        x_label2=None,
        y_label1=None,
        y_label2=None,
        x_range1=None,
        x_range2=None,
        y_range1=None,
        y_range2=None,
        x_interval1=None,
        x_interval2=None,
        y_interval1=None,
        y_interval2=None,
        labels1=None,
        bar_step=None,
        ymd=None, ymd_start=None, ymd_end=None,
        annotate1=None,
        annotate2=None,
        plot_background_fill=True,
        reference=None,
        filter_count=None):
    style_path = STYLE_PATH
    style_file = os.path.join(style_path, 'plot_regression.mplstyle')
    plt.style.use(style_file)
    figsize = (10, 5)
    dpi = 100
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax1 = plt.subplot2grid((1, 2), (0, 0))
    ax2 = plt.subplot2grid((1, 2), (0, 1))

    plot_ax = PlotAx()

    x_datas = [x_data1, x_data2, x_data3]
    y_datas = [y_data1, y_data2, y_data3]
    x_data_all = list()
    y_data_all = list()
    for x_data, y_data in zip(x_datas, y_datas):
        x_data_all = np.append(x_data_all, x_data)
        y_data_all = np.append(y_data_all, y_data)
    bar_x, bar_mean, bar_std, bar_count = get_bar_data(x_data_all, y_data_all, x_range1, bar_step)

    # -------------------------ax1------------------------
    marker_size = 5
    alpha = 0.6  # 透明度
    marker = "o"  # 形状
    colors = ['r', 'b', 'g']

    for color, x_data, y_data, label in zip(colors, x_datas, y_datas, labels1):
        ax1.scatter(x_data, y_data, s=marker_size, marker=marker, c=color,
                    lw=0, alpha=alpha, zorder=80, label=label)

    if filter_count is not None:
        # 过滤样本点少于50的点
        filter_index = np.where(bar_count >= 50)
        bar_x = bar_x[filter_index]
        bar_mean = bar_mean[filter_index]
        bar_std = bar_std[filter_index]

    if plot_background_fill:
        plot_ax.plot_time_series(ax1, bar_x, bar_mean, marker='o-', color=RED,
                                 line_width=0.6, marker_size=5,
                                 marker_edgecolor=RED, marker_edgewidth=0, alpha=0.8, zorder=90,
                                 label=None)
        plot_ax.plot_background_fill(ax1, x=bar_x,
                                     y1=bar_mean - bar_std,
                                     y2=bar_mean + bar_std,
                                     color=RED,
                                     alpha=0.2,)

    if reference is not None:
        color = '#4cd964'
        word_local = (reference, y_range1[1] * -0.9)
        ax1.axvline(x=reference, color=color, lw=0.7)
        ax1.annotate(reference, word_local,
                     va="top", ha="center", color=color,
                     size=6, fontproperties=FONT0)

    # -------------------------ax2------------------------
    bar_width = bar_step / 4.
    width = bar_width
    loop_count = 0
    for color, x_data, y_data, label in zip(colors, x_datas, y_datas, labels1):
        bar_x, bar_mean, bar_std, bar_count = get_bar_data(x_data, y_data, x_range2, bar_step)

        shift = loop_count * width
        bar_x = bar_x - bar_width / 2. + shift
        bar_count_log10 = np.log10(bar_count)
        plot_ax.plot_bar(
            ax2, bar_x, bar_count_log10, bar_count, width=width, color=color, label=label)
        loop_count += 1
    ax2.legend(loc=1, prop={"size": 11})
    # ############################## 格式化图片 #################################
    axs = [ax1, ax2]
    x_ranges = [x_range1, x_range2]
    y_ranges = [y_range1, y_range2]
    x_labels = [x_label1, x_label2]
    y_labels = [y_label1, y_label2]
    x_interval = [x_interval1, x_interval2]
    y_interval = [y_interval1, y_interval2]
    annotates = [annotate1, annotate2]
    for ax, x_range, y_range, x_label, y_label, x_interval, y_interval, annotate \
            in zip(axs, x_ranges, y_ranges, x_labels, y_labels, x_interval, y_interval, annotates):
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
        if x_interval is not None and x_range is not None:
            x_major_count = (x_range[1] - x_range[0]) / x_interval + 1
            format_kwargs['x_major_count'] = x_major_count
            if x_major_count <= 11:
                x_minor_count = 4
            else:
                x_minor_count = 1
            format_kwargs['x_minor_count'] = x_minor_count
        if y_interval is not None and y_range is not None:
            y_major_count = (y_range[1] - y_range[0]) / y_interval + 1
            format_kwargs['y_major_count'] = y_major_count
            if y_major_count <= 11:
                y_minor_count = 4
            else:
                y_minor_count = 1
            format_kwargs['y_minor_count'] = y_minor_count
        if annotate is not None:
            format_kwargs['annotate'] = annotate
            format_kwargs['annotate_font_color'] = REGRESSION_ANNOTATE_COLOR
            format_kwargs['annotate_font_size'] = REGRESSION_ANNOTATE_SIZE

        plot_ax.format_ax(ax, **format_kwargs)

    # ##### 标题和底部文字
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.15, top=0.85)

    if '\n' in title:
        title_y = 0.96
    else:
        title_y = 0.94
    fig.suptitle(title, y=title_y, ha='center', fontproperties=TITLE_FONT)

    if ymd_start and ymd_end:
        fig.text(0.65, 0.02, '%s-%s' % (ymd_start, ymd_end), fontproperties=BOTTOM_FONT)
    elif ymd:
        fig.text(0.65, 0.02, '%s' % ymd, fontproperties=BOTTOM_FONT)

    fig.text(0.87, 0.02, ORG_NAME, fontproperties=BOTTOM_FONT)

    # ##### 输出图片
    make_sure_path_exists(os.path.dirname(out_file))
    fig.savefig(out_file, dpi=100)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)


def plot_timeseries(
        data_x=None,
        data_y=None,
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
        plot_month=False,
        plot_zeroline=True):
    style_path = STYLE_PATH
    style_file = os.path.join(style_path, 'plot_timeseries.mplstyle')
    plt.style.use(style_file)
    figsize = (6, 4)
    dpi = 100
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax1 = plt.subplot2grid((1, 1), (0, 0))

    plot_ax = PlotAx()

    # 配置属性
    if x_range is not None:
        x_range = x_range
    elif ymd_start is not None and ymd_end is not None:
        x_min = datetime.strptime(ymd_start, '%Y%m%d')
        x_max = datetime.strptime(ymd_end, '%Y%m%d')
        x_range = [x_min, x_max]
    else:
        x_min = np.nanmin(data_x)
        x_max = np.nanmax(data_x)
        x_range = [x_min, x_max]

    # 绘制日数据长时间序列
    plot_ax.plot_time_series(ax1, data_x, data_y, marker='x', color=BLUE, line_width=None,
                             marker_size=6,
                             marker_edgecolor=BLUE, marker_edgewidth=0.3, alpha=0.8, zorder=80,
                             label="Daily")

    if plot_month:
        month_data_x, month_data_y, month_data_std = get_month_avg_std(data_x, data_y)
        finite_idx = np.isfinite(month_data_y)
        month_data_x = month_data_x[finite_idx]
        month_data_y = month_data_y[finite_idx]
        month_data_std = month_data_std[finite_idx]

        # 绘制月数据长时间序列
        if month_data_x is not None and month_data_y is not None:
            plot_ax.plot_time_series(ax1, month_data_x, month_data_y, marker='o-', color=RED,
                                     line_width=0.6, marker_size=5,
                                     marker_edgecolor=RED, marker_edgewidth=0, alpha=0.8, zorder=90,
                                     label="Monthly")

            # 绘制背景填充
            if month_data_std is not None:
                plot_ax.plot_background_fill(ax1, x=month_data_x,
                                             y1=month_data_y - month_data_std,
                                             y2=month_data_y + month_data_std,
                                             color=RED,
                                             alpha=0.2,
                                             )
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
        circle1 = mpatches.Circle((74, 15), 6, color=BLUE, ec=GRAY, lw=0)
        circle2 = mpatches.Circle((164, 15), 6, color=RED, ec=GRAY, lw=0)
        fig.patches.extend([circle1, circle2])

        fig.text(0.15, 0.02, 'Daily', color=BLUE, fontproperties=BOTTOM_FONT)
        fig.text(0.3, 0.02, 'Monthly', color=RED, fontproperties=BOTTOM_FONT)
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


def plot_timeseries_two(
        data_x1=None,
        data_x2=None,
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
        plot_month=False,
        label1='',
        label2='',
        plot_zeroline=True):
    style_path = STYLE_PATH
    style_file = os.path.join(style_path, 'plot_timeseries.mplstyle')
    plt.style.use(style_file)
    figsize = (6, 4)
    dpi = 100
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax1 = plt.subplot2grid((1, 1), (0, 0))

    plot_ax = PlotAx()

    # 配置属性
    if x_range is not None:
        x_range = x_range
    elif ymd_start is not None and ymd_end is not None:
        x_min = datetime.strptime(ymd_start, '%Y%m%d')
        x_max = datetime.strptime(ymd_end, '%Y%m%d')
        x_range = [x_min, x_max]
    else:
        x_min = np.nanmin(np.append(data_x1, data_x2))
        x_max = np.nanmax(np.append(data_x1, data_x2))
        x_range = [x_min, x_max]

    # 绘制日数据长时间序列
    data_xs = [data_x1, data_x2]
    data_ys = [data_y1, data_y2]
    colors = [BLUE, RED]
    labels = [label1, label2]
    for data_x, data_y, color, label in zip(data_xs, data_ys, colors, labels):
        plot_ax.plot_time_series(ax1, data_x, data_y, marker='x', color=color, line_width=None,
                                 marker_size=6,
                                 marker_edgecolor=color, marker_edgewidth=0.3, alpha=0.8, zorder=80,
                                 label=label)

    if plot_month:
        data_xs = np.append(data_x1, data_x2)
        data_ys = np.append(data_y1, data_y2)
        month_data_x, month_data_y, month_data_std = get_month_avg_std(data_xs, data_ys)
        finite_idx = np.isfinite(month_data_y)
        month_data_x = month_data_x[finite_idx]
        month_data_y = month_data_y[finite_idx]
        month_data_std = month_data_std[finite_idx]

        # 绘制月数据长时间序列
        if month_data_x is not None and month_data_y is not None:
            plot_ax.plot_time_series(ax1, month_data_x, month_data_y, marker='o-', color=RED,
                                     line_width=0.6, marker_size=5,
                                     marker_edgecolor=RED, marker_edgewidth=0, alpha=0.8, zorder=90,)

            # 绘制背景填充
            if month_data_std is not None:
                plot_ax.plot_background_fill(ax1, x=month_data_x,
                                             y1=month_data_y - month_data_std,
                                             y2=month_data_y + month_data_std,
                                             color=RED,
                                             alpha=0.2,
                                             )

    # 绘制 y=0 线配置，在绘制之前设置x轴范围
    if plot_zeroline:
        plot_ax.plot_zero_line(ax1, np.append(data_x1, data_x2), x_range)

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
    ax1.legend(loc=1, prop={"size": 10}, frameon=True)
    plot_ax.format_ax(ax1, **format_kwargs)
    # --------------------
    plt.tight_layout()
    fig.suptitle(title, y=0.96, ha='center', fontproperties=TITLE_FONT)
    if '\n' in title:
        fig.subplots_adjust(bottom=0.2, top=0.82)
    else:
        fig.subplots_adjust(bottom=0.2, top=0.85)

    if ymd_start and ymd_end:
        # circle1 = mpatches.Circle((74, 15), 6, color=BLUE, ec=GRAY, lw=0)
        # circle2 = mpatches.Circle((164, 15), 6, color=RED, ec=GRAY, lw=0)
        # fig.patches.extend([circle1, circle2])

        # fig.text(0.15, 0.02, 'Daily', color=BLUE, fontproperties=BOTTOM_FONT)
        # fig.text(0.3, 0.02, 'Monthly', color=RED, fontproperties=BOTTOM_FONT)
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


def plot_timeseries_omb(
        data_x=None,
        data_a=None,
        data_b=None,
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
        plot_zeroline=False):
    style_path = STYLE_PATH
    style_file = os.path.join(style_path, 'plot_timeseries.mplstyle')
    plt.style.use(style_file)
    figsize = (6, 4)
    dpi = 100
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax1 = plt.subplot2grid((1, 1), (0, 0))

    plot_ax = PlotAx()

    # 配置属性
    if x_range is not None:
        x_range = x_range
    elif ymd_start is not None and ymd_end is not None:
        x_min = datetime.strptime(ymd_start, '%Y%m%d')
        x_max = datetime.strptime(ymd_end, '%Y%m%d')
        x_range = [x_min, x_max]
    else:
        x_min = np.nanmin(data_x)
        x_max = np.nanmax(data_x)
        x_range = [x_min, x_max]

    # 绘制日数据长时间序列
    date_start, date_end = x_range
    norm = plot_ax.plot_time_series_omb(
        ax1, data_x=data_x, data_a=data_a, data_b=data_b, date_start=date_start,
        date_end=date_end, y_range=y_range, vmin=-4, vmax=4)

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
        fig.subplots_adjust(bottom=0.25, top=0.82)
    else:
        fig.subplots_adjust(bottom=0.25, top=0.85)

    # -------add colorbar ---------
    fig.canvas.draw()
    point_bl = ax1.get_position().get_points()[0]  # 左下
    point_tr = ax1.get_position().get_points()[1]  # 右上
    cbar_height = 0.05
    colorbar_ax = fig.add_axes([point_bl[0] - cbar_height, cbar_height,
                                (point_tr[0] - point_bl[0]) / 2.2, cbar_height])

    colorbar.ColorbarBase(colorbar_ax, cmap='jet', norm=norm, orientation='horizontal')
    for l in colorbar_ax.xaxis.get_ticklabels():
        l.set_fontproperties(FONT0)
        l.set_fontsize(9)
    # ----------------------------------

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


def plot_map_distribution(
        latitude,
        longitude,
        value,
        out_file,
        title='',
        ptype=None,
        vmin=None,
        vmax=None,
        marker='.',
        markersize=1.5,
        fmt='%d',
        mean=None,
        count=None,
        area_range=None,
        ymd=None,
        ymd_start=None,
        ymd_end=None,
):
    plot_figure = PlotFigure()
    fig = plt.figure(figsize=(6, 5))  # 图像大小
    pos1 = [0.1, 0.3, 0.8, 0.55]
    ax1 = plot_figure.add_ax(fig, *pos1)
    p = dv_map.dv_map(fig, ax=ax1)

    p.colormap = 'jet'
    p.delat = 30
    p.delon = 30
    p.colorbar_fmt = fmt
    p.show_countries = True
#                 p.show_china = True
#                 p.show_china_province = True
    p.show_line_of_latlon = True
    p.show_colorbar = False
    if area_range is not None:
        p.box = area_range  # [90., -90., -180., 180.] 经纬度范围 NSWE
    p.easyplot(
        latitude, longitude, value, ptype=ptype, vmin=vmin, vmax=vmax,
        markersize=markersize, marker=marker)
    p.draw()
    # 直方图
    pos2 = [0.1, 0.18, 0.8, 0.1]
    ax2 = plot_figure.add_ax(fig, *pos2)
    p2 = dv_hist(fig, ax=ax2)
    p2.easyplot(
        value.reshape((-1,)), bins=512, cmap="jet", range=(vmin, vmax))
    p2.xlim_min = vmin
    p2.xlim_max = vmax
    p2.simple_axis(mode=0)
    p2.draw()

    # ColorBar
    pos3 = [0.1, 0.145, 0.8, 0.03]
    ax3 = plot_figure.add_ax(fig, *pos3)
    plot_ax = PlotAx()
    plot_ax.add_colorbar_horizontal(ax3, vmin, vmax, cmap="jet", fmt=fmt)

    if mean is not None:
        percent = (mean - vmin) / (vmax - vmin)
        ax3.plot(percent, 0.5, 'ko', ms=5, zorder=5)
        strlist = ["mean = %0.2f" % mean]
        add_annotate(ax2, strlist, 'left_top')
    if count is not None:
        strlist = ["count = %d" % int(count)]
        add_annotate(ax2, strlist, 'right_top')

    # --------------------
    plt.tight_layout()
    fig.suptitle(title, y=0.96, ha='center', fontproperties=TITLE_FONT)
    if '\n' in title:
        fig.subplots_adjust(bottom=0.14, top=0.87)
    else:
        fig.subplots_adjust(bottom=0.14, top=0.90)

    if ymd_start and ymd_end:
        circle1 = mpatches.Circle((74, 15), 6, color=BLUE, ec=GRAY, lw=0)
        circle2 = mpatches.Circle((164, 15), 6, color=RED, ec=GRAY, lw=0)
        fig.patches.extend([circle1, circle2])

        fig.text(0.15, 0.02, 'Daily', color=BLUE, fontproperties=BOTTOM_FONT)
        fig.text(0.3, 0.02, 'Monthly', color=RED, fontproperties=BOTTOM_FONT)
        fig.text(0.50, 0.02, '%s-%s' % (ymd_start, ymd_end), fontproperties=BOTTOM_FONT)
    elif ymd:
        fig.text(0.50, 0.02, '%s' % ymd, fontproperties=BOTTOM_FONT)

    fig.text(0.8, 0.02, ORG_NAME, fontproperties=BOTTOM_FONT)
    # ---------------
    make_sure_path_exists(os.path.dirname(out_file))
    fig.savefig(out_file, dpi=200)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)


def plot_timeseries_3ax(
        data_x1=None,
        data_y1=None,
        data_x2=None,
        data_y2=None,
        data_x3=None,
        data_y3=None,
        out_file=None,
        title=None,
        y_label1=None,
        y_label2=None,
        y_label3=None,
        x_range=None,
        y_range1=None,
        y_range2=None,
        y_range3=None,
        y_interval1=None,
        y_interval2=None,
        y_interval3=None,
        ymd=None, ymd_start=None, ymd_end=None,
        annotate=None,
        plot_month=False,
        plot_zeroline=True):
    style_path = STYLE_PATH
    style_file = os.path.join(style_path, 'plot_timeseries.mplstyle')
    plt.style.use(style_file)
    figsize = (6, 6)
    dpi = 100
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax1 = plt.subplot2grid((3, 1), (0, 0))
    ax2 = plt.subplot2grid((3, 1), (1, 0))
    ax3 = plt.subplot2grid((3, 1), (2, 0))

    plot_ax = PlotAx()

    # 配置属性
    if x_range is not None:
        x_range = x_range
    elif ymd_start is not None and ymd_end is not None:
        x_min = datetime.strptime(ymd_start, '%Y%m%d')
        x_max = datetime.strptime(ymd_end, '%Y%m%d')
        x_range = [x_min, x_max]
    else:
        x_min = np.nanmin(data_x1)
        x_max = np.nanmax(data_x1)
        x_range = [x_min, x_max]

    # 绘制日数据长时间序列
    axs = [ax1, ax2, ax3]
    data_xs = [data_x1, data_x2, data_x3]
    data_ys = [data_y1, data_y2, data_y3]
    y_ranges = [y_range1, y_range2, y_range3]
    y_labels = [y_label1, y_label2, y_label3]
    y_intervals = [y_interval1, y_interval2, y_interval3]
    loop_count = 0
    for ax, data_x, data_y, y_range, y_label, y_interval in zip(axs, data_xs, data_ys, y_ranges,
                                                                y_labels, y_intervals):
        loop_count += 1
        plot_ax.plot_time_series(
            ax, data_x, data_y, marker='x', color=BLUE, line_width=None, marker_size=6,
            marker_edgecolor=BLUE, marker_edgewidth=0.3, alpha=0.8, zorder=80, label="Daily")

        if plot_month:
            month_data_x, month_data_y, month_data_std = get_month_avg_std(data_x, data_y)
            finite_idx = np.isfinite(month_data_y)
            month_data_x = month_data_x[finite_idx]
            month_data_y = month_data_y[finite_idx]
            month_data_std = month_data_std[finite_idx]


            # 绘制月数据长时间序列
            if month_data_x is not None and month_data_y is not None:
                plot_ax.plot_time_series(
                    ax, month_data_x, month_data_y, marker='o-', color=RED, line_width=0.6,
                    marker_size=5, marker_edgecolor=RED, marker_edgewidth=0, alpha=0.8, zorder=90,
                    label="Monthly")

                # 绘制背景填充
                if month_data_std is not None:
                    plot_ax.plot_background_fill(
                        ax, x=month_data_x, y1=month_data_y - month_data_std,
                        y2=month_data_y + month_data_std, color=RED, alpha=0.2,)
        # 绘制 y=0 线配置，在绘制之前设置x轴范围
        if plot_zeroline:
            plot_ax.plot_zero_line(ax, data_x, x_range)

        # 取消 x轴坐标
        if loop_count <= 2:
            plt.setp(ax.get_xticklabels(), visible=False)
            timeseries = False
        else:
            timeseries = True
        format_kwargs = {
            'timeseries': timeseries,
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

        plot_ax.format_ax(ax, **format_kwargs)
    # --------------------
    plt.tight_layout()
    fig.suptitle(title, y=0.96, ha='center', fontproperties=TITLE_FONT)
    if '\n' in title:
        fig.subplots_adjust(bottom=0.14, top=0.87)
    else:
        fig.subplots_adjust(bottom=0.14, top=0.90)

    if ymd_start and ymd_end:
        circle1 = mpatches.Circle((74, 15), 6, color=BLUE, ec=GRAY, lw=0)
        circle2 = mpatches.Circle((164, 15), 6, color=RED, ec=GRAY, lw=0)
        fig.patches.extend([circle1, circle2])

        fig.text(0.15, 0.02, 'Daily', color=BLUE, fontproperties=BOTTOM_FONT)
        fig.text(0.3, 0.02, 'Monthly', color=RED, fontproperties=BOTTOM_FONT)
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


def plot_map_project(
        latitude,
        longitude,
        value,
        out_file,
        title=None,
        ptype=None,
        vmin=None,
        vmax=None,
        marker=None,
        markersize=None):
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
    p.easyplot(latitude, longitude, value, vmin=vmin, vmax=vmax,
               ptype=ptype, markersize=markersize, marker=marker)
    p.title = title
    p.savefig(out_file)
    print '>>> {}'.format(out_file)


def plot_histogram(
        out_file=None,
        data=None,
        bins_count=200,
        title=None,
        x_label=None,
        y_label=None,
        x_range=None,
        y_range=None,
        hist_label=None,
        annotate=None,
        ymd_start=None,
        ymd_end=None,
        ymd=None, ):
    style_path = STYLE_PATH
    style_file = os.path.join(style_path, 'plot_histogram.mplstyle')
    plt.style.use(style_file)
    figsize = (6, 4)
    dpi = 100
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax1 = plt.subplot2grid((1, 1), (0, 0))

    ax1.hist(data,
             bins=bins_count,
             range=x_range,
             histtype="bar",
             color='b',
             label=hist_label,
             alpha=1, )

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
    fig.suptitle(title, y=0.94, ha='center', fontproperties=TITLE_FONT)
    fig.subplots_adjust(bottom=0.15, top=0.85)

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


def plot_image_origin(
        r,
        g,
        b,
        out_file,
        fill_point=0):
    row, col = np.shape(r)
    width = col / 100.
    length = row / 100.
    dpi = 100
    fig = plt.figure(figsize=(width, length), dpi=dpi)  # china

    for _ in xrange(fill_point):
        fill_points_2d_by_mask(r, np.isnan(r))
        fill_points_2d_by_mask(g, np.isnan(g))
        fill_points_2d_by_mask(b, np.isnan(b))

    rgb = np.stack([r, g, b], axis=2)

    plt.imshow(rgb)

    plt.axis('off')

    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)

    # ---------------
    make_sure_path_exists(os.path.dirname(out_file))

    fig.savefig(out_file, dpi=dpi)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)


def plot_image_image(r, g, b, out_file, brightness=None):
    """
    :param r: ndarray
    :param g: ndarray
    :param b: ndarray
    :param out_file: str
    :param brightness: int 亮度提升的倍数
    :return:
    """
    r = normal255int8(r)
    g = normal255int8(g)
    b = normal255int8(b)

    imr = Image.fromarray(r, 'L')
    img = Image.fromarray(g, 'L')
    imb = Image.fromarray(b, 'L')
    im = Image.merge('RGB', (imr, img, imb))

    if brightness is not None:
        enh_bri = ImageEnhance.Brightness(im)
        im = enh_bri.enhance(brightness)

    im.save(out_file)
    print '>>> {}'.format(out_file)


def plot_image_plt(
        r,
        g,
        b,
        out_file,
        title=None,
        ymd_start=None,
        ymd_end=None,
        ymd=None,
        fill_point=0):
    width = 8
    length = 8
    dpi = 100
    fig = plt.figure(figsize=(width, length), dpi=dpi)  # china
    fig.subplots_adjust(bottom=0.15, top=0.86)
    ax1 = plt.subplot2grid((1, 1), (0, 0))

    for _ in xrange(fill_point):
        fill_points_2d_by_mask(r, np.isnan(r))
        fill_points_2d_by_mask(g, np.isnan(g))
        fill_points_2d_by_mask(b, np.isnan(b))

    rgb = np.stack([r, g, b], axis=2)
    ax1.imshow(rgb)

    ax1.axis('off')

    # --------------------
    # plt.tight_layout()
    fig.suptitle(title, y=0.94, ha='center', fontproperties=TITLE_FONT)

    if width > 8:
        text_left = 0.7
    else:
        text_left = 0.5

    bottom_text = ''
    if ymd_start and ymd_end:
        bottom_text = bottom_text + '%s-%s' % (ymd_start, ymd_end)
    elif ymd:
        bottom_text = bottom_text + '%s' % ymd
    if ORG_NAME:
        bottom_text = bottom_text + '  ' + ORG_NAME

    if bottom_text:
        fig.text(text_left, 0.02, bottom_text, fontproperties=BOTTOM_FONT)
    # ---------------
    make_sure_path_exists(os.path.dirname(out_file))

    fig.savefig(out_file, dpi=dpi)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)


def plot_map_image(
        latitude,
        longitude,
        r,
        g,
        b,
        out_file,
        title=None,
        area_range=None,
        ymd_start=None,
        ymd_end=None,
        ymd=None,
        star_makers=None,
        fill_point=0):
    # row, col = np.shape(latitude)
    # width = col / 100.
    # length = row / 100.
    #
    # if width > 12:
    #     s = width / 12.
    #     width = width / s
    #     length = length / s
    # if length > 8:
    #     s = length / 8.
    #     width = width / s
    #     length = length / s
    # if width < 4:
    #     s = 4. / width
    #     width = width * s
    #     length = length * s
    #
    # width = np.ceil(width)
    # length = np.ceil(length)

    width = 8
    length = 8
    dpi = 100
    fig = plt.figure(figsize=(width, length), dpi=dpi)  # china
    fig.subplots_adjust(bottom=0.15, top=0.86)
    ax1 = plt.subplot2grid((1, 1), (0, 0))

    for _ in xrange(fill_point):
        fill_points_2d_by_mask(r, np.isnan(r))
        fill_points_2d_by_mask(g, np.isnan(g))
        fill_points_2d_by_mask(b, np.isnan(b))
        fill_points_2d_by_mask(latitude, np.isnan(latitude))
        fill_points_2d_by_mask(longitude, np.isnan(longitude))

    rgb = np.stack([r, g, b], axis=2)

    # 画区域
    if area_range is not None:
        llcrnrlat = area_range[0]
        urcrnrlat = area_range[1]
        llcrnrlon = area_range[2]
        urcrnrlon = area_range[3]
    else:
        llcrnrlat = np.nanmean(latitude)
        urcrnrlat = np.nanmax(latitude)
        llcrnrlon = np.nanmean(longitude)
        urcrnrlon = np.nanmax(longitude)

    m = Basemap(llcrnrlat=llcrnrlat, urcrnrlat=urcrnrlat,
                llcrnrlon=llcrnrlon, urcrnrlon=urcrnrlon,
                resolution='c', area_thresh=10000.,
                projection='cyl', lat_ts=20., ax=ax1)
    #
    # m.fillcontinents(color=GRAY)

    # draw parallels
    m.drawparallels(np.arange(90., -91., -5.), linewidth=LINE_WIDTH,
                    labels=[1, 0, 0, 1],
                    dashes=[100, .0001], color='white',
                    textcolor=EDGE_GRAY, fontproperties=TICKER_FONT)
    # draw meridians
    m.drawmeridians(np.arange(-180., 180., 5.), linewidth=LINE_WIDTH,
                    labels=[1, 0, 0, 1],
                    dashes=[100, .0001], color='white',
                    textcolor=EDGE_GRAY, fontproperties=TICKER_FONT)
    # draw parallels
    m.drawparallels(np.arange(60., -90., -5.), linewidth=LINE_WIDTH,
                    labels=[0, 0, 0, 0],
                    dashes=[100, .0001], color='white')
    # draw meridians
    m.drawmeridians(np.arange(-150., 180., 5.), linewidth=LINE_WIDTH,
                    labels=[0, 0, 0, 0],
                    dashes=[100, .0001], color='white')

    m.imshow(rgb)

    if star_makers is not None:
        add_landmark(ax1, m, star_makers, 'cyl', color='b')
    # --------------------
    # plt.tight_layout()
    fig.suptitle(title, y=0.94, ha='center', fontproperties=TITLE_FONT)

    if width > 8:
        text_left = 0.7
    else:
        text_left = 0.5

    bottom_text = ''
    if ymd_start and ymd_end:
        bottom_text = bottom_text + '%s-%s' % (ymd_start, ymd_end)
    elif ymd:
        bottom_text = bottom_text + '%s' % ymd
    if ORG_NAME:
        bottom_text = bottom_text + '  ' + ORG_NAME

    if bottom_text:
        fig.text(text_left, 0.02, bottom_text, fontproperties=BOTTOM_FONT)
    # ---------------
    make_sure_path_exists(os.path.dirname(out_file))

    fig.savefig(out_file, dpi=dpi)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)


def plot_map(
        latitude,
        longitude,
        out_file,
        title=None,
        marker='o',
        markersize=1.8,
        alpha=1,
        area_range=None,
        polar_range=None,
        ymd_start=None,
        ymd_end=None,
        ymd=None,
        star_makers=None):
    """
    画蝴蝶图
    """
    style_path = STYLE_PATH
    style_file = os.path.join(style_path, 'plot_map.mplstyle')
    plt.style.use(style_file)

    colors = [RED]
    if area_range is not None and polar_range is not None:
        fig = plt.figure(figsize=(8, 10), dpi=100)
        fig.subplots_adjust(bottom=0.15, top=0.90)
        ax1 = plt.subplot2grid((2, 2), (0, 0))
        ax2 = plt.subplot2grid((2, 2), (0, 1))
        ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)

        # 画两极
        polar_range = polar_range  # 两极范围
        m = plot_map_bottom(ax1, "north", polar_range)
        plot_map_point(m, longitude, latitude, colors[0], marker, markersize, alpha)
        m = plot_map_bottom(ax2, "south", polar_range)
        plot_map_point(m, longitude, latitude, colors[0], marker, markersize, alpha)

        # 画区域
        area_range = area_range  # 区域范围
        m = plot_map_bottom(ax3, "area", area_range)
        plot_map_point(m, longitude, latitude, colors[0], marker, markersize, alpha)

    elif polar_range is not None:
        fig = plt.figure(figsize=(8, 5), dpi=100)
        fig.subplots_adjust(bottom=0.15, top=0.86)
        ax1 = plt.subplot2grid((1, 2), (0, 0))
        ax2 = plt.subplot2grid((1, 2), (0, 1))
        ax3 = None

        # 画两极
        polar_range = polar_range  # 两极范围
        m = plot_map_bottom(ax1, "north", polar_range)
        plot_map_point(m, longitude, latitude, colors[0], marker, markersize, alpha)
        m = plot_map_bottom(ax2, "south", polar_range)
        plot_map_point(m, longitude, latitude, colors[0], marker, markersize, alpha)

    elif area_range is not None:
        fig = plt.figure(figsize=(8, 5), dpi=100)  # china
        fig.subplots_adjust(bottom=0.15, top=0.86)
        ax3 = plt.subplot2grid((1, 2), (0, 0), colspan=2)

        # 画区域
        area_range = area_range  # 区域范围
        m = plot_map_bottom(ax3, "area", area_range, set_title=False)
        plot_map_point(m, longitude, latitude, colors[0], marker, markersize, alpha)
    else:
        raise KeyError("area_range and polar_range are all None")

    if star_makers is not None and ax3 is not None:
        add_landmark(ax3, m, star_makers, 'cyl', color='b')

    # --------------------
    # plt.tight_layout()
    fig.suptitle(title, y=0.94, ha='center', fontproperties=TITLE_FONT)

    if ymd_start and ymd_end:
        fig.text(0.50, 0.02, '%s-%s' % (ymd_start, ymd_end), fontproperties=BOTTOM_FONT)
    elif ymd:
        fig.text(0.50, 0.02, '%s' % ymd, fontproperties=BOTTOM_FONT)

    fig.text(0.8, 0.05, ORG_NAME, fontproperties=BOTTOM_FONT)
    # ---------------
    make_sure_path_exists(os.path.dirname(out_file))
    fig.savefig(out_file, dpi=100)
    fig.clear()
    plt.close()
    print '>>> {}'.format(out_file)


def plot_map_bottom(ax, map_type, map_range, set_title=True):
    """
    create new figure
    """
    if map_type == "area":
        area_range = map_range
        llcrnrlat = area_range[0]
        urcrnrlat = area_range[1]
        llcrnrlon = area_range[2]
        urcrnrlon = area_range[3]

        m = Basemap(llcrnrlat=llcrnrlat, urcrnrlat=urcrnrlat,
                    llcrnrlon=llcrnrlon, urcrnrlon=urcrnrlon,
                    resolution='c', area_thresh=10000.,
                    projection='cyl', lat_ts=20., ax=ax)

        m.fillcontinents(color=GRAY)

        # draw parallels
        m.drawparallels(np.arange(90., -91., -30.), linewidth=LINE_WIDTH,
                        labels=[1, 0, 0, 1],
                        dashes=[100, .0001], color='white',
                        textcolor=EDGE_GRAY, fontproperties=TICKER_FONT)
        # draw meridians
        m.drawmeridians(np.arange(-180., 180., 30.), linewidth=LINE_WIDTH,
                        labels=[1, 0, 0, 1],
                        dashes=[100, .0001], color='white',
                        textcolor=EDGE_GRAY, fontproperties=TICKER_FONT)
        # draw parallels
        m.drawparallels(np.arange(60., -90., -30.), linewidth=LINE_WIDTH,
                        labels=[0, 0, 0, 0],
                        dashes=[100, .0001], color='white')
        # draw meridians
        m.drawmeridians(np.arange(-150., 180., 30.), linewidth=LINE_WIDTH,
                        labels=[0, 0, 0, 0],
                        dashes=[100, .0001], color='white')
        if set_title:
            ax.set_title("Global Map", fontproperties=FONT0)

    else:
        if map_type == "north":
            north_range = map_range[0]
            north_range = int(north_range[0])
            m = Basemap(projection='npaeqd', boundinglat=north_range - 1,
                        lon_0=0, resolution='c', ax=ax)

            lat_labels = [(0.0, i) for i in xrange(north_range, 91, 10)]
            for lon, lat in lat_labels:
                xpt, ypt = m(lon, lat)
                ax.text(xpt - 500000, ypt - 100000, str(lat)[0:2] + u'°N',
                        fontproperties=TICKER_FONT)
            if set_title:
                ax.set_title("Northern Hemisphere", fontproperties=FONT0)
        elif map_type == "south":
            south_range = map_range[1]
            south_range = int(south_range[0])
            m = Basemap(projection='spaeqd', boundinglat=south_range + 1,
                        lon_0=180, resolution='c', ax=ax)

            lat_labels = [(0.0, i) for i in xrange(south_range, -91, -10)]
            for lon, lat in lat_labels:
                xpt, ypt = m(lon, lat)
                ax.text(xpt + 500000, ypt + 200000, str(lat)[1:3] + u'°S',
                        fontproperties=TICKER_FONT)
            if set_title:
                ax.set_title("Southern Hemisphere", fontproperties=FONT0)
        else:
            raise KeyError("ns must be north or south")

        m.fillcontinents(color=GRAY)

        # draw parallels
        m.drawparallels(np.arange(60., 91., 10.), linewidth=LINE_WIDTH,
                        labels=[1, 0, 0, 1],
                        dashes=[100, .0001], color='white',
                        textcolor=EDGE_GRAY, fontproperties=TICKER_FONT)
        # draw meridians
        m.drawmeridians(np.arange(-180., 180., 30.), linewidth=LINE_WIDTH,
                        labels=[1, 0, 0, 1],
                        dashes=[100, .0001], color='white', latmax=90,
                        textcolor=EDGE_GRAY, fontproperties=TICKER_FONT)
        # draw parallels
        m.drawparallels(np.arange(60., -91., -10.), linewidth=LINE_WIDTH,
                        labels=[0, 0, 0, 0],
                        dashes=[100, .0001], color='white')
        # draw meridians
        m.drawmeridians(np.arange(-180., 180., 30.), linewidth=LINE_WIDTH,
                        labels=[0, 0, 0, 0],
                        dashes=[100, .0001], color='white', latmax=90)

    return m


def plot_map_point(m, lons, lats, color, marker='o', markersize=1.8, alpha=1):
    x, y = m(lons, lats)
    m.plot(x, y, marker=marker, linewidth=0, markerfacecolor=color,
           markersize=markersize,
           markeredgecolor=None, mew=0, alpha=alpha)


def add_landmark(ax, m, lonlatlocation, projection, color="r", marker="star",
                 markersize=60, fontsize=7.5, yplus=0):

    if marker == "star":
        marker = (5, 1, 0)
    if yplus == 0:
        if projection == "aea":
            yplus = 75000
        elif projection == "ortho":
            yplus = 160000
        else:
            yplus = 3
    for lon, lat, location in lonlatlocation:
        xpt, ypt = m(lon, lat)

        m.scatter(xpt, ypt, marker=marker, s=markersize, color=color,
                  edgecolors="#999999", lw=0.1, zorder=10)
        fnt = FONT0

        ax.annotate(location, xy=(xpt, ypt + yplus), ha="center", fontproperties=fnt,
                    size=fontsize, color="#999999")


def format_plot_time(plot_time):
    """
    all day night 转为 ALL Day Night
    :param plot_time:
    :return:
    """
    plot_time = plot_time.lower()
    if plot_time == 'all':
        plot_time = plot_time.upper()
    else:
        plot_time = plot_time.capitalize()
    return plot_time


def fill_2d(array2d, mask, use_from):
    """
    2维矩阵无效值补点
    array2d  2维矩阵
    mask     无效值掩模矩阵
    useFrom  u/d/l/r, 用上/下/左/右的点来补点
    """
    assert len(array2d.shape) == 2, \
        "array2d must be 2d array."
    assert array2d.shape == mask.shape, \
        "array2d and musk must have same shape."

    condition = np.empty_like(mask)
    # 用上方的有效点补点
    if use_from == 'up' or use_from == 'u':
        condition[1:, :] = mask[1:, :] * (~mask)[:-1, :]
        condition[0, :] = False
        index = np.where(condition)
        array2d[index[0], index[1]] = array2d[index[0] - 1, index[1]]

    # 用右方的有效点补点
    elif use_from == 'right' or use_from == 'r':
        condition[:, :-1] = mask[:, :-1] * (~mask)[:, 1:]
        condition[:, -1] = False
        index = np.where(condition)
        array2d[index[0], index[1]] = array2d[index[0], index[1] + 1]

    # 用下方的有效点补点
    elif use_from == 'down' or use_from == 'd':
        condition[:-1, :] = mask[:-1, :] * (~mask)[1:, :]
        condition[-1, :] = False
        index = np.where(condition)
        array2d[index[0], index[1]] = array2d[index[0] + 1, index[1]]

    # 用左方的有效点补点
    elif use_from == 'left' or use_from == 'l':
        condition[:, 1:] = mask[:, 1:] * (~mask)[:, :-1]
        condition[:, 0] = False
        index = np.where(condition)
        array2d[index[0], index[1]] = array2d[index[0], index[1] - 1]


def fill_points_2d(array2d, invalid_value=0):
    """
    2维矩阵无效值补点
    array2d  2维矩阵
    invalidValue  无效值
    """
    # 用右方的有效点补点
    mask = np.isclose(array2d, invalid_value)
    fill_2d(array2d, mask, 'r')

    # 用左方的有效点补点
    mask = np.isclose(array2d, invalid_value)
    fill_2d(array2d, mask, 'l')

    # 用上方的有效点补点
    mask = np.isclose(array2d, invalid_value)
    fill_2d(array2d, mask, 'u')

    # 用下方的有效点补点
    mask = np.isclose(array2d, invalid_value)
    fill_2d(array2d, mask, 'd')


def fill_points_2d_by_mask(array2d, mask):
    fill_2d(array2d, mask, 'r')
    fill_2d(array2d, mask, 'l')
    fill_2d(array2d, mask, 'u')
    fill_2d(array2d, mask, 'd')


def normal255int8(array):
    """
    小于 0 的值赋值为0，其他值归一化到 0-255
    :param array: ndarray
    :return: ndarray
    """
    array[array < 0] = 0
    array[np.isnan(array)] = 0
    data = (array - array.min()) / (array.max() - array.min())
    data = data * 255
    data = data.astype(np.uint8)
    return data


if __name__ == '__main__':
    pass
    # #####测试 plot_timeseries
    # from lib_test import get_timeseries_test_data
    # t_data_x, t_data_y = get_timeseries_test_data(800)
    #
    # t_x_range = [np.min(t_data_x), np.max(t_data_x)]
    #
    # plot_timeseries(t_data_x, t_data_y,
    #                 r'D:\nsmc\cross_data\test\test_timeseries.png', title='title',
    #                 y_label='y_label',
    #                 x_range=t_x_range, y_range=[-1, 1], y_interval=0.25, plot_month=True,
    #                 plot_zeroline=True, ymd_start='20180101', ymd_end='20280403')

    # ##### 测试 plot_timeseries_3ax
    # from lib_test import get_timeseries_test_data
    # t_data_x, t_data_y = get_timeseries_test_data(800)
    # t_x_range = [np.min(t_data_x), np.max(t_data_x)]
    # t_y_label = 'y_label'
    # t_y_range = [-1, 1]
    # t_y_interval = 1
    # plot_timeseries_3ax(data_x1=t_data_x, data_x2=t_data_x, data_x3=t_data_x,
    #                     data_y1=t_data_y, data_y2=t_data_y, data_y3=t_data_y,
    #                     out_file=r'D:\nsmc\cross_data\test\test_timeseries_3ax.png',
    #                     title='abcdefghijklmnop123456789013241324134',
    #                     y_label1=t_y_label, y_label2=t_y_label, y_label3=t_y_label,
    #                     y_range1=t_y_range, y_range2=t_y_range, y_range3=t_y_range,
    #                     y_interval1=t_y_interval, y_interval2=t_y_interval,
    #                     y_interval3=t_y_interval,
    #                     ymd_start='20180101', ymd_end='20200403',
    #                     plot_month=True)

    # #### 测试 plot_timeseries_omb
    # from lib_test import get_timeseries_test_data
    # t_data_x, t_data_y = get_timeseries_test_data(800)
    # t_x_range = [np.min(t_data_x), np.max(t_data_x)]
    # t_title = 'title\ntitle'
    # t_y_label = 'y_label'
    # t_y_range = [220, 320]
    # t_y_interval = 20
    # plot_timeseries_omb(
    #     data_x=t_data_x,
    #     data_a=t_data_y,
    #     data_b=t_data_y,
    #     out_file=r'D:\nsmc\cross_data\test\test_timeseries_omb.png', title=t_title,
    #     y_label=t_y_label,
    #     y_range=t_y_range,
    #     y_interval=t_y_interval,
    #     ymd=None, ymd_start='20180101', ymd_end='20200403',
    #     annotate=None,
    #     plot_zeroline=False)

    # ##### 测试 plot_statistics_analysis
    # from lib_gsics.lib_test import get_statistics_analysis_test_data
    # t_data_x, t_data_y = get_statistics_analysis_test_data(1000)
    # t_x_range = [-1, 1]
    # t_title = 'title\ntitle'
    # t_y_label1 = 'y_label'
    # t_y_range1 = [-4, 4]
    # t_y_range2 = [0, 7]
    # t_y_interval1 = 1
    # t_y_interval2 = 1
    # t_x_interval = 0.2
    #
    # plot_statistics_analysis(
    #         out_file=r'D:\nsmc\cross_data\test\test_statistics_analysis.png',
    #         title=t_title,
    #         x_data=t_data_x,
    #         y_data=t_data_y,
    #         x_label=t_y_label1,
    #         y_label1=t_y_label1,
    #         y_label2=t_y_label1,
    #         x_range=t_x_range,
    #         y_range1=t_y_range1,
    #         y_range2=t_y_range2,
    #         x_interval=t_x_interval,
    #         y_interval1=t_y_interval1,
    #         y_interval2=t_y_interval2,
    #         bar_step=0.1,
    #         bar_width=0.08,
    #         ymd='20180101',
    #         plot_background_fill=True,
    #         reference=0.4)

    # # #### 测试 plot_statistics_analysis
    # from lib_gsics.lib_test import get_statistics_analysis_test_data
    # t_data_x1, t_data_y1 = get_statistics_analysis_test_data(1000)
    # t_data_x2, t_data_y2 = get_statistics_analysis_test_data(500)
    # t_data_x3, t_data_y3 = get_statistics_analysis_test_data(300)
    # t_x_range = [-1, 1]
    # t_title = 'title\ntitle'
    # t_y_label1 = 'label'
    # t_x_range1 = [0, 24]
    # t_y_range1 = [-4, 4]
    # t_y_range2 = [0, 7]
    # t_y_interval1 = 1
    # t_y_interval2 = 1
    # t_x_interval = 1
    # t_labels = ['1', '2', '3']
    #
    # plot_hour_analysis(
    #     x_data1=t_data_x1,
    #     x_data2=t_data_x2,
    #     x_data3=t_data_x3,
    #     y_data1=t_data_y1,
    #     y_data2=t_data_y2,
    #     y_data3=t_data_y3,
    #     out_file=r'D:\nsmc\cross_data\test\test_hour_analysis.png',
    #     title=t_title,
    #     x_label=t_y_label1,
    #     y_label1=t_y_label1, y_label2=t_y_label1,
    #     x_range=t_x_range1,
    #     y_range1=t_y_range1,
    #     y_range2=t_y_range2,
    #     x_interval=t_x_interval,
    #     y_interval1=t_y_interval1,
    #     y_interval2=t_y_interval2,
    #     labels1=t_labels,
    #     annotate1=None,
    #     annotate2=None,
    #     bar_step=1,
    #     ymd='20180101',
    #     plot_background_fill=True,
    # )

    # ####### 测试 plot_map_distribution ##########
    test_x = np.array([1, 2, 3, 4, 5])
    test_y = np.array([1, 2, 3, 4, 5])
    title = 'asdfadsfasfdfasdfdasfsdafdasfdsfasdfdsfdsafasdf'
    out_file = 'test/test.png'
    plot_map_distribution(test_x, test_y, test_y, title=title, out_file=out_file, vmin=0, vmax=5)
