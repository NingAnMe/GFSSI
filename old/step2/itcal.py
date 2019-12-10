import math,os,sys,glob
from datetime import datetime,timedelta

def cos(x):
    return math.cos(math.radians(x))

def sin(x):
    return math.sin(math.radians(x))

def isleap(y):
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0

def calDoy(y,m,d):
    Doy = 0
    a = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if isleap(y):
        a[1] = 29
    for x in a[0:m-1]:
        Doy += x
    return Doy+d

def calDelta(Doy):
    #print "360/365*(284 + Doy) is %f" % (360.0/365*(284 + Doy))
    return 23.45*sin(360.0/365*(284 + Doy))
   
def calOmega(hr,min,lon,E):
    TT = hr + min/60.0 + 4*(lon-120)/60.0 + E/60.0
    return (TT - 12)*15

def calCosThetaz(lat,Delta,Omega):
    return cos(lat)*cos(Delta)*cos(Omega)  + sin(lat)*sin(Delta)
    
def calG0(Doy,CosThetaz):
    return 1366.1*(1 + 0.033 *cos(360.0/365*Doy))*CosThetaz

def calRb(lat,Beta,Delta,Omega,CosThetaz):
    return (cos(lat-Beta)*cos(Delta)*cos(Omega) + sin(lat-Beta)*sin(Delta))/CosThetaz

def calGt(Ib,Id,Ai,Rb,Beta,Itol):
    return (Ib+Id*Ai)*Rb + Id*(1-Ai)*(1+cos(Beta))/2.0 + Itol*0.2*(1-cos(Beta))/2.0

def assignTime(fileName_str):
    y = int(fileName_str[0:4])
    m = int(fileName_str[4:6])
    d = int(fileName_str[6:8])
    hr = int(fileName_str[8:10])+8
    min = int(fileName_str[10:12])
    return y,m,d,hr,min

def assignOriData(oriData):
    return float(oriData[0]),float(oriData[1]),float(oriData[2]),float(oriData[3]),float(oriData[4])

def assignE(fileName_str):
    for x in eData:
        if x[0] == fileName_str[4:8]:
            return float(x[1])

def readAndWrite(files,fileName_str):
    y,m,d,hr,min = assignTime(fileName_str)
    E = assignE(fileName_str)
  #  print "E is %d" % E
    Beta = 35.0
    wfd = open(save_path + fileName_str + '_ssi.txt','w')
    wfd.write("lon lat Itotal Ib Id G0 Ai Rb Gt Dni\n")
    with open(files[0]) as fd:
        for line in fd:
            oriData = line.split()
            lon,lat,Itol,Ib,Id = assignOriData(oriData)
            '''
            print y,m,d,hr,min,lon,lat,Itol,Ib,Id 
            y=2017
            m=8
            d=1
            lon=100.3105
            lat=38.9286
            Itol=338.526
            Ib=155.352
            Id=183.174
            hr=8
            min=30
            E = -7
            print y,m,d,hr,min,lon,lat,Itol,Ib,Id 
            '''
            Doy = calDoy(y,m,d)
            Delta = calDelta(Doy)
            Omega = calOmega(hr,min,lon,E)
            CosThetaz = calCosThetaz(lat,Delta,Omega)
            if Itol==9999.0 or Ib==9999.0 or Id==9999.0:
                G0 = 9999.0
                Ai = 9999.0
                Rb = 9999.0
                Gt = 9999.0
                Dni = 9999.0
            else:
                G0 = calG0(Doy,CosThetaz)
                Ai = Ib/G0
                Rb = calRb(lat,Beta,Delta,Omega,CosThetaz)
                Gt = calGt(Ib,Id,Ai,Rb,Beta,Itol)
                Dni = Ib/CosThetaz
            '''
            print "Doy is %d" % Doy
            print "Delta is %f " % Delta
            print "Omega is %f" % Omega
            print "CosThetaz is %f " % CosThetaz
            print "go is %f" % G0
            print "Ai is %f" % Ai
            print "Rb is %f" % Rb
            print "Gt is %f" % Gt
            '''
            wfd.write(str(round(lon,4))+' '+str(round(lat,4))+' '+str(round(Itol,2))+' '+str(round(Ib,2))+' '+str(round(Id,2))+' '+str(round(G0,2))+' '+str(round(Ai,2))+' '+str(round(Rb,2))+' '+str(round(Gt,2))+' '+str(round(Dni,2)))
            wfd.write('\n')

            #sys.exit()

data_path = 'I:\\FY4\\unzipNC\\2017\\'
output_path = 'F:\\FY4\\GT\\'
year = "2017"



if not os.path.exists(output_path + year):
    os.makedirs(output_path + year)

dt_from = datetime.strptime("20170901","%Y%m%d")
dt_to = datetime.strptime("20170902","%Y%m%d")
delta = timedelta(minutes = 15)

eData = []
with open('ep.txt') as fd:
    for line in fd:
        eData.append(line.split())

fileName = dt_from

while fileName <= dt_to:
    path = data_path + fileName.strftime("%Y%m%d") + '//'
    save_path = output_path + year + '//' + fileName.strftime("%Y%m%d") + '//'
    fileName_str = fileName.strftime("%Y%m%d%H%M")

  #  print "fileName_str is %s " % fileName_str
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    try:
        files = glob.glob(path+ '*' + fileName_str + '*.txt')
        if len(files) == 1:
            readAndWrite(files,fileName_str)

    except:
        print('No' + fileName_str + 'datafiles.')
    fileName += delta
