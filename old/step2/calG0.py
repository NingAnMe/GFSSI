import math,os,sys,glob
from datetime import datetime,timedelta
def is_number(s):
    if s == 'nan':
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False

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
    # print(fileName_str)
    y = int(fileName_str[0:4])
    m = int(fileName_str[4:6])
    d = int(fileName_str[6:8])
    hr = int(fileName_str[8:10])+8
    min = int(fileName_str[10:12])
    return y,m,d,hr,min

def assignOriData(oriData):
    return float(oriData[0]),float(oriData[1]),float(oriData[2]),float(oriData[3]),float(oriData[4])

def assignE(fileName_str,eData):
    for x in eData:
        if x[0] == fileName_str[4:8]:
            return float(x[1])

def judgeGt(Gt):
    # print('this is in judgeGt',Gt,is_number(Gt),float(Gt)<0)
    if is_number(Gt):
        if float(Gt)<0:
            return False
    return True

def calG0begin(line,lat,lon,eData,onlyG0=1):
    # print('line:',line)
    fileName_str = line[0]
    y,m,d,hr,min = assignTime(fileName_str)
    E = assignE(fileName_str,eData)
    Beta = 35.0
    # print("E is ",E)
    Doy = calDoy(y,m,d)
    Delta = calDelta(Doy)
    Omega = calOmega(hr,min,lon,E)
    CosThetaz = calCosThetaz(lat,Delta,Omega)
    G0 = calG0(Doy,CosThetaz)
    # print('(y,m,d,hr,min,E,Doy,Delta,Omega,CosThetaz,G0)值:\n',y,m,d,hr,min,E,Doy,Delta,Omega,CosThetaz,G0)
    if onlyG0 == 1:
        return G0
    else: # itotal 无效 （nan 或9999或负 或itotal>G0）
        Itol = 0.5*G0
        Ib = 0.3*Itol
        Id = 0.7*Itol
        Ai = Ib/G0
        Rb = calRb(lat,Beta,Delta,Omega,CosThetaz)
        Gt = calGt(Ib,Id,Ai,Rb,Beta,Itol)
        # print(Gt,G0)
        if judgeGt(Gt) == False:
            Gt = 0.8*G0
        Dni = Ib/CosThetaz
        # print('Ib=',Ib,'CosThetaz=',CosThetaz,'Dni=',Dni)
        # print('Itol,Ib,Id,G0,Ai,Rb,Gt,Dni值为：',[str(round(Itol,2)),str(round(Ib,2)),str(round(Id,2)),str(round(G0,2)),str(round(Ai,2)),str(round(Rb,2)),str(round(Gt,2)),str(round(Dni,2))])
        return [str(round(Itol,2)),str(round(Ib,2)),str(round(Id,2)),str(round(G0,2)),str(round(Ai,2)),str(round(Rb,2)),str(round(Gt,2)),str(round(Dni,2))]


