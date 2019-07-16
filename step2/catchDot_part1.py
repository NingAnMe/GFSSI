import pickle
import numpy as np
from math import ceil,floor,sqrt,pow

def getAdLatlon(lon,lat):
    if(round(float(lon)) == float(lon)):
        adjLon = [float(lon+1),float(lon-1)]
    else:
        adjLon = [float(ceil(lon)),float(floor(lon))]
    if (round(float(lat)) == float(lat)):
        adjLat = [float(lat+1),float(lat-1)]
    else:
        adjLat = [float(ceil(lat)),float(floor(lat))]
    return adjLon,adjLat

def calLonLat(lon,lat):
    print('   dest:',lon,lat)
    adjLon,adjLat = getAdLatlon(lon,lat)
    oalist = []
    distance = []
    print('       adjLon,adjLat',adjLon,adjLat)
    #change 2:
    with open(data_path + '\\20180704\\20180704000000_ssi.txt') as fd:
        for line in fd: # record lon,lat list(oalist) for cal
            try:
                oriLon,oriLat = float(line.split()[0]),float(line.split()[1])
            except:
                #print(line)
                continue
            if (oriLon<=adjLon[0]) and (oriLon >=adjLon[1]):
                if (oriLat<=adjLat[0]) and (oriLat >=adjLat[1]):
                    distance = sqrt(pow(oriLon-lon,2)+pow(oriLat-lat,2))
                    oalist.append([oriLon,oriLat,distance])
    oalist = sorted(oalist, key=lambda x: x[2], reverse=False)
    print('       this dot is search:\n       ',oalist[0][0],oalist[0][1])
    return oalist[0][0],oalist[0][1]

def getDot():
    dot = []
    searchDot = []
    searchLonlot = []
    with open('Dots_JZ.txt') as fd:
        for line in fd:
            outName,orilon,orilat = line.split()
            dot.append(line.split())
            searchLon,searchLat = calLonLat(float(orilon),float(orilat))
            searchDot.append([outName,searchLon,searchLat,orilon,orilat])
    return np.array(dot),np.array(searchDot)

if __name__ == '__main__':
    data_path = 'F:\\FY4\\shen\\autoGt\\2018\\'
    output_path = 'F:\\FY4\\'
    dot,searchDot = getDot()
    print(dot,'\n\n',searchDot)
    pf = open('searchDots_JZ.pkl','wb')
    pickle.dump(searchDot,pf)
    pf.close()