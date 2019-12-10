#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import sys
import random
import step4_bin.CorrectClass as CorrectClass
import numpy as np
import h5py
import shutil

current_dir = os.path.dirname(os.path.abspath(__file__))
EXE_DIR = current_dir
gfssi_dir = os.path.dirname(current_dir)
sys.path.append(gfssi_dir)

from lib.lib_read_ssi import FY4ASSI
from lib.lib_constant import FY4A_1KM_CORRECT_LAT_LON_RANGE, STATION_LIST
from lib.lib_constant import FULL_VALUE
from lib.lib_constant import VARIFY_EXE, STATISTICS_EXE

from config import DEBUG

LatLonRange = FY4A_1KM_CORRECT_LAT_LON_RANGE


# 每日数据订正
# install:BIN文件夹所在目录；runday:所需运行日期
def ForecastDataPerday(obs_dir, mid_dir, runday):
    """
    输入：
        站点的经纬度信息StationList.txt
        三天站点的观测值ObsData
    输出：
        模型输出的校正数据：COR
    :param obs_dir: Obs数据的输入目录
    :param mid_dir:  临时结果目录
    :param runday:  所需运行的日期
    :return:
    """
    nday = 3  # 读代码注释：使用3天的站点数据进行建模

    # 获取数据所在目录,获取站点信息,获取建模日期
    staInfo = CorrectClass.staInfoGet(STATION_LIST)
    dateList = CorrectClass.calDateList(runday, nday)

    # 站点间关系处理
    staNearList = CorrectClass.staNearListGet(staInfo, obs_dir, dateList)

    # 在对应目录创建输出文件夹
    corFileName = mid_dir + r"/COR"
    if not os.path.exists(corFileName):
        os.mkdir(corFileName)
    # 删除MID文件夹的中间结果
    MID_dir = mid_dir + r"/MID"
    if not os.path.exists(MID_dir):
        os.mkdir(MID_dir)
    else:
        return

    corResultFileName = mid_dir + r"/COR" + r"/" + runday
    if not os.path.exists(corResultFileName):
        os.mkdir(corResultFileName)

    # 中间结果集
    DataAll = {}
    for ihour in range(24):
        DataAll[ihour] = []

    # 逐站点循环计算
    for ista in staNearList:
        ## 1 将建模站点的数据原样导入COR文件夹
        # 读取数据
        fileTrnNameOt = obs_dir + r'/%s/ObsData_%s_%s.txt' % (dateList[0], ista[1], dateList[0])
        OtTrnData = []
        fileOtTrnFial = open(fileTrnNameOt, 'r')
        for line in fileOtTrnFial.readlines():
            pl = line.split(",")
            runTime = '%04d%02d%02d' % (int(dateList[0][0:4]), int(dateList[0][4:6]), int(dateList[0][6:8]))
            obsData = float(pl[4])
            if 0 <= obsData < 2000:
                OtTrnData.append([runTime, int(pl[3]), obsData])
        fileOtTrnFial.close()

        # 结果输出
        for ihour in range(24):
            midCor = 0.0
            for iline in OtTrnData:
                if dateList[0] == iline[0] and ihour == iline[1]:
                    midCor = iline[2]
            DataAll[ihour].append([ista[1], midCor])

        ## 2 对预测站点做数据预测
        # 当天建模站点生成文件名
        fileTrnName = obs_dir + r'/%s/ObsData_%s_%s.txt' % (dateList[0], ista[0], dateList[0])

        # 中间文件名
        filetrnOtName = mid_dir + r'/MID/%s_trn.txt' % (ista[1])
        fileForOtName = mid_dir + r'/MID/%s_frt.txt' % (ista[0])
        fileCorOtName = mid_dir + r'/MID/%s_crt.txt' % (ista[0])

        # 生成预测文件
        forData = []
        fileIn = open(fileTrnName, 'r')
        for line in fileIn.readlines():
            pl = line.split(",")
            runTime = '%04d%02d%02d%02d' % (
            int(dateList[0][0:4]), int(dateList[0][4:6]), int(dateList[0][6:8]), int(pl[3]))
            radData = float(pl[5]) + 0.15 * random.random()
            tepData = float(pl[6])
            if 0 <= radData < 2 and -100 < tepData < 100:
                forData.append([runTime, 9999.0, radData, tepData])
        fileIn.close()

        fileOt = open(fileForOtName, 'w')
        fileOt.write("%d %d\n" % (len(forData), len(forData[0]) - 2))
        for idata in forData:
            fileOt.write("%s %12.2f %12.2f %12.2f\n" % tuple(idata))
        fileOt.close()

        # 生成训练文件
        ObsRadNum = []
        trnData = []
        for iday in dateList[1:-1]:
            filetrnInName = obs_dir + r'/%s/ObsData_%s_%s.txt' % (iday, ista[1], iday)
            fileIntrn = open(filetrnInName, 'r')
            for line in fileIntrn.readlines():
                pl = line.split(",")
                runTime = '%04d%02d%02d%02d' % (int(iday[0:4]), int(iday[4:6]), int(iday[6:8]), int(pl[3]))
                obsData = float(pl[4])
                radData = float(pl[5]) + 0.15 * random.random()
                tepData = float(pl[6])
                if 0 < obsData < 2500 and 0 <= radData < 2 and -100 < tepData < 100:
                    if int(pl[3]) not in ObsRadNum: ObsRadNum.append(int(pl[3]))
                    trnData.append([runTime, obsData, radData, tepData])
            fileIntrn.close()

        fileOtTrn = open(filetrnOtName, 'w')
        fileOtTrn.write("%d %d\n" % (len(trnData), len(trnData[0]) - 2))
        for idata in trnData:
            fileOtTrn.write("%s %12.2f %12.2f %12.2f\n" % tuple(idata))
        fileOtTrn.close()

        # 运行EXE获取订正
        if os.path.exists(fileForOtName) and os.path.exists(filetrnOtName):
            exe = STATISTICS_EXE
            print()
            print(exe + " " + filetrnOtName + " " + fileForOtName + " " + fileCorOtName)
            print()
            os.system(exe + " " + filetrnOtName + " " + fileForOtName + " " + fileCorOtName)

        # 读取订正结果
        if os.path.exists(fileCorOtName):
            correctData = []
            fileCorrect = open(fileCorOtName)
            fileCorrect.readline()
            for iplll in fileCorrect.readlines():
                mid = iplll.split()
                if len(mid[0]) > 7:
                    correctFinal = float(mid[2])
                    correctData.append([mid[0][:8], int(mid[0][8:]), correctFinal])
            fileCorrect.close()

            for ihour in range(24):
                midCor = 0.0
                if ihour in ObsRadNum:
                    for iline in correctData:
                        if dateList[0] == iline[0] and ihour == iline[1]:
                            midCor = iline[2]
                DataAll[ihour].append([ista[0], midCor])

    # 逐时数据输出
    for thour in range(24):

        OutLine = {}
        for idata in DataAll[thour]:

            if idata[0] not in OutLine:
                obsData = idata[1]
                lonData = 9999.0
                latData = 9999.0
                for iline in staInfo:
                    if iline[0] == idata[0]:
                        lonData = iline[1]
                        latData = iline[2]
                if 0 < lonData < 200 and 0 < latData < 90 and 0 < obsData < 2500:
                    OutLine[idata[0]] = [lonData, latData, obsData]

        fileOutPath = corResultFileName + r"/" + runday + '%02d00_station_radiences.txt' % (thour)
        fileOut = open(fileOutPath, 'w')
        fileOut.write('%d\n' % (len(OutLine)))
        for idata in OutLine:
            fileOut.write(
                '%10s  %12.3f  %12.3f  %12.3f\n' % (idata, OutLine[idata][0], OutLine[idata][1], OutLine[idata][2]))
        fileOut.close()


def georaster(in_file):
    datas = FY4ASSI(in_file)

    ssi = datas.get_ssi()

    index_valid = np.isfinite(ssi)
    if not index_valid.any():
        print('ERROR:没有有效数据')
        return

    lons = datas.get_longitude_1km()
    lats = datas.get_latitude_1km()
    lons = lons[index_valid]
    lats = lats[index_valid]

    # 计算对应的经度范围
    lons_min = np.nanmin(lons)
    lons_max = np.nanmax(lons)
    lon_arange = np.arange(LatLonRange[2], LatLonRange[3], LatLonRange[4])
    if np.searchsorted(lon_arange, lons_max) <= np.searchsorted(lon_arange, lons_min) + 10:
        print('ERROR:经度范围不足')
        return
    data_index = np.searchsorted(lon_arange, lons_min) - 1
    min_lon = LatLonRange[2] + data_index * LatLonRange[4]
    num_lon = np.searchsorted(lon_arange, lons_max) - data_index

    # 计算对应的纬度范围

    lats_min = np.nanmin(lats)
    lats_max = np.nanmax(lats)
    lat_arange = np.arange(LatLonRange[0], LatLonRange[1], LatLonRange[4])
    if np.searchsorted(lat_arange, lats_max) <= np.searchsorted(lat_arange, lats_min) + 10:
        print('ERROR:纬度范围不足')
        return
    data_index = np.searchsorted(lat_arange, lats_min) - 1
    min_lat = LatLonRange[0] + data_index * LatLonRange[4]
    num_lat = np.searchsorted(lat_arange, lats_max) - data_index

    return min_lon, num_lon, min_lat, num_lat


def nc2txt(in_file, out_file):
    """
    列变为行，行变为列
    :param in_file: 
    :param out_file: 
    :return: 
    """
    datas = FY4ASSI(in_file)
    ssi = datas.get_ssi()
    ssi[np.isnan(ssi)] = 0
    ssi[np.logical_or(ssi < 0, ssi > 1500)] = 0

    if not os.path.isfile(out_file):
        with open(out_file, 'w') as file_out:
            i, j = ssi.shape
            i = list(range(i))
            j = list(range(j))
            for jj in j:
                for ii in i:
                    mid = ssi[ii, jj]
                    file_out.write("%15.7f" % mid)
                file_out.write("\n")
            file_out.close()


def get_fy4a_1km_correct_txt_lat_lon(in_file):
    if not os.path.isfile(in_file):
        raise FileExistsError(':{}'.format(in_file))
    datas = np.loadtxt(in_file)
    data = {}
    indexs = {
        'Latitude': 0,
        'Longitude': 1,
        'SSI': 2,
    }
    for name, index in indexs.items():
        data[name] = datas[:, index]
    return data


def out_hdf(nc_file, varify_file, out_file):
    if not os.path.isfile(varify_file):
        return

    temp_hdf_name = os.path.basename(nc_file)
    temp_hdf = os.path.join(os.path.dirname(varify_file), temp_hdf_name)

    if os.path.isfile(temp_hdf):
        os.remove(temp_hdf)
    shutil.copyfile(nc_file, temp_hdf)

    with h5py.File(temp_hdf) as hdf:
        print('read verify data start')
        varify_data = get_fy4a_1km_correct_txt_lat_lon(varify_file)
        print('read end')
        lats = varify_data['Latitude'].reshape(-1)
        lons = varify_data['Longitude'].reshape(-1)
        ii = np.floor((lats - LatLonRange[0]) / LatLonRange[4]).astype(np.int)
        jj = np.floor((lons - LatLonRange[2]) / LatLonRange[4]).astype(np.int)

        ssi = hdf.get('SSI')[:]
        ssi_varify = hdf.get('SSI')[:]

        varify_data_ssi = varify_data['SSI'].reshape(-1)
        # 无效值赋值为FULL_VALUE
        varify_data_ssi[np.logical_or(varify_data_ssi <= 0, varify_data_ssi >= 1500)] = FULL_VALUE
        ssi_varify[ii, jj] = varify_data_ssi

        # 将订正后的SSI进行存储
        hdf.get('SSI')[:] = ssi_varify

        if DEBUG:
            ssi_new = hdf.get('SSI')[:]
            print(np.mean(ssi[ssi > 0]))
            print(np.mean(ssi_varify[ssi_varify > 0]))
            print(np.mean(ssi_new[ssi_new > 0]))

            print(np.std(ssi[ssi > 0]))
            print(np.std(ssi_varify[ssi_varify > 0]))
            print(np.std(ssi_new[ssi_new > 0]))

        # 订正DifSSI和DirSSI
        diff_mid = ssi / ssi_varify
        dif_ssi = hdf.get("DifSSI")[:]
        dir_ssi = hdf.get("DirSSI")[:]
        index = diff_mid > 0
        dif_ssi[index] = dif_ssi[index] * diff_mid[index]
        dif_ssi[np.logical_or.reduce((dif_ssi <= 0, dif_ssi >= 1200, np.isnan(dif_ssi)))] = FULL_VALUE
        dir_ssi[index] = dir_ssi[index] * diff_mid[index]
        dir_ssi[np.logical_or.reduce((dir_ssi <= 0, dir_ssi >= 1200, np.isnan(dir_ssi)))] = FULL_VALUE

        # 将订正后的DifSSI和DirSSI进行存储
        hdf.get("DifSSI")[:] = dif_ssi
        hdf.get("DirSSI")[:] = dir_ssi

    shutil.copyfile(temp_hdf, out_file)


# 每日NC数据网格
# install:BIN文件夹所在目录; runday:所需运行日期 ; runhour:所需运行小时 世界时
def CaculateNCLine(nc_file, mid_dir, out_file, runday, runhour):
    MidFileName = mid_dir + r"/DIFFMID"
    if not os.path.isdir(MidFileName):
        os.makedirs(MidFileName)

    runTime = runday + '%02d' % runhour
    runTime_datetime = datetime.strptime(runTime, '%Y%m%d%H')
    runtime_datetime_beijing = runTime_datetime + relativedelta(hours=8)
    runday_beijing = runtime_datetime_beijing.strftime('%Y%m%d')
    runTime_beijing = runtime_datetime_beijing.strftime('%Y%m%d%H')

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # 读取高纬度下的有效经度数值
    # 形成经度网格
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    result = georaster(nc_file)
    if result is not None:
        minLon, numLon, minLat, numLat = result
    else:
        return

    print("有效经度范围： " + str(minLon) + "-" + str(minLon + LatLonRange[4] * numLon))
    print("有效纬度范围： " + str(minLat) + "-" + str(minLat + LatLonRange[4] * numLat))
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # 复制观测与NC文件至DIFFMID目录
    # 生成插值后的结果到DIFFMID目录
    # 生成网格和时间文件到DIFFMID目录
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # 观测站文件数据源
    obsFileSource = mid_dir + r'/COR' + r"/" + runday_beijing + r"/" + runTime_beijing + "00_station_radiences.txt"

    # 观测和NC源文件正常；经度网格正常
    if os.path.exists(obsFileSource) and minLon > LatLonRange[2] - 0.1 and numLon > 10:

        # 观测数据保留网格范围内的数据
        ObsData = []
        fileObs = open(obsFileSource, 'r')
        fileObs.readline()
        for ii in fileObs.readlines():
            pl = ii.split()
            staName = pl[0].strip()
            staLon = float(pl[1])
            staLat = float(pl[2])
            staObs = float(pl[3])
            if minLon < staLon < minLon + LatLonRange[4] * numLon and minLat < staLat < minLat + LatLonRange[
                4] * numLat:
                ObsData.append([staName, staLon, staLat, staObs])
        fileObs.close()

        ObsFileOutPath = MidFileName + r"/" + runTime_beijing + "00_station_radiences.txt"
        if len(ObsData) > 0:
            ObsFileOut = open(ObsFileOutPath, 'w')
            ObsFileOut.write('%d\n' % (len(ObsData)))
            for idata in ObsData:
                ObsFileOut.write('%10s  %12.3f  %12.3f  %12.3f\n' % tuple(idata))
            ObsFileOut.close()
            print(">>>         : {}".format(ObsFileOutPath))

        # 将1KM数据的SSI转为txt
        nc_file_source_path = os.path.join(mid_dir, 'IN')
        if not os.path.isdir(nc_file_source_path):
            os.makedirs(nc_file_source_path)
        ncFileSource = os.path.join(mid_dir, 'IN', os.path.basename(mid_dir) + '_ssi.txt')
        nc2txt(in_file=nc_file, out_file=ncFileSource)
        print(">>>         : {}".format(ncFileSource))

        # 生成 DIFFMID/grid_info.txt
        min_lat = LatLonRange[0]
        max_lat = LatLonRange[1]
        min_lon = LatLonRange[2]
        max_lon = LatLonRange[3]
        res = LatLonRange[4]

        num_lon = (max_lon - min_lon) / res + 1
        num_lat = (max_lat - min_lat) / res + 1

        fileGrid = open(MidFileName + r'/grid_info.txt', 'w')
        fileGrid.write("%12.4f  %12.4f  %12.2f  %d  %d" % (
            min_lat, min_lon, res, num_lon, num_lat))
        fileGrid.close()
        print(minLat, minLon, LatLonRange[4], numLon, numLat)
        print(">>>         : {}".format(MidFileName + r'/grid_info.txt'))

        # 生成 DIFFMID/time_radiance.txt
        fileTime = open(MidFileName + r'/time_radiance.txt', 'w')
        fileTime.write("1\n")
        fileTime.write(runTime_beijing + "00")
        fileTime.close()
        print(">>>         : {}".format(MidFileName + r'/time_radiance.txt'))

        # 插值结果正常生成后，开始变分订正,生成
        if os.path.exists(ncFileSource) and os.path.exists(ObsFileOutPath):
            OutDiffResultdir = mid_dir + r"/" + 'RESData'
            fileDiffResult = OutDiffResultdir + r"/" + runTime_beijing + "00_varify.txt"
            if not os.path.exists(OutDiffResultdir):
                os.mkdir(OutDiffResultdir)
            runFile = [ncFileSource,  # 原始4KM，程序中的计算没有用到这个文件
                       ncFileSource,  # 1KM订正
                       MidFileName + r'/time_radiance.txt',
                       MidFileName + r'/grid_info.txt',
                       ObsFileOutPath,
                       OutDiffResultdir]
            if not os.path.isfile(fileDiffResult):
                exe = VARIFY_EXE
                print()
                print(exe + " " + ' '.join(runFile))
                print()
                os.system(exe + " " + ' '.join(runFile))
        else:
            print('ERROR:必要的输入文件不存在')
            return

        # 输出HDF5结果
        print('start output HDF5')
        if not os.path.isdir(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))
        out_hdf(nc_file, fileDiffResult, out_file)
        print(">>>         {}".format(out_file))
