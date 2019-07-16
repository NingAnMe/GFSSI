import sys,time,arrow,os
def is_number(s):
    if s == 'nan':
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False

def judgeG0(line): #0<G0<1400
    if is_number(line[4]):
        if float(line[4])>0 and float(line[4])<1400:
            # #print('G0对:',line)#有负 或 nan 或 Itotal>G0, 
            return True

def judgeItotalG0(line):
    # print(line)
    if is_number(line[1]) and is_number(line[4]):
        if float(line[1])>float(line[4]):
            # print('*Itotal',line[1],'*G0',line[4])
            if judgeG0(line):
                return True
    return False


def otherColTrue(line):
    # print(line)
    for x in line[1:]:
        if is_number(x):
            if float(x)<0:
                return False
        elif x=='nan':
            return False
    return True

def transLine(thistime,line):
    # print(line.split()[1:],type(line.split()[1]))
    linestr = line
    line = line.split()
    if judgeItotalG0(line):#Itotal>G0，其他列也要判断不负和无nan 则除了G0之外，其它列都取32766
        if otherColTrue(line):
            # print('Itotal>G0  G0对 其他列无nan或负:',line,'\n改为',(thistime).shift(hours=8).format("YYYYMMDDHHmm")+replenishData2G0L+line[4]+replenishData2G0R+'\n','\n')
            return (thistime).shift(hours=8).format("YYYYMMDDHHmm")+replenishData2G0L+line[4]+replenishData2G0R+'\n'
    
    
    for x in line[1:]:#出现负值或nan的情况时，如果0<G0<1400，则也把G0值保留，其它列都取32766
        if is_number(x):
            if float(x)<0:
                if judgeG0(line):
                    # print('有负G0对',line,'\n改为:',(thistime).shift(hours=8).format("YYYYMMDDHHmm")+replenishData2G0L+line[4]+replenishData2G0R+'\n','\n')
                    return (thistime).shift(hours=8).format("YYYYMMDDHHmm")+replenishData2G0L+line[4]+replenishData2G0R+'\n'
                # print('有负, G0错:',line,'改为:',(thistime).shift(hours=8).format("YYYYMMDDHHmm")+replenishData2+'\n','\n')
                return (thistime).shift(hours=8).format("YYYYMMDDHHmm")+replenishData2+'\n'
        elif x=='nan':
            if judgeG0(line):
                # print('有nan, G0对:',line,'改为：',(thistime).shift(hours=8).format("YYYYMMDDHHmm")+replenishData2G0L+line[4]+replenishData2G0R+'\n')
                return (thistime).shift(hours=8).format("YYYYMMDDHHmm")+replenishData2G0L+line[4]+replenishData2G0R+'\n'
            # print('有nan, G0错:',line,'改为：',(thistime).shift(hours=8).format("YYYYMMDDHHmm")+replenishData2+'\n')
            return (thistime).shift(hours=8).format("YYYYMMDDHHmm")+replenishData2+'\n'
    return (thistime).shift(hours=8).format("YYYYMMDDHHmm")+linestr[12:]

def replenishTimeline(starttime,endtime,wfd,bflag=0):
    t1 = starttime.shift(hours=1)
    t2 = endtime.shift(hours=-1)
    timeLine = []
    ti = t1
    for i in range(len(arrow.Arrow.range('hour',t1,t2))):
        timeLine.append(ti.format("YYYYMMDDHHmm"))
        if bflag == 1:
            wfd.write(ti.format("YYYYMMDDHHmm")+replenishData1+'\n')
        else:
            wfd.write(ti.shift(hours=8).format("YYYYMMDDHHmm")+replenishData1+'\n')
        ti = ti.shift(hours=1)
    # print('=========================================\n replenishTimeline \n',timeLine)
    return timeLine

def replenishEachfile(filePath,fileName):
    wfd = open(outputpath + fileName,'w')
    cachetime = ''
    thistime = ''
    with open(filePath) as fd:
        for line in fd:
            line = line.replace("9999.0", "99999")
            if line.split()[0][10:12] != '00':
                if line.split()[0] == 'target' or line.split()[0] == 'Time':
                    wfd.write(line)
                    # print(line)
                continue
            else:
                if cachetime == '': # first line   
                    cachetime = arrow.get(str(line.split()[0]),"YYYYMMDDHHmm")
                    firsttime = arrow.get((line.split()[0][0:8] + '0000'),"YYYYMMDDHHmm").shift(hours=-1)
                    replenishTimeline(firsttime,firsttime.shift(hours=9),wfd,1)#00-07
                    if line.split()[0][8:10] != '00': # replenish begin
                        # print(firsttime,cachetime)
                        replenishTimeline(firsttime,cachetime,wfd)
                    wfd.write(transLine(cachetime,line))
                    continue

                thistime = arrow.get(str(line.split()[0]),"YYYYMMDDHHmm")
                if thistime != cachetime.shift(hours=1):
                    replenishTimeline(cachetime,thistime,wfd)

                wfd.write(transLine(thistime,line))
                cachetime = thistime
            # print(line.split()[0])
    wfd.close()

if __name__ == '__main__':
    replenishData1 = ' 32766 32766 32766 32766 32766 32766 32766 32766'
    replenishData2 = ' 32766 32766 32766 32766 32766 32766 32766 32766'
    replenishData2G0L = ' 32766 32766 32766 '
    replenishData2G0R = ' 32766 32766 32766 32766 '
    path = 'H:\\FY4\\catchDot\\FSZ\\'
    outputpath = 'H:\\FY4\\Undeal\\Dot_time\\FSZ\\'
    for root,dirs,files in os.walk(path):
        for file in files:
            start = time.time()
            filePath = root + '/' + file
            print(filePath)
            replenishEachfile(filePath,file)