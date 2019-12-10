import netCDF4 as nc
import os,sys
from datetime import datetime,timedelta
import glob


def changeFormat(x,n):
    return str(round(float(x),n))


fy4_ssi_file = 'FY4A-_AGRI--_N_DISK_1047E_L2-_SSI-_MULT_NOM_20190630050000_20190630051459_4000M_V0001.NC'
lat_path = 'lat-4000-2WEI.txt'
lon_path = 'lon-4000-2JING.txt'
lat = []
lon = []

with open(lat_path,'r') as f:
    for latLine in f:
        print(len(latLine.split()))
        lat.append(latLine.split())

with open(lon_path,'r') as f:
    for lonLine in f:
        print(len(lonLine.split()))
        lon.append(lonLine.split())


def ssi_nc2txt():
    data = nc.Dataset(fy4_ssi_file)

    SSI_data = data.variables['SSI'][:]
    DirSSI_data = data.variables['DirSSI'][:]
    DifSSI_data = data.variables['DifSSI'][:]

    SSI_data[SSI_data > 2000] = 9999
    DirSSI_data[SSI_data > 2000] = 9999
    DifSSI_data[SSI_data > 2000] = 9999

    print(len(SSI_data), len(SSI_data[0]))
    print(len(DirSSI_data), len(DirSSI_data[0]))
    print(len(DifSSI_data), len(DifSSI_data[0]))

    with open('20190630050000' + '_ssi.txt', 'w') as fd:
        for i in range(0, 1400):
            for j in range(0, len(SSI_data[0])):
                # print lon[i][j],lat[i][j]
                if str(SSI_data[i][j]) == '--':
                    SSI_data[i][j] = 9999
                elif str(DirSSI_data[i][j]) == '--':
                    DirSSI_data[i][j] = 9999
                elif str(DifSSI_data[i][j]) == '--':
                    DifSSI_data[i][j] = 9999
                elif float(lon[i][j]) > 70 and float(lon[i][j]) < 140 and float(lat[i][j]) < 55 and float(
                        lat[i][j]) > 0:
                    # print str(lon[i][j])+' '+str(lat[i][j])+' '+str(SSI_data[i][j])+' '+str(DirSSI_data[i][j])+' '+str(DifSSI_data[i][j])+' '
                    # fd.write(str(round(lon[i][j],4))+' '+str(round(lat[i][j],4))+' '+str(round(SSI_data[i][j],2))+' '+str(round(DirSSI_data[i][j],2))+' '+str(round(DifSSI_data[i][j],2))+' ')
                    fd.write(changeFormat(lon[i][j], 4) + ' ' + changeFormat(lat[i][j], 4) + ' ' + changeFormat(
                        SSI_data[i][j], 2) + ' ' + changeFormat(DirSSI_data[i][j], 2) + ' ' + changeFormat(
                        DifSSI_data[i][j], 2) + ' ')
                    fd.write('\n')
                    # pass

ssi_nc2txt()
