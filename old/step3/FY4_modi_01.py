# -*- coding: utf-8 -*-  


import time,sys,os
from netCDF4 import Dataset 
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import matplotlib.cm as cm


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

    
def geoRefer2xy(geoRefer):
    ncols,nrows,xll,yll,cellsize,NODATA_value = geoRefer
    x = np.linspace(xll,xll+ncols*cellsize-cellsize,ncols)
    y = np.linspace(yll,yll+nrows*cellsize-cellsize,nrows)
    return x,y

    
def interpolat(points,values,x,y):
    xv, yv = np.meshgrid(x, y)
    print('___interp',points.shape,values.shape,xv.shape,yv.shape)
    grid_z2 = griddata(points, values, (xv, yv), method='linear')  #'nearest''linear''cubic'
    return grid_z2

def modiGHI(a,b,r):
    c = a*(1+(r[0]*b/1000+r[1])*0.01)
    return c
def lat2row(lat):
    row = int(((lat - 9.995) / 0.01))
    return row
def topoCorrection(radiaArray,deltHgt):
    print('___topo',radiaArray.shape,deltHgt.shape)
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
    

def getrank(geoRefer,range):
    ncols,nrows,xll,yll,cellsize,NODATA_value = geoRefer
    xmin,xmax,ymin,ymax = range
    rmin = int(np.rint((ymin-yll)/cellsize))
    rmax = int(np.rint((ymax-yll)/cellsize))
    cmin = int(np.rint((xmin-xll)/cellsize))
    cmax = int(np.rint((xmax-xll)/cellsize))
    rank=[cmin,cmax,rmin,rmax]
    print(rank)
    return rank
    
def main(ffy,fddem,outfile,range=None,draw=0):

    #ffy = r'I:\python\data\201711030400_ssi.txt'    
    #fddem = r'I:\python\data\FY4\D_DEM.txt'
    fyarray = np.loadtxt(ffy)
    fyarray[fyarray>9998.0]=np.nan
    ddem,geoRefer = readASCIIfile(fddem)
    nx,ny = geoRefer2xy(geoRefer)
    print(1,geoRefer)
    ddemArr = np.array(ddem)[::-1]
    ddemArr[ddemArr==-9999]=np.nan
    
    if range:   
        rank = getrank(geoRefer,range)
        nx = nx[rank[0]:rank[1]]
        ny = ny[rank[2]:rank[3]]
        ddemArr = ddemArr[rank[2]:rank[3],rank[0]:rank[1]]
    topovalue=[]
    intervalue=[]
    print(2)#,nx,ny)
    for i in [2,3,4]:
        interArray = interpolat(fyarray[:,0:2],fyarray[:,i],nx,ny)
        topocorrArray = topoCorrection(interArray,ddemArr)
        print(interArray.shape,ddemArr.shape,topocorrArray.shape)
        topovalue.append(topocorrArray)
        intervalue.append(interArray)
    print(3)
    if '.nc' in outfile:
        #value = [interArray,ddemArr,topocorrArray]
        array2NC(outfile,topocorrArray,nx,ny)        
    else:
        xx,yy = np.meshgrid(nx,ny)
        print(xx.shape,yy.shape,topovalue[0].shape)
        outvalue = np.dstack((xx.flatten(),yy.flatten(),topovalue[0].flatten(),topovalue[1].flatten(),topovalue[2].flatten())).squeeze()
        np.savetxt(outfile,outvalue,fmt='%.6f',comments=' ')
    print(4)
    if draw:
        maparray(intervalue[0],topovalue[0],ddemArr)

def maparray(value1,value2,value3):
    fig = plt.figure()
    plt.imshow(value1, origin='lower')
    plt.savefig('hi1.png', format='png',  transparent=True, dpi=300)
    plt.imshow(value2, origin='lower')
    plt.savefig('hi2.png', format='png',  transparent=True, dpi=300)    
    plt.imshow(value3, origin='lower')
    plt.savefig('hi3.png', format='png',  transparent=True, dpi=300)    
    
    plt.close()
    
    '''
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
    '''
    
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
    ffy = r'I:\python\data\201711030400_ssi.txt'
    fddem = r'I:\python\data\FY4\D_DEM.txt'
    outfile = r'I:\python\data\FY4\outdata_01.txt'
    #outfile = r'I:\python\data\FY4\outdata_01.nc'
    main(ffy,fddem,outfile,range=[100,110,30,40],draw=0)
    
    
    

