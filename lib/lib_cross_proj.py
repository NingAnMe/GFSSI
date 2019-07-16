# -*- coding: utf-8 -*-

from math import ceil
from pyproj import Proj, transform
from PB.pb_space import deg2meter
import numpy as np

__description__ = u'静止和极轨通用匹配程序'
__author__ = 'wangpeng'
__date__ = '2018-09-06'
__version__ = '1.0.0_beat'


class prj_core(object):
    '''
    投影公共类
    '''

    def __init__(self, projstr, res, unit="m",
                 row=None, col=None, pt_tl=None, pt_br=None,
                 **kwargs):
        '''
        [args]:
        projstr proj4投影参数字符串 
        res     分辨率
        unit    分辨率单位，支持 m km deg，默认 m
        row     行数
        col     列数
        pt_tl   左上角经纬度元组， 形式如 (lon, lat)
        pt_br   右下角经纬度元组， 形式如 (lon, lat)

        row、 col 和  pt_tl、 pt_br 两对里必须传一对，用以确定网格大小， 不能都是None

        projstr 样例：
        1. 等经纬
           "+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +x_0=-half_res +y_0=half_res"
        2. 极射赤面
           "+proj=stere +ellps=clrk66 +lat_0=90 +lat_ts=70 +lon_0=0 +k_0=0.969858730377 +a=6371000 +units=m"
        3. 兰勃特等面积
           "+proj=laea +lat_0=-74.180000 +lon_0=-146.620000 +x_0=0 +y_0=0 +ellps=WGS84"
        4. 阿伯斯  (常用于中国区域)
           "+proj=aea +lat_0=0 +lon_0=105 +lat_1=25 +lat_2=47 +x_0=0 +y_0=0 +ellps=krass +a=6378245.0 +b=6356863.0"
        5. 待补充

        '''
        self.lut_dict = {}  # 查找表
        self.proj4str = projstr
        self.pfunc = Proj(self.proj4str)  # 转换函数
        # self.res 统一转换成单位米
        if unit == "m":
            self.res = res
        elif unit == "km":
            self.res = res * 1000
        elif unit == "deg":
            self.res = deg2meter(res)

        if row is not None and col is not None:
            self.row = row
            self.col = col
            self.x_tl = -self.col / 2. * self.res
            self.y_tl = self.row / 2. * self.res

        elif pt_tl is not None and pt_br is not None:
            self.x_tl, self.y_tl = self.pfunc(*pt_tl)
            self.x_br, self.y_br = self.pfunc(*pt_br)

            self.row = int(ceil((self.y_tl - self.y_br) / self.res)) + 1
            self.col = int(ceil((self.x_br - self.x_tl) / self.res)) + 1
        else:
            raise ValueError(
                "row、 col 和  pt_tl、 pt_br 两对里必须传一对，用以确定网格大小， 不能都是None")
#
        self.grid_lonslats()

    def lonslats2ij(self, lons, lats):
        '''
        '经纬度转行列号 lons,lats -> i,j
        '参数是n维数组 经纬度
        '返回值是n维数组 行列号
        '''
        if isinstance(lons, (list, tuple)):
            lons = np.array(lons)
        if isinstance(lats, (list, tuple)):
            lats = np.array(lats)

        if isinstance(lons, np.ndarray):
            assert lons.shape == lats.shape, \
                "lons and lats must have same shape."

            args_shape = lons.shape
            # 转成1维，因为proj只接收1维参数
            lons = lons.reshape((-1))
            lats = lats.reshape((-1))
            # 通过平面坐标系计算投影后的行和列
            x, y = self.pfunc(lons, lats)

            i = self.__y2i(y)
            j = self.__x2j(x)
            return i.reshape(args_shape), j.reshape(args_shape)
        else:
            x, y = self.pfunc(lons, lats)
            i = self.__y2i(y)
            j = self.__x2j(x)
            return i, j

    def __y2i(self, y):
        '''
        y 转 行号
        '''
        if isinstance(y, (list, tuple)):
            y = np.array(y)
        return np.rint((self.y_tl - y) / self.res).astype(int)

    def __x2j(self, x):
        '''
        x 转 列号
        '''
        if isinstance(x, (list, tuple)):
            x = np.array(x)
        return np.rint((x - self.x_tl) / self.res).astype(int)

    def grid_lonslats(self):
        '''
        '生成投影后网格 各格点的经纬度
        '''
        # 制作一个2维的矩阵
        i, j = np.mgrid[0:self.row:1, 0:self.col:1]
        y = self.__i2y(i)
        x = self.__j2x(j)

        # 把二维的x,y 转成1维，因为proj只接收1维参数
        x = x.reshape((-1))
        y = y.reshape((-1))
        lons, lats = self.pfunc(x, y, inverse=True)
        # 转回2维
        self.lons = lons.reshape((self.row, self.col))
        self.lats = lats.reshape((self.row, self.col))

    def __i2y(self, i):
        '''
        '行号 转 y
        '''
        if isinstance(i, (list, tuple)):
            i = np.array(i)

        y = self.y_tl - i * self.res
        return y

    def __j2x(self, j):
        '''
        '列号 转 x
        '''
        if isinstance(j, (list, tuple)):
            j = np.array(j)
        x = j * self.res + self.x_tl
        return x

    def create_lut(self, Lons, Lats, in_file):
        '''
        '创建投影查找表, 
        '即 源数据经纬度位置与投影后位置的对应关系
        '''
        if isinstance(Lons, (list, tuple)):
            Lons = np.array(Lons)
        if isinstance(Lats, (list, tuple)):
            Lats = np.array(Lats)
        assert Lons.shape == Lats.shape, \
            "Lons and Lats must have same shape."

        # 投影后的行列 proj1_i,proj1_j
        proj1_i, proj1_j = self.lonslats2ij(Lons, Lats)

        # 根据投影前数据别分获取源数据维度，制作一个和数据维度一致的数组，分别存放行号和列号
        # 原始数据的行列, data1_i, data1_j
        data1_row, data1_col = Lons.shape
        data1_i, data1_j = np.mgrid[0:data1_row:1, 0:data1_col:1]

        # 投影方格以外的数据过滤掉

        condition = np.logical_and.reduce((proj1_i >= 0, proj1_i < self.row,
                                           proj1_j >= 0, proj1_j < self.col))
        p1_i = proj1_i[condition]
        p1_j = proj1_j[condition]
        d1_i = data1_i[condition]
        d1_j = data1_j[condition]

        self.lut_dict[in_file] = [p1_i, p1_j, d1_i, d1_j]

    def transform2ij(self, proj_str1, x1, y1):
        '''
        '不同投影方式之间转换
        '返回值是整数
        '''
        args_shape = x1.shape
        x1 = np.array(x1).reshape((-1))  # 转成1维
        y1 = np.array(y1).reshape((-1))
        p1 = Proj(proj_str1)
        x2, y2 = transform(p1, self.pfunc, x1, y1)
        i = self.__y2i(y2)
        j = self.__x2j(x2)
        return i.reshape(args_shape), j.reshape(args_shape)
