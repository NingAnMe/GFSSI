#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import sys
import random
import step4_bin.CorrectClass as CorrectClass
import numpy as np
import pandas as pd

# 经纬度范围,及其循环次数
# NC的实际经纬度 [0.0, 55.0, 70.0, 140.0]
# LatLonRange = [20.0, 55.0, 75.0, 135.0, 0.04]

current_dir = os.path.dirname(os.path.abspath(__file__))
EXE_DIR = current_dir
gfssi_dir = os.path.dirname(current_dir)
sys.path.append(gfssi_dir)

from lib.lib_read_ssi import FY4ASSI
from lib.lib_constant import FY4A_1KM_CORRECT_LAT_LON_RANGE, STATION_LIST
from gfssi_b04_txt2hdf import fy4a_1km_correct_txt2hdf

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
    if not os.path.exists(corFileName): os.mkdir(corFileName)
    # 删除MID文件夹的中间结果
    CorrectClass.clearMidDir(mid_dir + r"/MID")

    corResultFileName = mid_dir + r"/COR" + r"/" + runday
    if not os.path.exists(corResultFileName): os.mkdir(corResultFileName)

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
        # fileTrnOtTrnName = install+r'/COR/%s/%s.txt'%(dateList[0], ista[1])
        # fileOtTrnFialLine = open(fileTrnOtTrnName, 'w')
        for ihour in range(24):
            midCor = 0.0
            for iline in OtTrnData:
                if dateList[0] == iline[0] and ihour == iline[1]:
                    midCor = iline[2]
            DataAll[ihour].append([ista[1], midCor])
            # fileOtTrnFialLine.write("%8s, %2d, %12.2f\n" % (dateList[0], ihour, midCor))
        # fileOtTrnFialLine.close()

        ## 2 对预测站点做数据预测
        # 当天建模站点生成文件名
        fileTrnName = obs_dir + r'/%s/ObsData_%s_%s.txt' % (dateList[0], ista[0], dateList[0])
        fileTrnOtCorName = mid_dir + r'/COR/%s/%s.txt' % (dateList[0], ista[0])

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
            exe = os.path.join(EXE_DIR, 'LRR_dyn_statistic.exe')
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

            # fileOtCor = open(fileTrnOtCorName, 'w')
            for ihour in range(24):
                midCor = 0.0
                if ihour in ObsRadNum:
                    for iline in correctData:
                        if dateList[0] == iline[0] and ihour == iline[1]:
                            midCor = iline[2]
                DataAll[ihour].append([ista[0], midCor])
                # fileOtCor.write("%8s, %2d, %12.2f\n"%(dateList[0], ihour, midCor))
            # fileOtCor.close()

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


def nc2txt(in_file, out_file):
    data_all = {
        'SSI': None,
        'DirSSI': None,
        'DifSSI': None,
        'Latitude': None,
        'Longitude': None,
    }
    # try:
    datas = FY4ASSI(in_file)
    data_get = {
        'SSI': datas.get_ssi,
        'DirSSI': datas.get_dirssi,
        'DifSSI': datas.get_difssi,
        'Latitude': datas.get_latitude_4km,
        'Longitude': datas.get_longitude_4km,
    }
    for dataname, data_getter in data_get.items():
        # try:
        data_all[dataname] = data_getter()
        # except:
        #     pass
    # except Exception as why:
    #     print(why)
    #     print('合成数据过程出错，文件为：{}'.format(in_file))

    ssi = data_all['SSI']
    index_valid = np.isfinite(ssi)
    if not index_valid.any():
        print('ERROR:没有有效数据')
        return

    ssi = ssi[index_valid]
    dirssi = data_all['DirSSI'][index_valid]
    difssi = data_all['DifSSI'][index_valid]
    lons = data_all['Longitude'][index_valid]
    lats = data_all['Latitude'][index_valid]

    # 计算对应的经度范围
    lons_min = np.nanmin(lons)
    lons_max = np.nanmax(lons)
    lon_arange = np.arange(LatLonRange[2], LatLonRange[3], LatLonRange[4])
    if np.searchsorted(lon_arange, lons_max) <= np.searchsorted(lon_arange, lons_min) + 10:
        print('ERROR:经度范围不足')
        return
    dataIndex = np.searchsorted(lon_arange, lons_min)
    minLon = LatLonRange[2] + dataIndex * LatLonRange[4]
    numLon = np.searchsorted(lon_arange, lons_max)

    # 计算对应的纬度范围

    lats_min = np.nanmin(lats)
    lats_max = np.nanmax(lats)
    lat_arange = np.arange(LatLonRange[0], LatLonRange[1], LatLonRange[4])
    if np.searchsorted(lat_arange, lats_max) <= np.searchsorted(lat_arange, lats_min) + 10:
        print('ERROR:纬度范围不足')
        return
    dataIndex = np.searchsorted(lat_arange, lats_min)
    minLat = LatLonRange[0] + dataIndex * LatLonRange[4]
    numLat = np.searchsorted(lat_arange, lats_max)

    d = {
        'lon': lons,
        'lat': lats,
        'ssi': ssi,
        'dirssi': dirssi,
        'difssi': difssi
    }

    if not os.path.isfile(out_file):
        df = pd.DataFrame(data=d)
        df.to_csv(out_file, sep=' ', header=False, index=False, encoding='utf-8')
    else:
        print("is already exist : {}".format(out_file))

    return out_file, minLon, numLon, minLat, numLat


# 每日NC数据网格
# install:BIN文件夹所在目录; runday:所需运行日期 ; runhour:所需运行小时 世界时
def CaculateNCLine(nc_file, mid_dir, out_file, runday, runhour):
    # 删除DIFFMID文件夹的中间结果
    MidFileName = mid_dir + r"/DIFFMID"
    if not os.path.isdir(MidFileName):
        os.makedirs(MidFileName)

    runTime = runday + '%02d' % runhour
    runTime_datetime = datetime.strptime(runTime, '%Y%m%d%H')
    runtime_datetime_beijing = runTime_datetime + relativedelta(hours=8)
    runday_beijing = runtime_datetime_beijing.strftime('%Y%m%d')
    runTime_beijing = runtime_datetime_beijing.strftime('%Y%m%d%H')

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # 获取NC文件对应的世界时
    # 并获取对应小时的离零点最近的数据
    # 读取高纬度下的有效经度数值
    # 形成经度网格
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    source_txt = os.path.join(mid_dir, os.path.basename(mid_dir) + '.txt')

    result = nc2txt(nc_file, source_txt)
    if result is not None:
        source_txt, minLon, numLon, minLat, numLat = result
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
    # NC文件数据源
    ncFileSource = source_txt

    # 观测和NC源文件正常；经度网格正常
    if os.path.exists(obsFileSource) and os.path.exists(ncFileSource) and minLon > LatLonRange[2] - 0.1 and numLon > 10:

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

        # cressman_FY4.exe程序插值
        # 生成 DIFFMID / runTime +"00_cubic.txt"
        # 1. 插值前卫星资料路径和文件名, 文本文件格式 fileIn
        # 2. 插值后卫星资料路径和文件名, 文本文件格式 fileOut
        # 3. 起始点纬度 * 1000, 例如20°，此处输入minLat*1000
        # 4. 起始点经度 * 1000, 例如75°，此处输入minLon*1000
        # 5. 网格距 * 1000, 例如0.04°，此处输入40
        # 6. X方向格点数 numLon
        # 7. Y方向格点数 numLat
        # fileOut = MidFileName + r"/" + runTime_beijing + "00_ssi_cubic.txt"
        # runData = [ncFileSource,
        #            fileOut,
        #            str(int(minLat * 1000)),
        #            str(int(minLon * 1000)),
        #            str(int(LatLonRange[4] * 1000)),
        #            str(numLon),
        #            str(numLat)]
        # exe = os.path.join(EXE_DIR, 'cressman_FY4.exe')
        # print()
        # print(exe + " " + ' '.join(runData))
        # print()
        # os.system(exe + " " + ' '.join(runData))

        # 三次样条插值
        fileOut = MidFileName + r"/" + runTime_beijing + "00_ssi_cubic.txt"
        totalFile = MidFileName + r"/" + runTime_beijing + "00_ssi_cubic_total.txt"
        CorrectClass.makeFileCubic(ncFileSource, fileOut, [minLat, numLat], [minLon, numLon], LatLonRange[4], totalFile)
        print(">>>         : {}".format(fileOut))
        print(">>>         : {}".format(totalFile))

        # 生成 DIFFMID/grid_info.txt
        fileGrid = open(MidFileName + r'/grid_info.txt', 'w')
        fileGrid.write("%12.4f  %12.4f  %12.2f  %d  %d" % (minLat, minLon, LatLonRange[4], numLon, numLat))
        fileGrid.close()
        print(minLat, minLon, LatLonRange[4], numLon, numLat)
        print(">>>         : {}".format(MidFileName + r'/grid_info.txt'))

        # 生成 DIFFMID/time_radiences.txt
        fileTime = open(MidFileName + r'/time_radiences.txt', 'w')
        fileTime.write("1\n")
        fileTime.write(runTime_beijing + "00")
        fileTime.close()
        print(">>>         : {}".format(MidFileName + r'/time_radiences.txt'))

        # 插值结果正常生成后，开始变分订正,生成
        if os.path.exists(fileOut) and os.path.exists(ObsFileOutPath):
            OutDiffResultdir = mid_dir + r"/" + runday
            fileDiffResult = OutDiffResultdir + r"/" + runTime_beijing + "00_varify.txt"
            if not os.path.exists(OutDiffResultdir): os.mkdir(OutDiffResultdir)
            runFile = [ncFileSource,
                       fileOut,
                       MidFileName + r'/time_radiences.txt',
                       MidFileName + r'/grid_info.txt',
                       ObsFileOutPath,
                       OutDiffResultdir]
            if not os.path.isfile(fileDiffResult):
                exe = os.path.join(EXE_DIR, 'varify.exe')
                print()
                print(exe + " " + ' '.join(runFile))
                print()
                os.system(exe + " " + ' '.join(runFile))
        else:
            print('ERROR:必要的输入文件不存在')
            return

        # 变分订正结果正常生成后，开始直散数据计算
        print('输出最后的结果 varify_finally.txt')
        if os.path.exists(fileDiffResult) and os.path.exists(totalFile):
            DiffResult = []
            for line in open(fileDiffResult, 'r').readlines():
                pl = line.split()
                latMidd = float(pl[0])
                lonMidd = float(pl[1])
                obsMidd = float(pl[2])
                DiffResult.append([latMidd, lonMidd, obsMidd])

            CubicResult = []
            for line in open(totalFile, 'r').readlines():
                pl = line.split()
                obsMidd = float(pl[2])
                dirMidd = float(pl[3])
                sctMidd = float(pl[4])
                CubicResult.append([obsMidd, dirMidd, sctMidd])

            dataNum = min([len(DiffResult), len(CubicResult)])
            fileOutFinallPass = OutDiffResultdir + r"/" + runTime_beijing + "00_varify_finally.txt"
            fileOutFinall = open(fileOutFinallPass, 'w')
            fileOutFinall.write(
                "        纬度          经度       卫星总辐射         卫星直射         卫星散射       变分总辐射         变分直射         变分散射\n")
            for i in range(dataNum):

                obsFinall1 = CubicResult[i][0]
                dirFinall1 = CubicResult[i][1]
                sctFinall1 = CubicResult[i][2]
                latFinall = DiffResult[i][0]
                lonFinall = DiffResult[i][1]
                obsFinall = DiffResult[i][2]
                dirFinall = 0.0
                sctFinall = 0.0

                diffMid = 0
                if obsFinall1 > 1: diffMid = 1.0 * obsFinall / obsFinall1
                if diffMid > 0:
                    dirFinall = dirFinall1 * diffMid
                    sctFinall = sctFinall1 * diffMid
                if dirFinall < 0 or dirFinall > 1200: dirFinall = 9999.0
                if sctFinall < 0 or sctFinall > 1200: sctFinall = 9999.0

                fileOutFinall.write("%12.3f  %12.3f  %15.3f  %15.3f  %15.3f  %15.3f  %15.3f  %15.3f\n"
                                    % (latFinall, lonFinall, obsFinall1, dirFinall1, sctFinall1, obsFinall, dirFinall,
                                       sctFinall))
            fileOutFinall.close()
            print(">>>         : {}".format(fileOutFinallPass))
            # txt2hdf
            fy4a_1km_correct_txt2hdf(in_file=fileOutFinallPass, out_file=out_file)
            print(">>>         : {}".format(out_file))
        print(runTime + "时段的订正运行结束")


if __name__ == "__main__":
    install_dir = r'/home/gfssi/Project/OM/gfssi/step4'

    OBS_DIR = ''
    MID_DIR = ''

    # runday = '20171015'
    runday = sys.argv[1]
    ForecastDataPerday(OBS_DIR, MID_DIR, runday)

    NC_FILE = ''

    CaculateNCLine(NC_FILE, MID_DIR, runday, 9)
