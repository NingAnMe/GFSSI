# coding: utf-8
"""
Created on 2018-04-20

@author: anning
"""
import os
from math import floor, ceil
from datetime import datetime

import numpy as np
from scipy import stats
import matplotlib as mpl

mpl.use("Agg")  # 必须加这个字段，否则引用 pyplot 服务器会报错，服务器上面没有 TK

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
from matplotlib.font_manager import FontProperties
from mpl_toolkits.basemap import Basemap


def get_ds_font(fontName="OpenSans-Regular.ttf"):
    """
    载入字体
    "OpenSans-Regular.ttf"
    "simhei.ttf"
    "微软雅黑.ttf"
    """
    selfpath = os.path.split(os.path.realpath(__file__))[0]
    font0 = FontProperties()
    font_path = os.path.join(selfpath, "FNT", fontName)
    if os.path.isfile(font_path):
        font0.set_file(font_path)
        return font0
    return None


FONT0 = get_ds_font()
FONT1 = get_ds_font()
FONT_MONO = get_ds_font("DroidSansMono.ttf")


def set_tick_font(ax, scale_size=11, color="#000000"):
    """
    设定刻度的字体
    """
    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_fontproperties(FONT0)
        tick.label1.set_fontsize(scale_size)
        tick.label1.set_color(color)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontproperties(FONT0)
        tick.label1.set_fontsize(scale_size)
        tick.label1.set_color(color)


def add_title(titledict):
    """
    添加大标题和xy轴名称
    """
    tt = plt.title(titledict["title"], fontsize=11, fontproperties=FONT0)
    tt.set_y(1.01)  # set gap space below title and subplot
    if "xlabel" in titledict.keys() and titledict["xlabel"] != "":
        plt.xlabel(titledict["xlabel"], fontsize=11, fontproperties=FONT0)
    if "ylabel" in titledict.keys() and titledict["ylabel"] != "":
        plt.ylabel(titledict["ylabel"], fontsize=11, fontproperties=FONT0)


def add_label(ax, label, local, fontsize=11, fontproperties=FONT0):
    """
    添加子图的标签
    :param fontproperties:
    :param fontsize:
    :param ax:
    :param label:
    :param local:
    :return:
    """
    if label is None:
        return
    if local == "xlabel":
        ax.set_xlabel(label, fontsize=fontsize, fontproperties=fontproperties)
    elif local == "ylabel":
        ax.set_ylabel(label, fontsize=fontsize, fontproperties=fontproperties)


def add_annotate(ax, strlist, local, color="#000000", fontsize=11):
    """
    添加上方注释文字
    loc must be "left" or "right"
    格式 ["annotate1", "annotate2"]
    """
    if strlist is None:
        return
    xticklocs = ax.xaxis.get_ticklocs()
    yticklocs = ax.yaxis.get_ticklocs()

    x_step = (xticklocs[1] - xticklocs[0])
    x_toedge = x_step / 6.
    y_toedge = (yticklocs[1] - yticklocs[0]) / 6.

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    if local == "left":
        ax.text(xlim[0] + x_toedge, ylim[1] - y_toedge,
                "\n".join(strlist), ha="left", va="top", color=color,
                fontsize=fontsize, fontproperties=FONT_MONO)

    elif local == "right":
        ax.text(xlim[1] - x_toedge, ylim[1] - y_toedge,
                "\n".join(strlist), ha="right", va="top", color=color,
                fontsize=fontsize, fontproperties=FONT_MONO)

    elif local == "leftbottom":
        ax.text(xlim[0] + x_toedge, ylim[0] + y_toedge,
                "\n".join(strlist), ha="left", va="bottom", color=color,
                fontsize=fontsize, fontproperties=FONT_MONO)


def day_data_write(title, data, outFile):
    """
    title: 标题
    data： 数据体
    outFile:输出文件
    """

    allLines = []
    DICT_D = {}
    FilePath = os.path.dirname(outFile)
    if not os.path.exists(FilePath):
        os.makedirs(FilePath)

    if os.path.isfile(outFile) and os.path.getsize(outFile) != 0:
        fp = open(outFile, "r")
        fp.readline()
        Lines = fp.readlines()
        fp.close()
        # 使用字典特性，保证时间唯一，读取数据
        for Line in Lines:
            DICT_D[Line[:8]] = Line[8:]
        # 添加或更改数据
        Line = data
        DICT_D[Line[:8]] = Line[8:]
        # 按照时间排序

        newLines = sorted(DICT_D.iteritems(), key=lambda d: d[0], reverse=False)
        for i in xrange(len(newLines)):
            allLines.append(str(newLines[i][0]) + str(newLines[i][1]))
        fp = open(outFile, "w")
        fp.write(title)
        fp.writelines(allLines)
        fp.close()
    else:
        fp = open(outFile, "w")
        fp.write(title)
        fp.writelines(data)
        fp.close()


def get_bar_data(xx, delta, Tmin, Tmax, step):
    T_seg = []
    mean_seg = []
    std_seg = []
    sampleNums = []
    for i in np.arange(Tmin, Tmax, step):
        idx = np.where(np.logical_and(xx >= i, xx < (i + step)))[0]

        if idx.size > 0:
            DTb_block = delta[idx]
        else:
            continue

        mean1 = np.mean(DTb_block)
        std1 = np.std(DTb_block)

        idx1 = np.where((abs(DTb_block - mean1) < std1))[0]  # 去掉偏差大于std的点
        if idx1.size > 0:
            DTb_block = DTb_block[idx1]
            mean_seg.append(np.mean(DTb_block))
            std_seg.append(np.std(DTb_block))
            sampleNums.append(len(DTb_block))
        else:
            mean_seg.append(0)
            std_seg.append(0)
            sampleNums.append(0)
        T_seg.append(i + step / 2.)

    return np.array(T_seg), np.array(mean_seg), np.array(std_seg), np.array(
        sampleNums)


def get_cabr_data(cbar_file):
    """
    读取日的 CABR 文件，返回 np.array
    :param cbar_file:
    :return:
    """
    try:
        names = ("date", "count", "slope", "s_std", "intercept", "i_std", "rsquared", "r_std")
        formats = ("object", "i4", "f4", "f4", "f4", "f4", "f4", "f4")
        data = np.loadtxt(cbar_file,
                          converters={0: lambda x: datetime.strptime(x, "%Y%m%d")},
                          dtype={"names": names,
                                 "formats": formats},
                          skiprows=1, ndmin=1)
    except IndexError:
        names = ("date", "count", "slope", "intercept", "rsquared")
        formats = ("object", "i4", "f4", "f4", "f4")
        data = np.loadtxt(cbar_file,
                          converters={0: lambda x: datetime.strptime(x, "%Y%m%d")},
                          dtype={"names": names,
                                 "formats": formats},
                          skiprows=1, ndmin=1)

    return data


def get_bias_data(md_file):
    """
    读取日的 MD 文件，返回 np.array
    :param md_file:
    :return:
    """
    try:
        names = ("date", "bias", "bias_std", "md", "md_std")
        formats = ("object", "f4", "f4", "f4", "f4")
        data = np.loadtxt(md_file,
                          converters={0: lambda x: datetime.strptime(x, "%Y%m%d")},
                          dtype={"names": names,
                                 "formats": formats},
                          skiprows=1, ndmin=1)
    except IndexError:
        names = ("date", "bias", "md")
        formats = ("object", "f4", "f4")
        data = np.loadtxt(md_file,
                          converters={0: lambda x: datetime.strptime(x, "%Y%m%d")},
                          dtype={"names": names,
                                 "formats": formats},
                          skiprows=1, ndmin=1)
    return data


def bias_information(x, y, boundary=None, bias_range=1):
    """
    # 过滤 range%10 范围的值，计算偏差信息
    # MeanBias( <= 10 % Range) = MD±Std @ MT
    # MeanBias( > 10 % Range) = MD±Std @ MT
    :param bias_range:
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
    md_greater = delta_greater.mean()  # 偏差均值
    std_greater = delta_greater.std()  # 偏差 std
    mt_greater = x_greater.mean()  # 样本均值

    md_lower = delta_lower.mean()
    std_lower = delta_lower.std()
    mt_lower = x_lower.mean()

    # 格式化数据
    info_lower = "MeanBias(<={:d}%Range)={:.4f}±{:.4f}@{:.4f}".format(
        int(bias_range * 100), md_lower, std_lower, mt_lower)
    info_greater = "MeanBias(>{:d}%Range) ={:.4f}±{:.4f}@{:.4f}".format(
        int(bias_range * 100), md_greater, std_greater, mt_greater)

    bias_info = {"md_greater": md_greater, "std_greater": std_greater,
                 "mt_greater": mt_greater,
                 "md_lower": md_lower, "std_lower": std_lower,
                 "mt_lower": mt_lower,
                 "info_lower": info_lower, "info_greater": info_greater}

    return bias_info


def set_x_locator(ax, xlim_min, xlim_max):
    day_range = (xlim_max - xlim_min).days
    if day_range <= 60:
        days = mdates.DayLocator(interval=(day_range / 6))
        ax.xaxis.set_major_locator(days)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    else:
        month_range = day_range / 30
        if month_range <= 12.:
            months = mdates.MonthLocator()  # every month
            ax.xaxis.set_major_locator(months)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        elif month_range <= 24.:
            months = mdates.MonthLocator(interval=2)
            ax.xaxis.set_major_locator(months)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        elif month_range <= 48.:
            months = mdates.MonthLocator(interval=4)
            ax.xaxis.set_major_locator(months)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        else:
            years = mdates.YearLocator()
            ax.xaxis.set_major_locator(years)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

        if month_range <= 48:
            add_year_xaxis(ax, xlim_min, xlim_max)


def add_year_xaxis(ax, xlim_min, xlim_max):
    """
    add year xaxis
    """
    if xlim_min.year == xlim_max.year:
        ax.set_xlabel(xlim_min.year, fontsize=11, fontproperties=FONT0)
        return
    newax = ax.twiny()
    newax.set_frame_on(True)
    newax.grid(False)
    newax.patch.set_visible(False)
    newax.xaxis.set_ticks_position("bottom")
    newax.xaxis.set_label_position("bottom")
    newax.set_xlim(xlim_min, xlim_max)
    newax.xaxis.set_major_locator(mdates.YearLocator())
    newax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    newax.spines["bottom"].set_position(("outward", 20))
    newax.spines["bottom"].set_linewidth(0.6)

    newax.tick_params(which="both", direction="in")
    set_tick_font(newax)
    newax.xaxis.set_tick_params(length=5)


def draw_regression(ax, x, y, label=None, ax_annotate=None, tick=None,
                    axislimit=None, locator=None,
                    diagonal=None, regressline=None, scatter_point=None,
                    density=None, ):
    """
    画回归线图
    :param tick:
    :param ax:
    :param x:
    :param y:
    :param label:
    :param ax_annotate:
    :param axislimit:
    :param locator:
    :param diagonal:
    :param regressline:
    :param scatter_point:
    :param density:
    :return:
    """
    if axislimit is not None:
        xlimit = axislimit.get("xlimit")
        ylimit = axislimit.get("ylimit")
        if xlimit is not None:
            xmin, xmax = xlimit
        else:
            xmin = floor(np.min(x))
            xmax = ceil(np.max(x))
        if ylimit is not None:
            ymin, ymax = ylimit
        else:
            ymin = floor(np.min(y))
            ymax = ceil(np.max(y))
    else:
        xmin = floor(np.min(x))
        xmax = ceil(np.max(x))
        ymin = floor(np.min(y))
        ymax = ceil(np.max(y))

    # 画对角线
    if diagonal is not None:
        diagonal_color = "#808080"
        diagonal_linewith = 1.2
        ax.plot([xmin, xmax], [ymin, ymax], color=diagonal_color,
                linewidth=diagonal_linewith)

    # 画回归线
    if regressline is not None:
        line_color = regressline.get("line_color")
        line_width = regressline.get("line_width")
        # 计算 a b
        ab = np.polyfit(x, y, 1)
        a = ab[0]
        b = ab[1]
        ax.plot([xmin, xmax], [xmin * a + b, xmax * a + b],
                color=line_color, linewidth=line_width, zorder=100)

    # 画散点
    if scatter_point is not None:
        alpha_value = 0.8  # 透明度
        marker_value = "o"  # 形状
        color_value = "b"  # 颜色
        ax.scatter(x, y, s=5, marker=marker_value, c=color_value, lw=0,
                   alpha=alpha_value)

    # 画密度点
    if density is not None:
        pos = np.vstack([x, y])
        kernel = stats.gaussian_kde(pos)
        z = kernel(pos)
        norm = plt.Normalize()
        norm.autoscale(z)
        density_size = density.get("size")
        density_alpha = density.get("alpha")
        density_marker = density.get("marker")
        ax.scatter(x, y, c=z, norm=norm, s=density_size, marker=density_marker,
                   cmap=plt.cm.jet, lw=0,
                   alpha=density_alpha)

    # 设定x y 轴的范围
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # 设定小刻度
    if locator is not None:
        major_locator_x = locator.get("locator_x")[0]
        minor_locator_x = locator.get("locator_x")[1]
        major_locator_y = locator.get("locator_y")[0]
        minor_locator_y = locator.get("locator_y")[1]

        major_x = (xmin, xmax)
        major_y = (ymin, ymax)
        xticklocs = ax.xaxis.get_ticklocs()
        yticklocs = ax.yaxis.get_ticklocs()
        if major_locator_x is not None:
            ax.xaxis.set_major_locator(
                MultipleLocator(
                    (major_x[1] - major_x[0]) / major_locator_x))
        if minor_locator_x is not None:
            ax.xaxis.set_minor_locator(
                MultipleLocator(
                    (xticklocs[1] - xticklocs[0]) / minor_locator_x))
        if major_locator_y is not None:
            ax.yaxis.set_major_locator(
                MultipleLocator(
                    (major_y[1] - major_y[0]) / major_locator_y))
        if minor_locator_y is not None:
            ax.yaxis.set_minor_locator(
                MultipleLocator(
                    (yticklocs[1] - yticklocs[0]) / minor_locator_y))

    # 注释，格式 ["annotate1", "annotate2"]
    if ax_annotate is not None:
        font_size = ax_annotate.get("fontsize", 10)
        add_annotate(ax, ax_annotate.get("left"), "left", fontsize=font_size)
        add_annotate(ax, ax_annotate.get("right"), "right", fontsize=font_size)

    # 标签
    if label is not None:
        font_size = label.get("fontsize", 11)
        add_label(ax, label.get("xlabel"), "xlabel", fontsize=font_size)  # x 轴标签
        add_label(ax, label.get("ylabel"), "ylabel", fontsize=font_size)  # y 轴标签

    # 设置 tick 字体
    if tick is not None:
        scale_size = tick.get("fontsize", 11)
    else:
        scale_size = 11
    set_tick_font(ax, scale_size=scale_size)


def draw_distribution(ax, x, y, label=None, ax_annotate=None, tick=None,
                      axislimit=None, locator=None,
                      avxline=None, zeroline=None, scatter_delta=None,
                      background_fill=None, regressline=None, ):
    """
    画偏差分布图
    :param tick:
    :param ax:
    :param x:
    :param y:
    :param label:
    :param ax_annotate:
    :param axislimit:
    :param locator:
    :param avxline:
    :param zeroline:
    :param scatter_delta:
    :param background_fill:
    :param regressline:
    :return:
    """
    if axislimit is not None:
        xlimit = axislimit.get("xlimit")
        ylimit = axislimit.get("ylimit")
        if xlimit is not None:
            xmin, xmax = xlimit
        else:
            xmin = floor(np.min(x))
            xmax = ceil(np.max(x))
        if ylimit is not None:
            ymin, ymax = ylimit
        else:
            ymin = floor(np.min(y))
            ymax = ceil(np.max(y))
    else:
        xmin = floor(np.min(x))
        xmax = ceil(np.max(x))
        ymin = floor(np.min(y))
        ymax = ceil(np.max(y))

    # 添加 y = 0 的线
    if zeroline is not None:
        zeroline_width = zeroline.get("line_width")
        zeroline_color = zeroline.get("line_color")
        ax.plot([xmin, xmax], [0, 0], color=zeroline_color,
                linewidth=zeroline_width)

    # 画偏差散点
    if scatter_delta is not None:
        delta = x - y  # 计算偏差
        scatter_size = scatter_delta.get("scatter_size")  # 大小
        scatter_alpha = 0.8  # 透明度
        scatter_marker = "o"  # 形状
        scatter_color = "b"  # 颜色
        ax.scatter(x, delta, s=scatter_size, marker=scatter_marker,
                   c=scatter_color, lw=0, alpha=scatter_alpha)

    # 画偏差回归线
    if regressline is not None:
        delta = x - y
        delta_ab = np.polyfit(x, delta, 1)
        delta_a = delta_ab[0]
        delta_b = delta_ab[1]
        regressline_x = [xmin, xmax]
        regressline_y = [xmin * delta_a + delta_b, xmax * delta_a + delta_b]

        regressline_color = "r"
        regressline_width = 1.2

        ax.plot(regressline_x, regressline_y,
                color=regressline_color, linewidth=regressline_width,
                zorder=100)

    # 画背景填充线
    if background_fill is not None:
        delta = x - y
        fill_color = background_fill.get("fill_color")
        fill_step = background_fill.get("fill_step")
        T_seg, mean_seg, std_seg, sampleNums = get_bar_data(x, delta, xmin,
                                                            xmax, fill_step)
        ax.plot(T_seg, mean_seg, "o-",
                ms=6, lw=0.6, c=fill_color,
                mew=0, zorder=50)
        ax.fill_between(T_seg, mean_seg - std_seg, mean_seg + std_seg,
                        facecolor=fill_color, edgecolor=fill_color,
                        interpolate=True, alpha=0.4, zorder=100)

    # 画 avx 注释线
    if avxline is not None:
        avxline_x = avxline.get("line_x")
        avxline_color = avxline.get("line_color")
        avxline_width = 0.7
        avxline_word = avxline.get("word")
        avxline_wordcolor = avxline.get("word_color")
        avxline_wordlocal = avxline.get("word_location")
        avxline_wordsize = avxline.get("word_size")
        ax.axvline(x=avxline_x, color=avxline_color, lw=avxline_width)
        ax.annotate(avxline_word, avxline_wordlocal,
                    va="top", ha="center", color=avxline_wordcolor,
                    size=avxline_wordsize, fontproperties=FONT_MONO)

    # 设定x y 轴的范围
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # 设定小刻度
    if locator is not None:
        major_locator_x = locator.get("locator_x")[0]
        minor_locator_x = locator.get("locator_x")[1]
        major_locator_y = locator.get("locator_y")[0]
        minor_locator_y = locator.get("locator_y")[1]

        major_x = (xmin, xmax)
        major_y = (ymin, ymax)
        xticklocs = ax.xaxis.get_ticklocs()
        yticklocs = ax.yaxis.get_ticklocs()
        if major_locator_x is not None:
            ax.xaxis.set_major_locator(
                MultipleLocator(
                    (major_x[1] - major_x[0]) / major_locator_x))
        if minor_locator_x is not None:
            ax.xaxis.set_minor_locator(
                MultipleLocator(
                    (xticklocs[1] - xticklocs[0]) / minor_locator_x))
        if major_locator_y is not None:
            ax.yaxis.set_major_locator(
                MultipleLocator(
                    (major_y[1] - major_y[0]) / major_locator_y))
        if minor_locator_y is not None:
            ax.yaxis.set_minor_locator(
                MultipleLocator(
                    (yticklocs[1] - yticklocs[0]) / minor_locator_y))

    # 注释，格式 ["annotate1", "annotate2"]
    if ax_annotate is not None:
        font_size = ax_annotate.get("fontsize", 10)
        add_annotate(ax, ax_annotate.get("left"), "left", fontsize=font_size)
        add_annotate(ax, ax_annotate.get("right"), "right", fontsize=font_size)
        add_annotate(ax, ax_annotate.get("leftbottom"), "leftbottom", fontsize=font_size)

    # 标签
    if label is not None:
        font_size = label.get("fontsize", 11)
        add_label(ax, label.get("xlabel"), "xlabel", fontsize=font_size)  # x 轴标签
        add_label(ax, label.get("ylabel"), "ylabel", fontsize=font_size)  # y 轴标签

    # 设置 tick 字体
    if tick is not None:
        scale_size = tick.get("fontsize", 11)
    else:
        scale_size = 11
    set_tick_font(ax, scale_size=scale_size)


def draw_histogram(ax, x, label=None, ax_annotate=None, tick=None,
                   axislimit=None, locator=None,
                   histogram=None, ):
    """
    画直方图
    :param tick:
    :param ax:
    :param x:
    :param label:
    :param ax_annotate:
    :param axislimit:
    :param locator:
    :param histogram:
    :return:
    """
    if axislimit is not None:
        xlimit = axislimit.get("xlimit")
        # ylimit = axislimit.get("ylimit")
        if xlimit is not None:
            xmin, xmax = xlimit
        else:
            xmin = floor(np.min(x))
            xmax = ceil(np.max(x))
        # if ylimit is not None:
        #     ymin, ymax = ylimit
        # else:
        #     ymin = floor(np.min(y))
        #     ymax = ceil(np.max(y))
    else:
        xmin = floor(np.min(x))
        xmax = ceil(np.max(x))
        # ymin = floor(np.min(y))
        # ymax = ceil(np.max(y))

    if histogram is not None:
        hist_alpha = histogram.get("alpha")
        hist_color = histogram.get("color")
        hist_label = histogram.get("label")
        hist_bins = histogram.get("bins")
        hist_label_size = histogram.get("fontsize", 10)

        ax.hist(x, hist_bins, range=(xmin, xmax), histtype="bar",
                color=hist_color,
                label=hist_label, alpha=hist_alpha)
        ax.legend(prop={"size": hist_label_size})

    # 设定x y 轴的范围
    ax.set_xlim(xmin, xmax)
    # ax.set_ylim(ymin, ymax)  # 画直方图的时候不设置 y 轴的范围

    # 设定小刻度
    if locator is not None:
        major_locator_x = locator.get("locator_x")[0]
        minor_locator_x = locator.get("locator_x")[1]
        # major_locator_y = locator.get("locator_y")[0]
        minor_locator_y = locator.get("locator_y")[1]

        major_x = (xmin, xmax)
        # major_y = (ymin, ymax)
        xticklocs = ax.xaxis.get_ticklocs()
        yticklocs = ax.yaxis.get_ticklocs()

        if major_locator_x is not None:
            ax.xaxis.set_major_locator(
                MultipleLocator(
                    (major_x[1] - major_x[0]) / major_locator_x))
        if minor_locator_x is not None:
            ax.xaxis.set_minor_locator(
                MultipleLocator(
                    (xticklocs[1] - xticklocs[0]) / minor_locator_x))
        # 画直方图的时候不调整 y 轴主刻度的范围大小
        # if major_locator_y is not None:
        #     ax.yaxis.set_major_locator(
        #         MultipleLocator((major_y[1] - major_y[0]) / major_locator_y))
        if minor_locator_y is not None:
            ax.yaxis.set_minor_locator(
                MultipleLocator(
                    (yticklocs[1] - yticklocs[0]) / minor_locator_y))

    # 注释，格式 ["annotate1", "annotate2"]
    if ax_annotate is not None:
        font_size = ax_annotate.get("fontsize", 10)
        add_annotate(ax, ax_annotate.get("left"), "left", fontsize=font_size)
        add_annotate(ax, ax_annotate.get("right"), "right", fontsize=font_size)

    # 标签
    if label is not None:
        font_size = label.get("fontsize", 11)
        add_label(ax, label.get("xlabel"), "xlabel", fontsize=font_size)  # x 轴标签
        add_label(ax, label.get("ylabel"), "ylabel", fontsize=font_size)  # y 轴标签

    # 设置 tick 字体
    if tick is not None:
        scale_size = tick.get("fontsize", 11)
    else:
        scale_size = 11
    set_tick_font(ax, scale_size=scale_size)


def draw_bar(ax, x, y, label=None, ax_annotate=None, tick=None,
             axislimit=None, locator=None,
             bar=None
             ):
    """
    画带有数字的 bar 图
    :param tick:
    :param ax:
    :param x:
    :param y:
    :param label:
    :param ax_annotate:
    :param axislimit:
    :param locator:
    :param bar:
    :return:
    """
    if axislimit is not None:
        xlimit = axislimit.get("xlimit")
        ylimit = axislimit.get("ylimit")
        if xlimit is not None:
            xmin, xmax = xlimit
        else:
            xmin = floor(np.min(x))
            xmax = ceil(np.max(x))
        if ylimit is not None:
            ymin, ymax = ylimit
        else:
            ymin = floor(np.min(y))
            ymax = ceil(np.max(y))
    else:
        xmin = floor(np.min(x))
        xmax = ceil(np.max(x))
        ymin = floor(np.min(y))
        ymax = ceil(np.max(y))

    # 设定x y 轴的范围
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # 设定小刻度
    # 设定小刻度
    if locator is not None:
        major_locator_x = locator.get("locator_x")[0]
        minor_locator_x = locator.get("locator_x")[1]
        major_locator_y = locator.get("locator_y")[0]
        minor_locator_y = locator.get("locator_y")[1]

        major_x = (xmin, xmax)
        major_y = (ymin, ymax)
        xticklocs = ax.xaxis.get_ticklocs()
        yticklocs = ax.yaxis.get_ticklocs()
        if major_locator_x is not None:
            ax.xaxis.set_major_locator(
                MultipleLocator((major_x[1] - major_x[0]) / major_locator_x))
        if minor_locator_x is not None:
            ax.xaxis.set_minor_locator(
                MultipleLocator(
                    (xticklocs[1] - xticklocs[0]) / minor_locator_x))
        if major_locator_y is not None:
            ax.yaxis.set_major_locator(
                MultipleLocator((major_y[1] - major_y[0]) / major_locator_y))
        if minor_locator_y is not None:
            ax.yaxis.set_minor_locator(
                MultipleLocator(
                    (yticklocs[1] - yticklocs[0]) / minor_locator_y))

    if bar is not None:
        delta = x - y
        bar_step = bar.get("bar_step")
        bar_width = bar.get("bar_width")
        bar_color = bar.get("BlUE")
        T_seg, mean_seg, std_seg, sampleNums = get_bar_data(x, delta, xmin,
                                                            xmax, bar_step)
        plt.bar(T_seg, np.log10(sampleNums), width=bar_width, align="center",
                color=bar_color, linewidth=0)
        for i, T in enumerate(T_seg):
            if sampleNums[i] > 0:
                plt.text(T, np.log10(sampleNums[i]) + 0.2,
                         "%d" % int(sampleNums[i]), ha="center",
                         fontsize=6, fontproperties=FONT_MONO)

    # 注释，格式 ["annotate1", "annotate2"]
    if ax_annotate is not None:
        font_size = ax_annotate.get("fontsize", 10)
        add_annotate(ax, ax_annotate.get("left"), "left", fontsize=font_size)
        add_annotate(ax, ax_annotate.get("right"), "right", fontsize=font_size)

    # 标签
    if label is not None:
        font_size = label.get("fontsize", 11)
        add_label(ax, label.get("xlabel"), "xlabel", fontsize=font_size)  # x 轴标签
        add_label(ax, label.get("ylabel"), "ylabel", fontsize=font_size)  # y 轴标签

    # 设置 tick 字体
    if tick is not None:
        scale_size = tick.get("fontsize", 11)
    else:
        scale_size = 11
    set_tick_font(ax, scale_size=scale_size)


def draw_timeseries(ax, x, y, label=None, ax_annotate=None, tick=None,
                    axislimit=None, locator=None,
                    zeroline=None, timeseries=None,
                    background_fill=None,
                    ):
    if axislimit is not None:
        xlimit = axislimit.get("xlimit")
        ylimit = axislimit.get("ylimit")
        if xlimit is not None:
            xmin, xmax = xlimit
        else:
            xmin = floor(np.min(x))
            xmax = ceil(np.max(x))
        if ylimit is not None:
            ymin, ymax = ylimit
        else:
            ymin = floor(np.min(y))
            ymax = ceil(np.max(y))
    else:
        xmin = floor(np.min(x))
        xmax = ceil(np.max(x))
        ymin = floor(np.min(y))
        ymax = ceil(np.max(y))

    # 添加 y = 0 的线
    if zeroline is not None:
        zeroline_width = zeroline.get("line_width")
        zeroline_color = zeroline.get("line_color")
        ax.plot([xmin, xmax], [0, 0], color=zeroline_color,
                linewidth=zeroline_width)

    # 画时间序列图
    if timeseries is not None:
        ts_marker = timeseries.get("marker")
        ts_color = timeseries.get("color")
        ts_linewidth = timeseries.get("linewidth")
        ts_markersize = timeseries.get("markersize")
        ts_markerfacecolor = timeseries.get("markerfacecolor")
        ts_markeredgecolor = timeseries.get("markeredgecolor")
        ts_alpha = timeseries.get("alpha")
        ts_markeredgewidth = timeseries.get("markeredgewidth")
        ts_label = timeseries.get("label")
        ax.plot(x, y, ts_marker,
                ms=ts_markersize,
                lw=ts_linewidth,
                c=ts_color,
                markerfacecolor=ts_markerfacecolor,
                markeredgecolor=ts_markeredgecolor,
                alpha=ts_alpha,
                mew=ts_markeredgewidth,
                label=ts_label,
                zorder=100)

    if background_fill is not None:
        fill_color = background_fill.get("color")
        x_fill = background_fill.get("x")
        y_fill = background_fill.get("y")
        y1_fill = background_fill.get("y1")
        ax.fill_between(x_fill, y_fill, y1_fill,
                        facecolor=fill_color, edgecolor=fill_color,
                        interpolate=True, alpha=0.1, zorder=80)

    # 设定x y 轴的范围
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # 设定小刻度
    if locator is not None:
        major_locator_x = locator.get("locator_x")[0]
        minor_locator_x = locator.get("locator_x")[1]
        major_locator_y = locator.get("locator_y")[0]
        minor_locator_y = locator.get("locator_y")[1]

        major_x = (xmin, xmax)
        major_y = (ymin, ymax)
        xticklocs = ax.xaxis.get_ticklocs()
        yticklocs = ax.yaxis.get_ticklocs()
        if major_locator_x is not None:
            ax.xaxis.set_major_locator(
                MultipleLocator(
                    (major_x[1] - major_x[0]) / major_locator_x))
        if minor_locator_x is not None:
            ax.xaxis.set_minor_locator(
                MultipleLocator(
                    (xticklocs[1] - xticklocs[0]) / minor_locator_x))
        if major_locator_y is not None:
            ax.yaxis.set_major_locator(
                MultipleLocator(
                    (major_y[1] - major_y[0]) / major_locator_y))
        if minor_locator_y is not None:
            ax.yaxis.set_minor_locator(
                MultipleLocator(
                    (yticklocs[1] - yticklocs[0]) / minor_locator_y))

    # 注释，格式 ["annotate1", "annotate2"]
    if ax_annotate is not None:
        font_size = ax_annotate.get("fontsize", 10)
        add_annotate(ax, ax_annotate.get("left"), "left", fontsize=font_size)
        add_annotate(ax, ax_annotate.get("right"), "right", fontsize=font_size)

    # 标签
    if label is not None:
        font_size = label.get("fontsize", 11)
        add_label(ax, label.get("xlabel"), "xlabel", fontsize=font_size)  # x 轴标签
        add_label(ax, label.get("ylabel"), "ylabel", fontsize=font_size)  # y 轴标签

    # 设置 tick 字体
    if tick is not None:
        scale_size = tick.get("fontsize", 11)
    else:
        scale_size = 11
    set_tick_font(ax, scale_size=scale_size)

    set_x_locator(ax, xmin, xmax)


def get_dot_color(xlist, ylist):
    """
    取得color数组
    """
    divide = 200.  # 分成200份
    colors = np.zeros(len(xlist))
    xmin = floor(np.min(xlist))
    xmax = ceil(np.max(xlist))
    ymin = floor(np.min(ylist))
    ymax = ceil(np.max(ylist))

    xstep = (xmax - xmin) / divide
    ystep = (ymax - ymin) / divide

    x1 = xmin
    while x1 < xmax:
        x2 = x1 + xstep
        y1 = ymin
        while y1 < ymax:
            y2 = y1 + ystep
            condition = np.logical_and(xlist >= x1, xlist < x2)
            condition = np.logical_and(condition, ylist >= y1)
            condition = np.logical_and(condition, ylist < y2)

            colors[condition] = np.count_nonzero(condition)
            y1 = y2
        x1 = x2
    return colors
