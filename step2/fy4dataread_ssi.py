import netCDF4 as nc
import os,sys
from datetime import datetime,timedelta
import glob

def changeFormat(x,n):
    return str(round(float(x),n))

data_path = 'F:/FY4/0423/2018/'
output_path = 'F:/FY4/'
lat_path = 'lat-4000-2WEI.txt'
lon_path = 'lon-4000-2JING.txt'
lat = []
lon = []
year = "2018"

if not os.path.exists(output_path + year):
    os.makedirs(output_path + year)

with open(lat_path,'r') as f:
    for latLine in f:
        #print len(latLine.split())
        lat.append(latLine.split())
#print lat

with open(lon_path,'r') as f:
    for lonLine in f:
        #print len(lonLine.split())
        lon.append(lonLine.split())
#print lon

dt_from = datetime.strptime("20180423","%Y%m%d")
dt_to = datetime.strptime("20180424","%Y%m%d")
delta = timedelta(minutes = 15)

start = dt_from

while start <= dt_to:
    path = data_path + start.strftime("%Y%m%d") + '//'
    save_path = output_path + year + '//' + start.strftime("%Y%m%d") + '//'
    t_str = start.strftime("%Y%m%d%H%M")

    print(t_str)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    #try:
    files = glob.glob(path+ '*' + t_str + '*.NC')
    if len(files) == 1:
        data = nc.Dataset(files[0])

        SSI_data = data.variables['SSI'][:]
        DirSSI_data = data.variables['DirSSI'][:]
        DifSSI_data = data.variables['DifSSI'][:]

        SSI_data[SSI_data>2000]=9999
        DirSSI_data[SSI_data>2000]=9999
        DifSSI_data[SSI_data>2000]=9999

        print(len(SSI_data), len(SSI_data[0]))
        print(len(DirSSI_data), len(DirSSI_data[0]))
        print(len(DifSSI_data), len(DifSSI_data[0]))

        with open(save_path + t_str + '_ssi.txt','w') as fd:
            for i in range(0, 1400):
                for j in range(0, len(SSI_data[0])):
                    #print lon[i][j],lat[i][j]
                    if str(SSI_data[i][j]) == '--':
                        SSI_data[i][j] = 9999
                    elif str(DirSSI_data[i][j]) == '--':
                        DirSSI_data[i][j] = 9999
                    elif str(DifSSI_data[i][j]) == '--':
                        DifSSI_data[i][j] = 9999
                    elif float(lon[i][j])>70 and float(lon[i][j])<140 and float(lat[i][j])<55 and float(lat[i][j])>0:
                        #print str(lon[i][j])+' '+str(lat[i][j])+' '+str(SSI_data[i][j])+' '+str(DirSSI_data[i][j])+' '+str(DifSSI_data[i][j])+' '
                        #fd.write(str(round(lon[i][j],4))+' '+str(round(lat[i][j],4))+' '+str(round(SSI_data[i][j],2))+' '+str(round(DirSSI_data[i][j],2))+' '+str(round(DifSSI_data[i][j],2))+' ')
                        fd.write(changeFormat(lon[i][j],4)+' '+changeFormat(lat[i][j],4)+' '+changeFormat(SSI_data[i][j],2)+' '+changeFormat(DirSSI_data[i][j],2)+' '+changeFormat(DifSSI_data[i][j],2)+' ')                            
                        fd.write('\n')
                        #pass
        fd.close()
            #os.system('rename E://FY4//ssi.txt '+newfilename)

    #except:
        #print('No' + t_str + 'datafiles.')

    start += delta
