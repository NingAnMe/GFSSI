import os,sys,glob,time,pickle
import numpy as np
from math import ceil,floor,sqrt,pow
from datetime import datetime,timedelta

def readAndWrite(files,fileName_str):
    print(files,fileName_str)
    with open(files[0]) as fd:
        for line in fd:
            oriData = line.split()
            if oriData[0]=='lon':
                continue
            if [oriData[0],oriData[1]] in searchLonlot:
                i = searchLonlot.index([oriData[0],oriData[1]])
                print('*********catched!\n',[float(oriData[0]),float(oriData[1])],searchDot[i],'\noridata:\n',oriData,'\n')
                wfd = open(output_path + searchDot[i][0] + '.txt','a')
                wfd.write(str(fileName_str)+' '+str(oriData[2])+' '+str(oriData[3])+' '+str(oriData[4])+' '+str(oriData[5])+' '+str(oriData[6])+' '+str(oriData[7])+' '+str(oriData[8])+' '+str(oriData[9]))
                wfd.write('\n')
                wfd.close()

def catchEachDot():
    fileName = dt_from
    while fileName < dt_to:
        fileName_str = fileName.strftime("%Y%m%d%H%M")
        year = fileName_str[0:4]
        data_path = data_path_prefix + year +'\\'
        path = data_path + fileName.strftime("%Y%m%d") + '//'
        # try:
        print('\n\ntxt path is:',path+ '*' + fileName_str + '*.txt')
        files = glob.glob(path+ '*' + fileName_str + '*.txt')

        if len(files) == 1:
            # print(files,fileName_str)
            readAndWrite(files,fileName_str) # read each txt
        # except:
        #     print('No' + fileName_str + 'datafiles.')
        fileName += delta

def writeHead(searchDot):
    for dot in searchDot:
        # outName,orilon,orilat = dot.split()
        wfd = open(output_path + dot[0] + '.txt','a')
      #  wfd.write('target lonlat:' + str(dot[3]) + ' ' + str(dot[4]) +' find lonlat:' + str(dot[1]) + ' ' + str(dot[2]) + '\nTime Itotal Ib Id G0 Ai Rb Gt Dni\n')
        wfd.close()

def getsearchDot():
    pf = open(r"searchDot.pkl","rb")
    searchDot = pickle.load(pf)
    searchLonlot = searchDot[:,1:3]
    pf.close()
    searchDot = searchDot.tolist()
    searchLonlot = searchLonlot.tolist()
    print('searchDot is :\n',searchDot,'\nsearchLonlot:\n',searchLonlot)
    return searchDot,searchLonlot

if __name__ == '__main__':
    data_path_prefix = 'H:\\FY4\\Gt\\'
    output_path = 'H:\\FY4\\catchDot\\FSZ\\'
    dt_from = datetime.strptime("20181201","%Y%m%d")
    dt_to = datetime.strptime("20190101","%Y%m%d")
    delta = timedelta(minutes = 15)

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    searchDot,searchLonlot = getsearchDot()
    writeHead(searchDot)
    catchEachDot()