#!/usr/bin/python
# -*- coding:utf-8 -*-


import os
import sys
import random
import CorrectClass
import Python_Program

# 经纬度范围,及其循环次数
# NC的实际经纬度 [0.0, 55.0, 70.0, 140.0]
# LatLonRange = [20.0, 55.0, 75.0, 135.0, 0.04]
LatLonRange = [9.995, 55.01, 69.995, 135.01, 0.01]


# 每日数据订正
# install:BIN文件夹所在目录；runday:所需运行日期
def ForecastDataPerday(install, runday):
    nday = 3

    # 获取数据所在目录,获取站点信息,获取建模日期
    dirInfo = CorrectClass.dirInfoGet(install)
    staInfo = CorrectClass.staInfoGet(install)
    dateList = CorrectClass.calDateList(runday, nday)

    # 站点间关系处理
    staNearList = CorrectClass.staNearListGet(staInfo, dirInfo[0], dateList)

    # 在对应目录创建输出文件夹
    corFileName = install + r"/COR"
    if not os.path.exists(corFileName): os.mkdir(corFileName)
    # 删除MID文件夹的中间结果
    CorrectClass.clearMidDir(install + r"/MID")

    corResultFileName = install + r"/COR" + r"/" + runday
    if not os.path.exists(corResultFileName): os.mkdir(corResultFileName)

    # 中间结果集
    DataAll = {}
    for ihour in range(24):
        DataAll[ihour] = []

    # 逐站点循环计算
    for ista in staNearList:
        ## 1 将建模站点的数据原样导入COR文件夹
        # 读取数据
        fileTrnNameOt = dirInfo[0] + r'/%s/ObsData_%s_%s.txt' % (dateList[0], ista[1], dateList[0])
        OtTrnData = []
        fileOtTrnFial = open(fileTrnNameOt, 'r')
        for line in fileOtTrnFial.readlines():
            pl = line.split(",")
            runTime = '%04d%02d%02d' % (int(pl[0]), int(pl[1]), int(pl[2]))
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
        fileTrnName = dirInfo[0] + r'/%s/ObsData_%s_%s.txt' % (dateList[0], ista[0], dateList[0])
        fileTrnOtCorName = install + r'/COR/%s/%s.txt' % (dateList[0], ista[0])

        # 中间文件名
        filetrnOtName = install + r'/MID/%s_trn.txt' % (ista[1])
        fileForOtName = install + r'/MID/%s_frt.txt' % (ista[0])
        fileCorOtName = install + r'/MID/%s_crt.txt' % (ista[0])

        # 生成预测文件
        forData = []
        fileIn = open(fileTrnName, 'r')
        for line in fileIn.readlines():
            pl = line.split(",")
            runTime = '%04d%02d%02d%02d' % (int(pl[0]), int(pl[1]), int(pl[2]), int(pl[3]))
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
            filetrnInName = dirInfo[0] + r'/%s/ObsData_%s_%s.txt' % (iday, ista[1], iday)
            fileIntrn = open(filetrnInName, 'r')
            for line in fileIntrn.readlines():
                pl = line.split(",")
                runTime = '%04d%02d%02d%02d' % (int(pl[0]), int(pl[1]), int(pl[2]), int(pl[3]))
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
            os.system(
                install + r'/BIN/LRR_dyn_statistic.exe ' + filetrnOtName + " " + fileForOtName + " " + fileCorOtName)

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


# 每日NC数据网格
# install:BIN文件夹所在目录; runday:所需运行日期 ; runhour:所需运行小时 北京时
def CaculateNCLine(install, runday, runhour):
    # 删除DIFFMID文件夹的中间结果
    MidFileName = install + r"/DIFFMID"
    CorrectClass.clearMidDir(MidFileName)

    # 北京时YYYYMMDDHH
    runTime = runday + '%02d' % (runhour)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # 获取NC文件对应的世界时
    # 并获取对应小时的离零点最近的数据
    # 读取高纬度下的有效经度数值
    # 形成经度网格
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # 将北京时转化为世界时
    wordHour = Python_Program.add_hour(int(runday[0:4]), int(runday[4:6]), int(runday[6:8]), int(runhour), -8)
    yesDate = "%04d%02d%02d" % tuple(wordHour[:3])
    dirNcInfo = CorrectClass.dirInfoGet(install)[1] + r"/" + yesDate

    # 获取目录下的对应时间的文件,离yesDate00点最近的文件
    fileName = ""
    if os.path.exists(dirNcInfo):
        fileList = []
        for ifile in os.listdir(dirNcInfo):
            if ifile.startswith(yesDate + "%02d" % (wordHour[3])):
                fileList.append(ifile)
        if len(fileList) > 0:
            fileList.sort()
            fileName = fileList[0]
    print("开始运行:" + runTime + "时段的订正,读取NC文件:" + fileName)

    # 读取对应的NC文件,仅读取高纬度有值数据
    LonRange = []
    if len(fileName) > 0:
        with open(dirNcInfo + r"/" + fileName, 'r') as flieMM:
            for line in flieMM:
                pl = line.split()
                lon = float(pl[0])
                lat = float(pl[1])
                obs = float(pl[2])
                # 纬度:[最大纬度-1, 最大纬度] ; 经度:[最小经度, 最大经度] ; 总辐射: [0, 1500)之间 ;
                if LatLonRange[1] - 1 < lat < LatLonRange[1] and LatLonRange[2] < lon < LatLonRange[
                    3] and 0 <= obs < 1500:
                    LonRange.append(lon)

    # 计算对应经度范围
    minLon = 0.0
    numLon = 0
    if len(LonRange) > 0:
        dataIndex = []
        step = int((LatLonRange[3] - LatLonRange[2]) / LatLonRange[4]) + 2
        for i in range(step):
            rangeNum = 0
            for j in LonRange:
                if (LatLonRange[2] + i * LatLonRange[4] <= j < LatLonRange[2] + (i + 1) * LatLonRange[4]):
                    rangeNum = rangeNum + 1
            if rangeNum > 1: dataIndex.append(i)
        if len(dataIndex) > 0:
            minLon = LatLonRange[2] + dataIndex[0] * LatLonRange[4]
            numLon = dataIndex[-1] - dataIndex[0]

    # 计算对应的纬度范围
    minLat = LatLonRange[0]
    numLat = int((LatLonRange[1] - LatLonRange[0]) / LatLonRange[4])
    print("有效经度范围： " + str(minLon) + "-" + str(minLon + LatLonRange[4] * numLon))
    print("有效纬度范围： " + str(minLat) + "-" + str(minLat + LatLonRange[4] * numLat))

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # 复制观测与NC文件至DIFFMID目录
    # 生成插值后的结果到DIFFMID目录
    # 生成网格和时间文件到DIFFMID目录
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # 观测文件数据源
    obsFileSource = install + r'/COR' + r"/" + runday + r"/" + runTime + "00_station_radiences.txt"
    # NC文件数据源
    ncFileSource = dirNcInfo + r"/" + fileName

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

        ObsFileOutPath = MidFileName + r"/" + runTime + "00_station_radiences.txt"
        if len(ObsData) > 0:
            ObsFileOut = open(ObsFileOutPath, 'w')
            ObsFileOut.write('%d\n' % (len(ObsData)))
            for idata in ObsData:
                ObsFileOut.write('%10s  %12.3f  %12.3f  %12.3f\n' % tuple(idata))
            ObsFileOut.close()

        # cressman_FY4.exe程序插值
        # 生成 DIFFMID / runTime +"00_cubic.txt"
        # 1. 插值前卫星资料路径和文件名, 文本文件格式 fileIn
        # 2. 插值后卫星资料路径和文件名, 文本文件格式 fileOut
        # 3. 起始点纬度 * 1000, 例如20°，此处输入minLat*1000
        # 4. 起始点经度 * 1000, 例如75°，此处输入minLon*1000
        # 5. 网格距 * 1000, 例如0.04°，此处输入40
        # 6. X方向格点数 numLon
        # 7. Y方向格点数 numLat
        fileOut = MidFileName + r"/" + runTime + "00_ssi_cubic.txt"
        runData = [ncFileSource,
                   fileOut,
                   str(int(minLat * 1000)),
                   str(int(minLon * 1000)),
                   str(int(LatLonRange[4] * 1000)),
                   str(numLon),
                   str(numLat)]
        # os.system( install + r'/BIN/cressman_FY4.exe ' + ' '.join(runData) )

        # 三次样条插值
        totalFile = MidFileName + r"/" + runTime + "00_ssi_cubic_total.txt"
        CorrectClass.makeFileCubic(ncFileSource, fileOut, [minLat, numLat], [minLon, numLon], LatLonRange[4], totalFile)

        # 生成 DIFFMID / grid_info.txt
        fileGrid = open(MidFileName + r'/grid_info.txt', 'w')
        fileGrid.write("%12.4f  %12.4f  %12.2f  %d  %d" % (minLat, minLon, LatLonRange[4], numLon, numLat))
        print(minLat, minLon, LatLonRange[4], numLon, numLat)
        fileGrid.close()

        # 生成 DIFFMID / time_radiences.txt
        fileTime = open(MidFileName + r'/time_radiences.txt', 'w')
        fileTime.write("1\n")
        fileTime.write(runTime + "00")
        fileTime.close()

        # 插值结果正常生成后，开始变分订正
        if os.path.exists(fileOut) and os.path.exists(ObsFileOutPath):
            OutDiffResultdir = CorrectClass.dirInfoGet(install)[2] + r"/" + runday
            if not os.path.exists(OutDiffResultdir): os.mkdir(OutDiffResultdir)
            runFile = [ncFileSource,
                       fileOut,
                       MidFileName + r'/time_radiences.txt',
                       MidFileName + r'/grid_info.txt',
                       ObsFileOutPath,
                       OutDiffResultdir]

            os.system(install + r'/BIN/varify.exe ' + ' '.join(runFile))

        print('输出最后的结果00_varify.txt')
        # 变分订正结果正常生成后，开始直散数据计算
        fileDiffResult = OutDiffResultdir + r"/" + runTime + "00_varify.txt"
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

            print('输出最后的结果00_varify_finally.txt')
            dataNum = min([len(DiffResult), len(CubicResult)])
            fileOutFinallPass = OutDiffResultdir + r"/" + runTime + "00_varify_finally.txt"
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
        print(runTime + "时段的订正运行结束")


if __name__ == "__main__":
    install_dir = r'/home/gfssi/Project/OM/gfssi/step4'

    runday = '20171015'
    # runday = sys.argv[1]
    # ForecastDataPerday(install_dir, runday)
    CaculateNCLine(install_dir, runday, 9)
    # for ihour in range(24):
    #     try:
    #         CaculateNCLine(r'/home/gfssi/Project/OM/gfssi/step4', runday, ihour)
    #     except:
    #         pass
