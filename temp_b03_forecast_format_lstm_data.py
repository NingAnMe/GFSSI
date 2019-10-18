#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/10/10 10:20
# @Author  : AnNing
from collections import OrderedDict
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
import os
import h5py
import numpy as np

"""
#This script demonstrates the use of a convolutional LSTM network.

This network is used to predict the next frame of an artificially
generated movie which contains moving squares.
"""
from keras.models import Sequential
from keras.layers import Flatten, LSTM, Dense, MaxPooling3D, TimeDistributed
from keras.layers.convolutional import Conv3D, Conv2D, Conv1D
from keras.layers.convolutional_recurrent import ConvLSTM2D
from keras.layers.normalization import BatchNormalization
from keras.models import load_model

from lib.lib_io import get_files_by_date

"""
目标，准备（sample，timestep， datashape， channels）的数据
"""
timestep = 5  # 设置步长
forecast_step = 9  # 设置预测的时长
width = length = 63  # 数据大小
channels = 2

hours = 14  # 一共使用每天14个小时的数据
hour_start = 6  # 从6点开始

# We create a layer which take as input movies of shape
# (n_frames, width, height, channels) and returns a movie
# of identical shape.
def model1():
    seq = Sequential()
    seq.add(ConvLSTM2D(filters=40, kernel_size=(3, 3),
                       input_shape=(timestep, width, length, channels),
                       padding='same', return_sequences=True))
    seq.add(BatchNormalization())

    seq.add(ConvLSTM2D(filters=40, kernel_size=(3, 3),
                       padding='same', return_sequences=True))
    seq.add(BatchNormalization())

    seq.add(MaxPooling3D(pool_size=(1, 3, 3)))
    seq.add(BatchNormalization())

    seq.add(Flatten())
    seq.add(Dense(forecast_step))
    seq.compile(loss='mse', optimizer='adadelta')
    print(seq.summary())
    return seq


def model2():
    seq = Sequential()
    seq.add(ConvLSTM2D(filters=40, kernel_size=(3, 3),
                       input_shape=(timestep, width, length, channels),
                       padding='same', return_sequences=True))
    seq.add(BatchNormalization())

    seq.add(ConvLSTM2D(filters=40, kernel_size=(3, 3),
                       padding='same', return_sequences=True))
    seq.add(BatchNormalization())

    seq.add(Conv3D(filters=2, kernel_size=(3, 3, 3),
                   padding='same', data_format='channels_last'))
    seq.add(BatchNormalization())
    seq.add(MaxPooling3D(pool_size=(1, 3, 3)))

    seq.add(Flatten())
    seq.add(Dense(forecast_step))
    seq.compile(loss='mse', optimizer='adadelta')
    print(seq.summary())
    return seq


def model3():
    seq = Sequential()
    seq.add(ConvLSTM2D(filters=40, kernel_size=(3, 3),
                       input_shape=(timestep, width, length, channels),
                       padding='same', return_sequences=True))
    seq.add(BatchNormalization())

    seq.add(Conv3D(filters=2, kernel_size=(3, 3, 3),
                   padding='same', data_format='channels_last'))
    seq.add(BatchNormalization())
    seq.add(MaxPooling3D(pool_size=(2, 3, 3)))

    seq.add(Flatten())
    seq.add(Dense(forecast_step))
    seq.compile(loss='mse', optimizer='adadelta')
    print(seq.summary())
    return seq


class FY4AExtractFileLoader:
    def __init__(self, infile):
        self.infile = infile

    def get_datetime(self):
        pattern = r'.*MULT_NOM_(\d{14})'
        result = re.match(pattern, self.infile)
        if result is not None:
            return datetime.strptime(result.groups()[0], '%Y%m%d%H%M%S')

    def get_ssi_array(self):
        with h5py.File(self.infile, 'r') as hdf5:
            return hdf5.get('data_x')[:]

    def get_g0_array(self):
        with h5py.File(self.infile, 'r') as hdf5:
            return hdf5.get('data_g0')[:]

    def get_ssi_scalar(self):
        with h5py.File(self.infile, 'r') as hdf5:
            return hdf5.get('data_y')[:]


# root_path = '/content/drive/My Drive/'
root_path = r'C:\D\GoogleDrive'
# in_path = os.path.join(root_path, 'FY4AForecast')
in_path = os.path.join(root_path, 'FY4AForecast_verify')

fix_names = os.listdir(in_path)

result = OrderedDict()
for fix_name in fix_names:
    print(fix_name)
    in_path_fix = os.path.join(in_path, fix_name)
    in_files = get_files_by_date(in_path_fix)
    in_files.sort()

    count_files = len(in_files)
    if count_files <= 0:
        exit()
    print('文件数量：{}'.format(count_files))

    ssi_arrays = np.zeros((count_files, width, length), dtype=np.float32)
    g0_arrays = np.zeros((count_files, width, length), dtype=np.float32)
    ssi_scalars = np.zeros((count_files, 1), dtype=np.float32)
    ssi_dates = np.zeros(count_files, dtype=np.object)

    hours = 14  # 使用每天14个小时的数据
    for i, in_file in enumerate(in_files):
        file_loader = FY4AExtractFileLoader(in_file)
        datetime_ = file_loader.get_datetime()
        datetime_ = datetime_ + relativedelta(hours=8)  # 修改世界时为北京时
        day = datetime_.timetuple()[7]
        hour = datetime_.hour
        if result.get(fix_name) is None:
            result[fix_name] = dict()
        if result[fix_name].get(day) is None:
            result[fix_name][day] = dict()
        if result[fix_name][day].get(hour) is None:
            result[fix_name][day][hour] = dict()
        ssi_array = file_loader.get_ssi_array()[:]
        result[fix_name][day][hour]['ssi_array'] = ssi_array

        g0_array = file_loader.get_g0_array()[:]
        result[fix_name][day][hour]['g0_array'] = g0_array

        ssi_scalar = file_loader.get_ssi_scalar()
        result[fix_name][day][hour]['ssi_scalar'] = ssi_scalar

        result[fix_name][day][hour]['ssi_date'] = datetime_

# ########################## 制作每日预测训练使用的样本数据 ##########################
sample_count = 0
for fix_name in result.keys():
    sample_count += len(result[fix_name])
print('样本数量: {}'.format(sample_count))
train_x = np.zeros((sample_count, timestep, width, length, channels), dtype=np.float32)
train_y = np.zeros((sample_count, forecast_step), dtype=np.float32)

sample = 0
for fix_name, result_fix in result.items():
    for k, v in result_fix.items():
        for j in range(hours):
            hour = j + 6  # 从早上六点开始
            data_hour = v.get(hour)
            if data_hour is not None:
                if hour_start <= hour < hour_start + timestep:
                    train_x[sample, hour-hour_start, ::, ::, 0] = v[hour]['ssi_array']
                    train_x[sample, hour-hour_start, ::, ::, 1] = v[hour]['g0_array']
                elif hour_start + timestep <= hour < hour_start + timestep + forecast_step:
                    train_y[sample, hour-hour_start-timestep] = v[hour]['ssi_scalar']
        sample += 1

train_x[np.isnan(train_x)] = 0
train_y[np.isnan(train_y)] = 0
# ########################## 制作4小时或者7小时预测训练使用的样本数据 ##########################
# date_start = ssi_dates[0]
# date_end = ssi_dates[-1]
#
# samples = 0
# for k, v in result.items():
#     delta = len(v['ssi_scalar']) - forecast_step - timestep
#     if delta > 0:
#         samples += delta
#
# print('样本数量: {}'.format(samples))
# train_x = np.zeros((samples, timestep, width, length, channels), dtype=np.float32)
# train_y = np.zeros((samples, forecast_step))
#
# sample = 0
# for k, v in result.items():
#     d_length = len(v['ssi_scalar'])
#     for i in range(d_length):
#         if i + timestep + forecast_step < d_length:
#             ssi_array_tmp = v['ssi_array'][i:i + timestep]
#             g0_array_tmp = v['g0_array'][i:i + timestep]
#             train_y_tmp = v['ssi_scalar'][i + timestep:i + timestep + forecast_step].reshape(-1)
#
#             train_x[sample, ::, ::, ::, 0] = ssi_array_tmp
#             train_x[sample, ::, ::, ::, 1] = g0_array_tmp
#             train_y[sample, ::] = train_y_tmp
#             sample += 1
#
# train_x[np.isnan(train_x)] = 0
# train_y[np.isnan(train_y)] = 0
# print(train_x.shape)
# print(train_x[0])
# print(train_y.shape)


# # ########################## 训练模型 ##########################
# model_number = 2
# model_name = 'model{}'.format(model_number)
# model_outfile = os.path.join(root_path, 'model/nice_model{}_step{}.h5'.format(model_number, forecast_step))
# if os.path.isfile(model_outfile):
#     model = load_model(model_outfile)
# else:
#     model = eval(model_name)()
# model.fit(train_x, train_y, batch_size=32,
#           epochs=150, validation_split=0.1)
# if not os.path.isdir('model'):
#     os.makedirs('model')
# model.save(model_outfile)


# ########################### 验证模型 ##########################
google_drive = r'C:\D\GoogleDrive'
model_number = 2
model_name = 'model{}'.format(model_number)
model_outfile = os.path.join(google_drive, 'model/nice_model{}_step{}.h5'.format(model_number, forecast_step))
model = load_model(model_outfile)
result = model.predict(train_x)
print(result.shape)

for y, y_hat in zip(train_y, result):
    print()
    print(y, y_hat)

import matplotlib.pyplot as plt
for i in range(len(train_y)):
    print('_' * 10)
    for y, y_hat in zip(train_y[i], result[i]):
        print('{:08.04f} {:08.04f}'.format(y, y_hat))
    plt.plot(train_y[i], label='live')
    plt.plot(result[i], label='forecast')
    plt.legend()
    plt.show()
    plt.close()
    print(np.mean(train_y[i]), np.mean(result[i]))
    print('*' * 10)
