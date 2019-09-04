# -*- coding: utf-8 -*-  


import time,sys,os
from netCDF4 import Dataset 
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def readlatlon(file_path):
    arr = []
    with open(file_path,'r') as f:
        for Line in f:
            arr.append(list(map(float, Line.split())))
    return arr


def readASCIIfile(ASCIIfile):
    arr = []
    geoRefer = []
    
    fh = iter(open(ASCIIfile))
    skiprows = 6
    
    for i in range(skiprows):
        try:
            this_line = next(fh)
            geoRefer.append(float(this_line.split()[1]))
        except StopIteration:break
        
    while 1:
        try:
            this_line = next(fh)
            if this_line:
                arr.append(list(map(float, this_line.split())))
        except StopIteration:break
    fh.close()
    return arr,geoRefer

    
def FYToArray(fyfile):
    data = Dataset(fyfile)
    namelist = ['SSI','DirSSI','DifSSI']
    value = []
    for j in namelist:
        dataarr = data.variables[j][:1400]
        dataarr[dataarr>2000]=np.nan
        dataarr[dataarr==-9999]=np.nan
        dataarr[dataarr==9999]=np.nan
        value.append(dataarr)
    return np.array(value)
    
def geoRefer2xy(geoRefer):
    ncols,nrows,xll,yll,cellsize,NODATA_value = geoRefer
    x = np.arange(xll,xll+ncols*cellsize,cellsize)
    y = np.arange(yll,yll+nrows*cellsize,cellsize)
    return x,y

    
def interpolat(points,values,x,y):
    print('t01')
    xv, yv = np.meshgrid(x, y)
    print('t02',points.shape,values.shape,xv.shape,yv.shape)
    grid_z2 = griddata(points, values, (xv, yv), method='linear')  #'nearest''linear''cubic'
    return grid_z2

def modiGHI(a,b,r):
    c = a*(1+(r[0]*b/1000+r[1])*0.01)
    return c
def lat2row(lat):
    row = int(((lat - 9.995) / 0.01))
    return row
def topoCorrection(radiaArray,deltHgt):
    print(5)
    ghi_ri=[]
    rr = [[2.6036,0.0365],[2.6204,0.0365],[2.6553,0.0362],[2.6973,0.0356],[2.7459,0.0343]\
          ,[2.8012,0.0324],[2.8616,0.0299],[2.9236,0.0257],[2.9870,0.0204]]

    if len(deltHgt) == len(radiaArray):
        for i in range(len(deltHgt)):
            if i>=lat2row(52.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]),np.array(deltHgt[i]),rr[8]))
            if i>=lat2row(47.5) and i<lat2row(52.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]),np.array(deltHgt[i]),rr[7]))
            if i>=lat2row(42.5) and i<lat2row(47.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]),np.array(deltHgt[i]),rr[6]))
            if i>=lat2row(37.5) and i<lat2row(42.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]),np.array(deltHgt[i]),rr[5]))
            if i>=lat2row(32.5) and i<lat2row(37.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]),np.array(deltHgt[i]),rr[4]))
            if i>=lat2row(27.5) and i<lat2row(32.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]),np.array(deltHgt[i]),rr[3]))
            if i>=lat2row(22.5) and i<lat2row(27.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]),np.array(deltHgt[i]),rr[2]))
            if i>=lat2row(17.5) and i<lat2row(22.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]),np.array(deltHgt[i]),rr[1]))
            if i<lat2row(17.5):
                ghi_ri.append(modiGHI(np.array(radiaArray[i]),np.array(deltHgt[i]),rr[0]))
    return np.array(ghi_ri)
    
def array2NC(ncfile,value,x,y):
    
    Rnum = len(y)
    Cnum = len(x)
   
    ncf = Dataset(ncfile,"w")
    lat = ncf.createDimension("lat", Rnum)
    lon = ncf.createDimension("lon", Cnum)
    
    latitudes = ncf.createVariable("lat","f4",("lat",))
    longitudes = ncf.createVariable("lon","f4",("lon",))
    Value1 = ncf.createVariable("V1","f4",("lat","lon"))
    Value2 = ncf.createVariable("V2","f4",("lat","lon"))
    Value3 = ncf.createVariable("V3","f4",("lat","lon"))
    
    #latitudes.units = "degrees north"
    #longitudes.units = "degrees east"
    #FristValue.units = ""

    latitudes[:] = y
    longitudes[:] = x
    Value1[:] = value[0]
    Value2[:] = value[1]
    Value3[:] = value[2]
    ncf.close()
    
def maparray(value1,value2,value3):
    fig = plt.figure()
    plt.subplot(221)
    plt.imshow(value1, origin='lower')
    plt.title('value1')
    plt.subplot(222)
    plt.imshow(value2, origin='lower')
    plt.title('value2')
    plt.subplot(223)
    plt.imshow(value3, origin='lower')
    plt.title('value3')    
    plt.show()
    
def selectpoint(lon,lat):
    ijList = []
    for i in range(0, 1400):
        for j in range(0, len(lat[0])):
            if float(lon[i][j])>70 and float(lon[i][j])<140 and float(lat[i][j])<55 and float(lat[i][j])>0:
                ijList.append([i,j,lat[i][j],lon[i][j]])
    return ijList
def getvalue(ijList,radiValue):
    lines = []
    for k in ijList:
        row,col,lat,lon = k
        i,j = int(row),int(col)
        line = [lon,lat,radiValue[0,i,j],radiValue[1,i,j],radiValue[2,i,j]]
        lines.append(line)
    return lines
    
def main():
    #lat_path = r'I:\do\FY4\lat-4000-2WEI.txt'
    #lon_path = r'I:\do\FY4\lon-4000-2JING.txt'
    FY_path = r'I:\do\FY4\FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_20170801040000_20170801041459_4000M_V0001.NC'
    ddem_path = r'I:\do\FY4\D_DEM.txt'
    ncfile = r'I:\do\FY4\FY4SSI.nc'
    file3 =r'I:\do\FY4\latlonfile.txt'
    
    #prepare scat
    print('a')
    radiValue = FYToArray(FY_path)   #SSI_data,DirSSI_data,DifSSI_data=FYToArray(FY_path)
    #lat = np.loadtxt(lat_path)  #np.array(readlatlon(lat_path))
    #lon = np.loadtxt(lon_path)   #np.array(readlatlon(lon_path))
    
    print('b')
    #ijList = np.array(selectpoint(lon,lat))
    #np.savetxt(file3,ijList,fmt='%.6f',comments=' ')
    ijList = np.loadtxt(file3)
    lines = getvalue(ijList,radiValue)
    '''
    ipath = r'I:\do\FY4\201708010400_cssi.txt'
    with open(ipath,'r') as f:
        for Line in f:
            #print len(latLine.split())
            lines.append(list(map(float, Line.split())))
    '''
    print('c',lines[1000])
    #points = np.dstack((lon.ravel(),lat.ravel()))[0]    
    #points = np.dstack((lon.ravel(),lat.ravel(),SSI_data.ravel(),DirSSI_data.ravel(),DifSSI_data.ravel()).squeeze()
    points = np.array(lines).squeeze()
    print('d',points[0])
    #prepare grid
    ddem,geoRefer = readASCIIfile(ddem_path)
    nx,ny = geoRefer2xy(geoRefer)
    
    print('f',nx,ny,geoRefer)
    #ddemArr = np.flipud(np.array(ddem))
    ddemArr = np.array(ddem)[::-1]
    ddemArr[ddemArr==-9999]=np.nan
    
    print('g',points[:,0:2].shape,points[:,2].shape)
    interArray = interpolat(points[:,0:2],points[:,2],nx,ny)
    
    #terrain Correction
    print('h',interArray.shape,ddemArr.shape)
    topocorrArray = topoCorrection(interArray,ddemArr)
    
    #save array    
    print('i',topocorrArray.shape)
    value = [interArray,ddemArr,topocorrArray]
    array2NC(ncfile,value,nx,ny)
    print('j',topocorrArray.shape,len(nx),len(ny))
    maparray(interArray,topocorrArray,ddemArr)

def test():
    
    ddem_path = r'I:\do\FY4\D_DEM.txt'
    '''
    x,y = np.meshgrid(np.arange(70, 140, 0.05), np.arange(10, 50, 0.05)) 
    value = np.sqrt(x ** 2 + y ** 2)
    
    points = np.dstack((x.ravel(),y.ravel()))[0]
    va = value.ravel()
    '''
    ddemArr = np.loadtxt(ddem_path,skiprows=6)
    #ddem,geoRefer = readASCIIfile(ddem_path)
    
    #ddemArr = np.array(ddem)
    #ddemArr[ddemArr==-9999.0]=np.nan
    print(ddemArr.shape,ddemArr.max(),ddemArr.min(),ddemArr[2000:2010,2000:2010])
    #print(array.type)
    
    #print(ddemArr,array)
    fig = plt.figure()
    y = np.arange(ddemArr.shape[0])
    x = np.arange(ddemArr.shape[1])
    xv,yv = np.meshgrid(x,y)
    print(x,y)
    plt.contourf(xv,yv,ddemArr)
    #plt.imshow(ddemArr, vmax=abs(ddemArr).max(), vmin=-abs(ddemArr).max(),cmap=cm.RdYlGn,origin='lower')
    plt.show()
    
if __name__ == '__main__':
    main()

