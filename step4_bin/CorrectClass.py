#!/usr/bin/python
# -*- coding: utf-8 -*-
#for the type 3.5 or 2.7


import os
import datetime
import math
import shutil
import numpy as np
from scipy.interpolate import griddata as sciGridData
import Python_Program


# 获取数据所在目录
# dirInfo[0]:观测数据， dirInfo[1]:风云4NC数据， dirInfo[2]:结果数据
def dirInfoGet(in_dir, mid_dir):
    """
    将输入目录、输出目录改为固定的目录
    :param in_dir:  输入目录
    :param mid_dir:  输入目录
    :return:
    """
    dirInfo = [in_dir + r'/ObsData', in_dir + r'/SatNcData', mid_dir + r'/RetData']
    return dirInfo


# 获取站点信息
# staInfo[0][0]:站点编号，staInfo[0][1]:纬度，staInfo[0][2]:经度
def staInfoGet(txt_file):
    # sta_infor = open(install + r'/BIN/StationList.txt', 'r')
    staInfo = []
    sta_infor=open(txt_file,'r')
    for line in sta_infor.readlines():
        mid=line.split(",")
        try:
            staInfo.append([mid[0].strip(), float(mid[1]), float(mid[2])])
        except:
            pass
    sta_infor.close()

    return staInfo



# 计算所有站点列表中的站点数据状况，统计形成建模对
# staInfo站点信息列表, dirInfo观测数据目录, dataList数据建模日期
# 返回:[ 预报站点, 建模站点, 最近距离 ]
def staNearListGet(staInfo, dirInfo, dataList):

    forStaList = []
    trnStaList = []
    for ista in staInfo:

        # 计算forecastData的数据量
        forDataNum = 0
        frtFileName = dirInfo+r"/"+dataList[0]+r"/"+"ObsData_%s_%s.txt"%(ista[0], dataList[0])
        if os.path.exists(frtFileName):
            filein = open(frtFileName, 'r')
            for line in filein.readlines():
                pl = line.split(",")
                if 0 <= float(pl[5]) < 2 and -100 <= float(pl[6]) < 100:
                    forDataNum = forDataNum + 1
            filein.close()

        # 计算trainData的数据量
        trnDataNum = 0
        for iday in dataList[1:-1]:
            trnFileName = dirInfo + r"/" + iday + r"/" + "ObsData_%s_%s.txt" % (ista[0], iday)
            if os.path.exists(trnFileName):
                fileinOne = open(trnFileName, 'r')
                for line in fileinOne.readlines():
                    pl = line.split(",")
                    if 0 < float(pl[4]) < 2500 and 0 <= float(pl[5]) < 2 and -100 <= float(pl[6]) < 100:
                        trnDataNum = trnDataNum + 1
                fileinOne.close()

        if forDataNum>5 :
            if trnDataNum==0:
                forStaList.append(ista)
            else:
                trnStaList.append(ista)

    StaNearList = []
    for ista in forStaList:
        lstStaName = []
        lstStaDir = 1000000
        for itrain in trnStaList:
            dirSta = (itrain[1]-ista[1])**2 + (itrain[2]-ista[2])**2
            if dirSta < lstStaDir:
                lstStaName = itrain
                lstStaDir = dirSta
        if len(lstStaName)>0 and lstStaDir<25:
            StaNearList.append( [ista[0], lstStaName[0], math.sqrt(lstStaDir)] )

    return StaNearList


# 计算当前日期前N+1天的日期(包括当天)
# runday:当前日期， nday:运行日期
# 返回: runday, runday-1, runday-2 ... runday-nday, runday-nday-1
def calDateList(runday, nday):

    traindate = []
    dtoday=datetime.datetime(int(runday[:4]),int(runday[4:6]),int(runday[6:]))
    for i in range(nday+2):
        traindate.append( str(dtoday - datetime.timedelta(i))[:10].replace("-", "") )
    return traindate



# 计算当前日期后N天的日期(包括当天)
# runday:当前日期， nday:运行日期
# 返回: runday, runday+1, runday+2 ... runday+nday-1, runday+nday
def calDateListAfter(runday, nday):

    traindate = []
    dtoday=datetime.datetime(int(runday[:4]),int(runday[4:6]),int(runday[6:]))
    for i in range(nday+1):
        traindate.append( str(dtoday + datetime.timedelta(i))[:10].replace("-", "") )
    return traindate


# make_flie : YYYYMMDDHHmm_ssi_cubic.txt
# in: YYYYMMDDHHmm_ssi.txt
# LatInfo:[ 纬度起点，网格数 ] ； LonInfo[ 经度度起点，网格数 ] ; LatLonRange网格间距
def makeFileCubic(inFile, outFile, LatInfo, LonInfo, LatLonRange, totalFile):


    # 获取经纬度范围
    LatBegin = LatInfo[0]
    LatEnd = LatBegin + LatInfo[1] * LatLonRange
    lonBegin = LonInfo[0]
    LonEnd = lonBegin + LonInfo[1] * LatLonRange

    rads = []
    lons = []
    lats = []
    dirs = []
    scts = []
    # 读取NC文件源数据
    fileIn = open(inFile , 'r')
    for line in fileIn.readlines():
        pl = line.split()
        lonMid = float( pl[0] )
        latMid = float( pl[1] )
        radMid = float( pl[2] )
        dirMid = float( pl[3] )
        sctMid = float( pl[4] )
        if radMid<0 or radMid>2000: radMid = 0.0
        if dirMid<0 or dirMid>2000: dirMid = 0.0
        if sctMid<0 or sctMid>2000: sctMid = 0.0
        if lonBegin<= lonMid <= LonEnd and LatBegin<= latMid <= LatEnd:
            lons.append( lonMid )
            lats.append( latMid )
            rads.append( radMid )
            dirs.append( dirMid )
            scts.append( sctMid )
    fileIn.close()

    # 三次样条
    x = np.arange(lonBegin, LonEnd, LatLonRange, dtype=np.float64)
    y = np.arange(LatBegin, LatEnd, LatLonRange, dtype=np.float64)
    xx, yy = np.meshgrid(x, y)
    result1 = sciGridData((lons, lats), rads, xi=(xx, yy), method="cubic", rescale=True)
    result2 = sciGridData((lons, lats), dirs, xi=(xx, yy), method="cubic", rescale=True)
    result3 = sciGridData((lons, lats), scts, xi=(xx, yy), method="cubic", rescale=True)

    minLonLen = min( [len(x), LonInfo[1]] )
    # write YYYYMMDDHHmm_ssi_cubic_total.txt
    fileOut = open(totalFile , 'w')
    i = np.arange(0, len(y))
    j = np.arange(0, minLonLen)
    for jj in j:
        for ii in i:
            mid1 = 0.0
            mid2 = 0.0
            mid3 = 0.0
            try:
                midd1 = float(result1[ii, jj])
                midd2 = float(result2[ii, jj])
                midd3 = float(result3[ii, jj])
                if 0.0 <= midd1 < 1500: mid1 = midd1
                if 0.0 <= midd2 < 1500: mid2 = midd2
                if 0.0 <= midd3 < 1500: mid3 = midd3
            except: pass
            fileOut.write( "%12.3f  %12.3f  %15.3f  %15.3f  %15.3f\n" %(y[ii],x[jj],mid1,mid2,mid3) )
    fileOut.close()

    # write YYYYMMDDHHmm_ssi_cubic.txt
    fileOut = open(outFile , 'w')
    i = np.arange(0, len(y))
    j = np.arange(0, minLonLen)
    for jj in j:
        for ii in i:
            mid = 0.0
            try:
                midd = float(result1[ii, jj])
                if 0.0 <= midd <1500: mid = midd
            except: pass
            fileOut.write( "%15.7f" %(mid) )
        fileOut.write("\n")
    fileOut.close()


# 清空并创建中间结果集
def clearMidDir(fileDir):

    if os.path.exists(fileDir):
        shutil.rmtree(fileDir)
    os.mkdir(fileDir)
