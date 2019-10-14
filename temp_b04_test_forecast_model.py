#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/10/10 10:20
# @Author  : AnNing
from collections import OrderedDict
from datetime import datetime
import re
import os
import h5py
import numpy as np
from lib.lib_io import get_files_by_date


from keras.models import load_model
"""
目标，准备（sample，timestep， datashape， channels）的数据
"""
timestep = 4  # 设置步长
forecast_step = 7  # 设置预测的时长
width = 63
length = 63
channels = 2


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


in_path = r'C:\D\GoogleDrive\FY4AForecast\20190630'
in_files = get_files_by_date(in_path)
in_files.sort()

count_files = len(in_files)
if count_files <= 0:
    exit()
print('文件数量：{}'.format(count_files))

ssi_arrays = np.zeros((count_files, width, length), dtype=np.float32)
g0_arrays = np.zeros((count_files, width, length), dtype=np.float32)
ssi_scalars = np.zeros((count_files, 1), dtype=np.float32)
ssi_dates = np.zeros(count_files, dtype=np.object)

result = OrderedDict()
for i, in_file in enumerate(in_files):
    file_loader = FY4AExtractFileLoader(in_file)
    datetime_ = file_loader.get_datetime()
    day = datetime_.timetuple()[7]
    if result.get(day) is None:
        result[day] = {
            'ssi_array': None,
            'ssi_scalar': None,
            'ssi_date': None,
            'g0_array': None,
        }
    ssi_array = file_loader.get_ssi_array()[:]
    if result[day]['ssi_array'] is None:
        result[day]['ssi_array'] = ssi_array
    else:
        result[day]['ssi_array'] = np.concatenate((result[day]['ssi_array'], ssi_array))

    g0_array = file_loader.get_g0_array()[:]
    if result[day]['g0_array'] is None:
        result[day]['g0_array'] = g0_array
    else:
        result[day]['g0_array'] = np.concatenate((result[day]['g0_array'], g0_array))

    ssi_scalar = file_loader.get_ssi_scalar()
    if result[day]['ssi_scalar'] is None:
        result[day]['ssi_scalar'] = ssi_scalar
    else:
        result[day]['ssi_scalar'] = np.concatenate((result[day]['ssi_scalar'], ssi_scalar))

# ########################## 制作训练使用的样本数据 ##########################
date_start = ssi_dates[0]
date_end = ssi_dates[-1]

samples = 0
for k, v in result.items():
    delta = len(v['ssi_scalar']) - forecast_step - timestep
    if delta > 0:
        samples += delta

print('样本数量: {}'.format(samples))
train_x = np.zeros((samples, timestep, width, length, channels), dtype=np.float32)
train_y = np.zeros((samples, forecast_step))

sample = 0
for k, v in result.items():
    d_length = len(v['ssi_scalar'])
    for i in range(d_length):
        if i + timestep + forecast_step < d_length:
            ssi_array_tmp = v['ssi_array'][i:i + timestep]
            g0_array_tmp = v['g0_array'][i:i + timestep]
            train_y_tmp = v['ssi_scalar'][i + timestep:i + timestep + forecast_step].reshape(-1)

            train_x[sample, ::, ::, ::, 0] = ssi_array_tmp
            train_x[sample, ::, ::, ::, 1] = g0_array_tmp
            train_y[sample, ::] = train_y_tmp
            sample += 1

train_x[np.isnan(train_x)] = 0
train_y[np.isnan(train_y)] = 0
print(train_x.shape)
# print(train_x[0])
print(train_y.shape)

google_drive = r'C:\D\GoogleDrive'

model_number = 2
model_name = 'model{}'.format(model_number)
model_outfile = os.path.join(google_drive, 'model/nice_model{}_step{}.h5'.format(model_number, forecast_step))
model = load_model(model_outfile)

# for x in train_x:
#     print(x)

result = model.predict(train_x)
print(result.shape)

for y, y_hat in zip(train_y, result):
    print()
    print(y, y_hat)

for y, y_hat in zip(train_y[0], result[0]):
    print('{:.04f} {:.04f}'.format(y, y_hat))
# for y, y_hat in zip(train_y[0+forecast_step], result[0+forecast_step]):
#     print('{:08.04f} {:08.04f}'.format(y, y_hat))
