#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/11/29 9:53
# @Author  : NingAnMe <ninganme@qq.com>
import os
from lib.lib_database import exist_result_data, add_result_data
from correct.RunCorrect import ForecastDataPerday, CaculateNCLine


def fy4a_1km_correct(in_file, out_file, obs_dir, temp_dir,
                     resultid, planid, datatime, resolution_type):
    print('<<< 1km correct: {}'.format(in_file))

    area_type = 'Full_DISK'
    if os.path.isfile(out_file):
        print('数据已经存在: {}'.format(out_file))
        if not exist_result_data(resultid=resultid, datatime=datatime,
                                 resolution_type=resolution_type,
                                 area_type=area_type):
            add_result_data(resultid=resultid, planid=planid, address=out_file, datatime=datatime,
                            resolution_type=resolution_type, area_type=area_type)
        return

    runday = datatime.strftime('%Y%m%d')

    runhour = int(datatime.strftime("%H"))

    if not os.path.isdir(temp_dir):
        os.makedirs(temp_dir)
    flag = ForecastDataPerday(obs_dir=obs_dir, mid_dir=temp_dir, runday=runday)
    if not flag:
        print(f'没有足够的MID数据：{runday}{runhour}0000')

    if flag:
        CaculateNCLine(nc_file=in_file, mid_dir=temp_dir, out_file=out_file, runday=runday, runhour=runhour)

    if os.path.isfile(out_file) and not exist_result_data(resultid=resultid, datatime=datatime,
                                                          resolution_type=resolution_type,
                                                          area_type=area_type):
        add_result_data(resultid=resultid, planid=planid, address=out_file, datatime=datatime,
                        resolution_type=resolution_type, area_type=area_type)

    return 0
