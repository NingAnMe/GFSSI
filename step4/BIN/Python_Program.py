#!/usr/bin/python
# -*- coding: utf-8 -*-
#for the type 3.5 or 2.7




#++++++++++++++++++++++++++    时间处理段    ++++++++++++++++++++++++++        
#+++++    nyear() 用于判断平润年  +++++
#+++++   nmonth() 用于统计该月天数  +++++
#+++++ ndate_JD() 用于把年月日转换为儒略日  +++++
#+++++ ndate_AD() 用于把儒略日转换为年月日  +++++   
#+++++ add_hour() 用于计算小时累加值  +++++ 
#+++++  weekday() 用于计算年月日对应的星期数  +++++
#+++++  add_day() 用于计算日期的累加值  +++++ 


#+++ 计算第iyear年平闰状况,平年:0,闰年:1 +++
#+++ 例输入2016 得到1 +++ 
def nyear(iyear):
    result=0
    if iyear%400==0:                 result=1
    if iyear%100!=0 and iyear%4==0 : result=1
    return result
if __name__=='__main__': print (nyear(2016))


#+++ 计算第iyear年imonth月有多少天,考虑平闰年 +++
#+++ 例输入2016,02 得到29 +++ 
def nmonth(iyear,imonth):
    pin_day=[31,28,31,30,31,30,31,31,30,31,30,31]
    if imonth==2:
        return pin_day[imonth-1]+nyear(iyear)
    else:
        return pin_day[imonth-1]
if __name__=='__main__': print (nmonth(2016,2))


#+++ 用于把年月日转换为儒略日 +++
#+++ 例输入2016,03,03 得到2016,63 +++ 
def ndate_JD(iyear,imonth,iday):
    pin_day=[31,28,31,30,31,30,31,31,30,31,30,31]
    JD=iday
    for i in range(imonth-1):
        JD=JD+pin_day[i]
    if imonth>=3: JD=JD+nyear(iyear)
    return (iyear,JD)
if __name__=='__main__': print (ndate_JD(2016,3,3)) 


#+++ 用于把儒略日转换为年月日 +++
#+++ 例输入2016,63 得到2016,03,03 +++ 
def ndate_AD(iyear,JD):
    pin_day=[0,31,59,90,120,151,181,212,243,273,304,334]
    run_day=[0,31,60,91,121,152,182,213,244,274,305,335]
    imonth=12
    if nyear(iyear)==1:
        for i in range(11):
            if run_day[i] < JD <= run_day[i+1]: imonth=i+1
        iday=JD-run_day[imonth-1]
    else:
        for i in range(11):
            if pin_day[i] < JD <= pin_day[i+1]: imonth=i+1        
        iday=JD-pin_day[imonth-1]
    if JD >366: return (iyear,9999,9999)
    else:       return (iyear,imonth,iday)
if __name__=='__main__': print (ndate_AD(2016,63))


#+++ 用于小时数的累加,能跨年运算 +++
#+++ 例输入2016,01,10,20,5 得到2016,01,11,1 +++ 
def add_hour(iyear,imonth,iday,ihour,addhour):
    (now_year,now_date)=ndate_JD(iyear,imonth,iday)
    now_hour=ihour+addhour
    final_hour=now_hour%24
    final_date=now_date+(now_hour-final_hour)/24
    if final_date > (365+nyear(now_year)):
        final_date=final_date-(365+nyear(now_year))
        now_year=now_year+1
    (final_year,final_month,final_day)=ndate_AD(now_year,final_date)
    return (final_year,final_month,final_day,final_hour)
if __name__=='__main__': print (add_hour(2016,12,31,23,5))


#+++ 计算iyear,imonth,iday是周几 +++
#+++ 例输入2016,1,1 得到5 +++
#+++ 基于2010年1月1日是周五,往后推算 +++
def weekday(iyear,imonth,iday):
    (runyear,JD)=ndate_JD(iyear,imonth,iday)
    nday=JD
    for i in range(iyear-2010):
        nday=nday+365+nyear(2010+i)
    weektime=(nday+4)%7
    if weektime==0: weektime=7
    return weektime
if __name__=='__main__': print (weekday(2017,3,28))




#+++ 计算iyear,imonth,iday之后增减addiday后的日期,最大跨度为1年 +++
#+++ 例输入2016,1,1,-1 得到2015,12,31 +++
def add_day(iyear,imonth,iday,add):
    (runyear,JD)=ndate_JD(iyear,imonth,iday)
    runday=JD+add
    if runday<=0 :
        runyear=runyear-1
        runday=runday+365+nyear(runyear)
    elif runday>(365+nyear(runyear)):
        runday=runday-365-nyear(runyear)
        runyear=runyear+1
    else: pass           
    (final_year,final_month,final_day)=ndate_AD(runyear,runday)
    return (final_year,final_month,final_day)        
if __name__=='__main__': print (add_day(2015,12,31,60))



#++++++++++++++++++++++++++    时间处理段    ++++++++++++++++++++++++++   






#++++++++++++++++++++++++++    误差统计段    ++++++++++++++++++++++++++   
#+++++        COR() 计算相关系数R  +++++
#+++++     CORMSE() 计算均方根误差RMSE  +++++
#+++++      COMAE() 计算绝对平均误差MAE  +++++
#+++++ COR_Matrix() 计算相关系数矩阵  +++++



def COR(X,Y):
    """  caculate the R of X and Y  """
    import math
    num=len(X)
    if len(X)!=len(Y) or len(X)==0:
        print ("list X and list Y have different length!")
        R=9999.0
        return R
    else:
        SXY=0.0
        SX =0.0
        SY =0.0
        SX2=0.0
        SY2=0.0
        for i in range(num):
            SXY=SXY+X[i]*Y[i]
            
            SX=SX+X[i]
            SY=SY+Y[i]
            SX2=SX2+X[i]*X[i]
            SY2=SY2+Y[i]*Y[i]
        midX=math.sqrt( SX2- math.pow(SX,2)/num )
        midY=math.sqrt( SY2- math.pow(SY,2)/num )
        if midX==0 or midY==0:
            print ("list X or list Y is equal list!")
            R=0.0
            return R
        else:
            R=SXY-SX*SY/num
            R=R/(midX*midY)
            return R


def CORMSE(X,Y):
    """  caculate the RMSE of X and Y  """
    import math
    num=len(X)
    if len(X)!=len(Y) or len(X)==0:
        print ("list X and list Y have different length!")
        RMSE=9999.0
        return RMSE
    else:
        wucha=0.0
        for i in range(num):
            wucha=wucha+ math.pow((X[i]-Y[i]),2)
        RMSE=math.sqrt(wucha/num)
        return RMSE


def COMAE(X,Y):
    """  caculate the MAE of X and Y  """
    import math
    num=len(X)
    if len(X)!=len(Y) or len(X)==0:
        print ("list X and list Y have different length!")
        MAE=9999.0
        return MAE
    else:
        wucha=0.0
        for i in range(num):
            wucha=wucha+ math.fabs(X[i]-Y[i])
        MAE=wucha/num
        return MAE


def COR_Matrix(X):
    """   caculate the R Matrix between Xi and Xj
    data in X must be real
    when if i!=j,cacualate the R of Xi and Xj,
    in order to judge the relationship within the X  
    return Matrix like [[1 X X],[0 1 X],[0 0 1]]
    """
    import math
    num_row=len(X)
    num_clo=len(X[0])   

    if num_row<=2 or num_clo<2:
        print ("data input is not enough!")
        result=9999.0
    else:
        result=[]
        for i in range(num_clo):
            mid=[]
            for j in range(num_clo):
                if i>j:
                    mid.append(0)
                elif i==j :
                    mid.append(1)
                else:                  
                    mid.append( COR(X[:][i],X[:][j]) )
            result.append(mid)
    return result


#++++++++++++++++++++++++++    误差统计段    ++++++++++++++++++++++++++   





#++++++++++++++++++++++++++    污染数值处理段    ++++++++++++++++++++++++++   
#+++++   caculate_AQI() 用于计算日均AQI,等级和首要污染物  +++++
#+++++   caculate_iaqi()用于计算小时IAQI  +++++
#+++++   caculate_aqi() 用于计算小时AQI,首要污染物  +++++
#+++++   range_AQI() 用于计算AQI的等级(1——6)  +++++


#+++ base on the data of 6 kind of pollute,caculate the AQI +++
def caculate_AQI(so2,no2,pm10,pm25,co,o3):
    data_AQI=[0,50,100,150,200,300,400,500]
    data_so2=[0,50,150,475,800,1600,2100,2620]
    data_no2=[0,40,80,180,280,565,750,940]
    data_pm10=[0,50,150,250,350,420,500,600]
    data_pm25=[0,35,75,115,150,250,350,500]
    data_co=[0,2,4,14,24,36,48,60]
    data_o3=[0,100,160,215,265,800]

    IAQI=[9999 for i in range(6)]
    #++  caculate IAQI for so2  ++
    if so2>data_so2[len(data_so2)-1] and so2<=4000: IAQI[0]=500    
    for i in range(len(data_so2)-1):
        if so2>data_so2[i] and so2<=data_so2[i+1]:
            IAQI[0]=data_AQI[i]+ int(round(1.0*(so2-data_so2[i])*(data_AQI[i+1]-data_AQI[i])/(data_so2[i+1]-data_so2[i])))
    if so2>0 and so2<=1:IAQI[0]=1
            
    #++  caculate IAQI for no2  ++
    if no2>data_no2[len(data_no2)-1] and no2<=2000: IAQI[1]=500    
    for i in range(len(data_no2)-1):
        if no2>data_no2[i] and no2<=data_no2[i+1]:
            IAQI[1]=data_AQI[i]+ int(round(1.0*(no2-data_no2[i])*(data_AQI[i+1]-data_AQI[i])/(data_no2[i+1]-data_no2[i])))     
    if no2>0 and no2<=1:IAQI[1]=1
    
    #++  caculate IAQI for pm10  ++
    if pm10>data_pm10[len(data_pm10)-1] and pm10<=4000: IAQI[2]=500    
    for i in range(len(data_pm10)-1):
        if pm10>data_pm10[i] and pm10<=data_pm10[i+1]:
            IAQI[2]=data_AQI[i]+ int(round(1.0*(pm10-data_pm10[i])*(data_AQI[i+1]-data_AQI[i])/(data_pm10[i+1]-data_pm10[i])))
    if pm10>0 and pm10<=1:IAQI[2]=1
    
    #++  caculate IAQI for pm25  ++
    if pm25>data_pm25[len(data_pm25)-1] and pm25<=4000: IAQI[3]=500    
    for i in range(len(data_pm25)-1):
        if pm25>data_pm25[i] and pm25<=data_pm25[i+1]:
            IAQI[3]=data_AQI[i]+ int(round(1.0*(pm25-data_pm25[i])*(data_AQI[i+1]-data_AQI[i])/(data_pm25[i+1]-data_pm25[i])))
    if pm25>0 and pm25<=1:IAQI[3]=1
    
    #++  caculate IAQI for co  ++
    if co>data_co[len(data_co)-1] and co<=120: IAQI[4]=500    
    for i in range(len(data_co)-1):
        if co>data_co[i] and co<=data_co[i+1]:
            IAQI[4]=data_AQI[i]+ int(round(1.0*(co-data_co[i])*(data_AQI[i+1]-data_AQI[i])/(data_co[i+1]-data_co[i])))
    if co>0 and co<=0.02:IAQI[4]=1
    
    #++  caculate IAQI for o3  ++
    if o3>data_o3[len(data_o3)-1] and o3<=4000: IAQI[5]=500 
    for i in range(len(data_o3)-1):
        if o3>data_o3[i] and o3<=data_o3[i+1]:
            IAQI[5]=data_AQI[i]+ int(round(1.0*(o3-data_o3[i])*(data_AQI[i+1]-data_AQI[i])/(data_o3[i+1]-data_o3[i])))
    if o3>0 and o3<=1:IAQI[5]=1

    #++  caculate AQI and primary ++
    AQI=0
    primary=0
    for i in range(6):
        if IAQI[i]<=500 and IAQI[i]>AQI:
            AQI=IAQI[i]
            primary=i+1
 
    #++  caculate grade ++
    if AQI<=0 or AQI>500:
        AQI=9999
        grade=9999
        primary=9999
    elif AQI<=50:
        grade=1
        primary=0
    elif AQI<=100:
        grade=2
    elif AQI<=150:
        grade=3
    elif AQI<=200:
        grade=4
    elif AQI<=300: 
        grade=5
    else:
        grade=6       
    return(AQI,grade,primary)



#++++  caculate the periaqi for 6 pollute  ++++
#++++  kind:the kind of pollute ; value:the data of the pollute  ++++
#++++  if value>5000 mean that data is lost,then IAQI=9999  ++++ 
def caculate_iaqi(kind,value):

    IAQI_range=[0,50,100,150,200,300,400,500]
    if kind==1: po_range=[0,150,500,650,800]                   #SO2
    if kind==2: po_range=[0,100,200,700,1200,2340,3090,3840]   #NO2
    if kind==3: po_range=[0,50,150,250,350,420,500,600]        #PM10
    if kind==4: po_range=[0,35,75,115,150,250,350,500]         #PM25
    if kind==5: po_range=[0,5,10,35,60,90,120,150]             #CO
    if kind==6: po_range=[0,160,200,300,400,800,1000,1200]     #O3
     
    #++++  value to IAQI for different po_range  ++++
    len_range=len(po_range)
    if value>=5000:
        IAQI=9999 
    elif value>=po_range[len_range-1]:
        IAQI=IAQI_range[len_range-1]
    else:
        flag=0
        for i in range(len_range-2):
            if value>=po_range[i+1] and value<po_range[i+2]: flag=i+1
        IAQI=IAQI_range[flag]+1.0*(IAQI_range[flag+1]-IAQI_range[flag])*abs(value-po_range[flag])/(po_range[flag+1]-po_range[flag])
    return int(IAQI) 
    #++++  value to IAQI for different po_range  ++++
  


#++++  caculate the aqi of 6 pollute  ++++
#++++  kind=1,so2; kind=2,no2; kind=3,pm10; kind=4,pm25; kind=5,co; kind=6,o3;  ++++
def caculate_aqi(pollute_data):
    
    pollute_name=['SO2','NO2','PM10','PM25','CO','O3']
    #++++  caculate the IAQI for each pollute  ++++
    IAQI=[9999 for i in range(6)]
    for i in range(6): IAQI[i]=caculate_iaqi(i+1,pollute_data[i])
    #++++  caculate the (AQI,PRI) in max of IAQI  ++++   
    AQI=-1
    PRI=-1
    for i in range(6):
        if IAQI[i]>AQI and IAQI[i]<501:
            AQI=IAQI[i]
            PRI=i
    PRIC='9999'
    if AQI==-1 : AQI=9999
    if AQI<50 : PRIC='NONE'
    if AQI>=50: PRIC='%4s'%(pollute_name[PRI])
    return(AQI,PRIC)



#++++  caculate the range of aqi  ++++
#++++  if value>500 mean that data is lost,then range=9999  ++++ 
def range_AQI(value):
    AQI_range=[0,50,100,150,200,300,400,500]
    if value>500:      rang=9999
    if 300<value<=500: rang=6
    if 200<value<=300: rang=5
    if 150<value<=200: rang=4
    if 100<value<=150: rang=3
    if 50<value<=100:  rang=2
    if value<=50:      rang=1
    return(rang)


    
#++++++++++++++++++++++++++    污染数值处理段    ++++++++++++++++++++++++++





#++++++++++++++++++++++++++    订正相关子函数    ++++++++++++++++++++++++++   
#+++++   make_base_data() 用于生成中间base类数据  +++++
#+++++   base_back_ground()用于生成train,forecast数据  +++++ 
#+++++   result_output()用于生成result数据  +++++ 



#++++  make the mid_data which is equal to base.txt  ++++
#++++  include the OBS  FORECAST  MM5 data   ++++
#++++  install:程序目录  ista:站点信息  model_runday:建模日期  model_time：建模时长
#++++  model_type:建模类型 model_type=0:24小时值;model_type=1:48小时值;
def make_base_data(install,ista,model_runday,model_time,model_type):
    import os
    
    ista_base=[]
    #+++  train_data  +++
    for iday in range(model_time,0,-1):
      
        date_OBS=add_day(int(model_runday[:4]),int(model_runday[4:6]),int(model_runday[6:]),1-1*iday)
        date_FOR=add_day(int(model_runday[:4]),int(model_runday[4:6]),int(model_runday[6:]),-1*iday-model_type)
        #print date_OBS,date_FOR
        date_OBS_char='%04d%02d%02d'%tuple(date_OBS)
        date_FOR_char='%04d%02d%02d'%tuple(date_FOR)
        date_MM5_char='%04d%02d%02d'%tuple(date_FOR)
        file_exist_flag=0
        if os.path.exists( install+r'/OBS/%8s/OBS_%3s_%8s.txt'%(date_OBS_char,ista[1],date_OBS_char) )          : file_exist_flag=file_exist_flag+1
        if os.path.exists( install+r'/FORECAST/%8s/FORECAST_%3s_%8s.txt'%(date_FOR_char,ista[1],date_FOR_char) ): file_exist_flag=file_exist_flag+1
        if os.path.exists( install+r'/MM5/%8s/result_%04d_%8s_total.txt'%(date_MM5_char,ista[0],date_MM5_char) ): file_exist_flag=file_exist_flag+1     

        if file_exist_flag==3:
            OBS_data={}
            file_OBS=open(install+r'/OBS/%8s/OBS_%3s_%8s.txt'%(date_OBS_char,ista[1],date_OBS_char),'r')
            file_OBS.readline()
            for line in file_OBS.readlines():
                mid=line.split()
                date_OBS_perhour='%04d%02d%02d%02d'%(int(mid[0]),int(mid[1]),int(mid[2]),int(mid[3]))
                (AQI_OBS,PRIC)=caculate_aqi([float(mid[4]),float(mid[5]),float(mid[6]),float(mid[7]),float(mid[8]),float(mid[9])])
                OBS_data[date_OBS_perhour]=[AQI_OBS,float(mid[4]),float(mid[5]),float(mid[6]),float(mid[7]),float(mid[8]),float(mid[9])]
            file_OBS.close()      

            FOR_data={}
            file_FOR=open(install+r'/FORECAST/%8s/FORECAST_%3s_%8s.txt'%(date_FOR_char,ista[1],date_FOR_char),'r')
            file_FOR.readline()
            for line in file_FOR.readlines():
                mid=line.split()
                date_FOR_perhour='%04d%02d%02d%02d'%(int(mid[0]),int(mid[1]),int(mid[2]),int(mid[3]))
                (AQI_FOR,PRIC)=caculate_aqi([float(mid[4]),float(mid[5]),float(mid[6]),float(mid[7]),float(mid[8]),float(mid[9])])
                FOR_data[date_FOR_perhour]=[AQI_FOR,float(mid[4]),float(mid[5]),float(mid[6]),float(mid[7]),float(mid[8]),float(mid[9])]
            file_FOR.close()

            MM5_data={}
            file_MM5=open(install+r'/MM5/%8s/result_%04d_%8s_total.txt'%(date_MM5_char,ista[0],date_MM5_char),'r')
            file_MM5.readline()
            for line in file_MM5.readlines():
                mid=line.split(',')
                date_MM5_perhour='%04d%02d%02d%02d'%(int(mid[0]),int(mid[1]),int(mid[2]),int(mid[3]))
                MM5_data[date_MM5_perhour]=[float(mid[4]),float(mid[5]),float(mid[6]),float(mid[7]),float(mid[8]),float(mid[9]),float(mid[10]),float(mid[11]),float(mid[12])]
            file_MM5.close()

            for ihour in range(24):
                mid_perdata=[date_OBS[0],date_OBS[1],date_OBS[2],ihour]
                time_judge=date_OBS_char+'%02d'%(ihour)
                mid_perdata.extend( OBS_data.get(time_judge,[9999,9999,9999,9999,9999,9999,9999]) )
                mid_perdata.extend( FOR_data.get(time_judge,[9999,9999,9999,9999,9999,9999,9999]) )                
                mid_perdata.extend( MM5_data.get(time_judge,[9999,9999,9999,9999,9999,9999,9999]) )
                ista_base.append(mid_perdata)
    #+++  train_data  +++

    #+++  forecast_data  +++
    date_OBS=add_day(int(model_runday[:4]),int(model_runday[4:6]),int(model_runday[6:]),1+model_type)
    date_FOR=add_day(int(model_runday[:4]),int(model_runday[4:6]),int(model_runday[6:]),0)
    #print date_OBS,date_FOR
    date_OBS_char='%04d%02d%02d'%tuple(date_OBS)
    date_FOR_char='%04d%02d%02d'%tuple(date_FOR)
    date_MM5_char='%04d%02d%02d'%tuple(date_FOR)
    file_exist_flag=0
    if os.path.exists( install+r'/FORECAST/%8s/FORECAST_%3s_%8s.txt'%(date_FOR_char,ista[1],date_FOR_char) ): file_exist_flag=file_exist_flag+1
    if os.path.exists( install+r'/MM5/%8s/result_%04d_%8s_total.txt'%(date_MM5_char,ista[0],date_MM5_char) ): file_exist_flag=file_exist_flag+1     

    if file_exist_flag==2:     
        FOR_data={}
        file_FOR=open(install+r'/FORECAST/%8s/FORECAST_%3s_%8s.txt'%(date_FOR_char,ista[1],date_FOR_char),'r')
        file_FOR.readline()
        for line in file_FOR.readlines():
            mid=line.split()
            date_FOR_perhour='%04d%02d%02d%02d'%(int(mid[0]),int(mid[1]),int(mid[2]),int(mid[3]))
            (AQI_FOR,PRIC)=caculate_aqi([float(mid[4]),float(mid[5]),float(mid[6]),float(mid[7]),float(mid[8]),float(mid[9])])
            FOR_data[date_FOR_perhour]=[AQI_FOR,float(mid[4]),float(mid[5]),float(mid[6]),float(mid[7]),float(mid[8]),float(mid[9])]
        file_FOR.close()

        MM5_data={}
        file_MM5=open(install+r'/MM5/%8s/result_%04d_%8s_total.txt'%(date_MM5_char,ista[0],date_MM5_char),'r')
        file_MM5.readline()
        for line in file_MM5.readlines():
            mid=line.split(',')
            date_MM5_perhour='%04d%02d%02d%02d'%(int(mid[0]),int(mid[1]),int(mid[2]),int(mid[3]))
            MM5_data[date_MM5_perhour]=[float(mid[4]),float(mid[5]),float(mid[6]),float(mid[7]),float(mid[8]),float(mid[9]),float(mid[10]),float(mid[11]),float(mid[12])]
        file_MM5.close()

        for ihour in range(24):
            mid_perdata=[date_OBS[0],date_OBS[1],date_OBS[2],ihour,9999,9999,9999,9999,9999,9999,9999]
            time_judge=date_OBS_char+'%02d'%(ihour)
            mid_perdata.extend( FOR_data.get(time_judge,[9999,9999,9999,9999,9999,9999,9999]) )                
            mid_perdata.extend( MM5_data.get(time_judge,[9999,9999,9999,9999,9999,9999,9999]) )
            ista_base.append(mid_perdata)
    #+++  forecast_data  +++
    return ista_base



#++++  make the train and forecast which based on base  ++++
#++++  include the train forecast   ++++
#++++  ista_base_24hour:建模数据  back_ground：背景场  pollute污染种类
#++++  model_type:建模类型 model_type=0:24小时值;model_type=1:48小时值;
#++++  txt_type:输出文件类型 txt_type=0:train; txt_type=1:forecast;
def base_back_ground(install,ista_base,back_ground,pollute,model_runday,model_type,txt_type):

    back_ground_individual=[]
    for perdata in back_ground[:-1]: back_ground_individual.append(perdata.strip()[model_type])
    
    date_today=[ int(model_runday[:4]),int(model_runday[4:6]),int(model_runday[6:8]) ]
    base_distinguish=-1
    for i in range(1,len(ista_base)):
        if ista_base[i-1][:3]==date_today and ista_base[i][:3]!=date_today:base_distinguish=i
    
    if base_distinguish!=-1:
        if txt_type==0:
            #+++  生成data_train  +++
            ista_base_pertf=[]
            for line in ista_base[:base_distinguish]:
                mid=['%04d%02d%02d%02d'%tuple(line[:4]),line[4+pollute],line[11+pollute]]
                for i in range(11,len(line)):
                    if i!=11+pollute and back_ground_individual[i-11]=='1':mid.append(line[i])
                lose_flag=0
                for perdata in mid[1:]:
                    if perdata>5000:lose_flag=lose_flag+1 
                if lose_flag==0:ista_base_pertf.append(mid)

            if len(ista_base_pertf)>24 and len(ista_base_pertf[0])>2:
                file_train=open(install+r'\bin\train.txt','w')
                file_train.write( '%6d   %4d\n'%(len(ista_base_pertf),len(ista_base_pertf[0])-2) )
                for perline in ista_base_pertf:
                    mid='%10s '%(perline[0])
                    for perdata in perline[1:]:
                        mid=mid+'%12.3f '%(perdata)
                    mid=mid+'\n'
                    file_train.write(mid)   
                file_train.close()
            #+++  生成data_train  +++                    
        else:
            #+++  生成data_forecast  +++
            ista_base_pertf=[]
            for line in ista_base[base_distinguish:]:
                mid=['%04d%02d%02d%02d'%tuple(line[:4]),line[4+pollute],line[11+pollute]]
                for i in range(11,len(line)):
                    if i!=11+pollute and back_ground_individual[i-11]=='1':mid.append(line[i])
                lose_flag=0
                for perdata in mid[2:]:
                    if perdata>5000:lose_flag=lose_flag+1 
                if lose_flag==0:ista_base_pertf.append(mid)

            if len(ista_base_pertf)>12 and len(ista_base_pertf[0])>2:
                file_forecast=open(install+r'\bin\forecast.txt','w')
                file_forecast.write( '%6d   %4d\n'%(len(ista_base_pertf),len(ista_base_pertf[0])-2) )
                for perline in ista_base_pertf:
                    mid='%10s '%(perline[0])
                    for perdata in perline[1:]:
                        mid=mid+'%12.3f '%(perdata)
                    mid=mid+'\n'
                    file_forecast.write(mid)   
                file_forecast.close() 
            #+++  生成data_forecast  +++



#++++  make the result which based on correct_result  ++++
#++++  include the correct data for 48 hour  ++++
#++++  correct_result:订正结果 如果数据缺失就用FORECAST补充
def result_output(install,ista,model_runday,correct_result):
    import os
    exist_flag=0
    
    if os.path.exists(install+r'/FORECAST/%8s/FORECAST_%3s_%8s.txt'%(model_runday,ista[1],model_runday)):
        FOR_data={}
        file_FOR=open(install+r'/FORECAST/%8s/FORECAST_%3s_%8s.txt'%(model_runday,ista[1],model_runday),'r')
        file_FOR.readline()
        for line in file_FOR.readlines():
            mid=line.split()
            date_FOR_perhour='%04d%02d%02d%02d'%(int(mid[0]),int(mid[1]),int(mid[2]),int(mid[3]))
            (AQI_FOR,PRIC)=caculate_aqi([float(mid[4]),float(mid[5]),float(mid[6]),float(mid[7]),float(mid[8]),float(mid[9])])
            FOR_data[date_FOR_perhour]=[AQI_FOR,float(mid[4]),float(mid[5]),float(mid[6]),float(mid[7]),float(mid[8]),float(mid[9])]
        file_FOR.close()

        result_data=[]   
        for iday in range(2):
            date_for=add_day(int(model_runday[:4]),int(model_runday[4:6]),int(model_runday[6:]),iday+1)
            for ihour in range(24):
                date_COR_perhour=[date_for[0],date_for[1],date_for[2],ihour]
                mid_perdata=[]                
                mid_perdata.extend( date_COR_perhour )
                mid_perdata.extend( FOR_data.get('%04d%02d%02d%02d'%tuple(date_COR_perhour),[9999,9999,9999,9999,9999,9999,9999]) )          
                for perdata in correct_result:
                    if  perdata[:4]==date_COR_perhour:
                        mid_perdata[4+perdata[4]]=perdata[5]
                        exist_flag=exist_flag+1 
                result_data.append(mid_perdata)
               
        file_result=open(install+r'\RESULT\%8s\CORRECT_%3s_%8s.txt'%(model_runday,ista[1],model_runday),'w')
        file_result.write('年 月 日 时 AQI SO2 NO2 PM10 PM25 CO O3\n')
        for line in result_data:
            mid='%4d,%3d,%3d,%3d,%8.1f,%10.1f,%10.1f,%10.1f,%10.1f,%10.3f,%10.1f\n'%tuple(line)
            file_result.write(mid)
        file_result.close()
    return exist_flag    



    
#++++++++++++++++++++++++++    订正相关子函数    ++++++++++++++++++++++++++


