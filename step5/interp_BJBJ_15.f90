program main
implicit none
character*200 fn,fn1
character*12 tim1,tim2
integer hour,minnute
real  aa,go1,go2,Itotal1,Itotal2,Itotal3
integer,parameter::itime=10880
integer  ii
integer  year1,month1,day1,hour1,minu1
integer  year2,month2,day2,hour2,minu2
character*4 syear1,syear2
character*2 smonth1,sday1,shour1,sminu1
character*2 smonth2,sday2,shour2,sminu2
character*2 s_hour3,s_minu3
integer  mm1,mm2,mmm,mmmm
integer  mm3,hour3,minu3
integer  icc
character*10 tim11,tim22 
real   kk

print*,'hello'


fn='BJBJ.txt'
fn1='result_chazhi.txt'
open(12,file=fn1)

open(11,file=fn)
read(11,*)
read(11,*)
read(11,*)tim1,Itotal1,aa,aa,go1
tim11=tim1(1:10)
 call Word_to_BJTIME(tim11,year1,month1,day1,hour1,syear1,smonth1,sday1,shour1)
read(tim1(11:12),'(i2)') minu1
mm1=60*hour1+minu1
write(12,100)syear1,smonth1,sday1,shour1,tim1(11:12) ,Itotal1
!!!!!!!!read the first obs,and get the BJtime.write the 1st bjtime obs data to
!!!!!!!!result file


do ii=1,itime   !!here do loop for all the time.2nd time mimus 1st time,there
                !!are several situation.  9999,nan,ordinary,etc
read(11,*)tim2,Itotal2,aa,aa,go2
!print*,tim2,Itotal2,aa,aa,go2
tim22=tim2(1:10)
read(tim2(11:12),'(i2)') minu2
 call Word_to_BJTIME(tim22,year2,month2,day2,hour2,syear2,smonth2,sday2,shour2)
mm2=60*hour2+minu2
!!!here get 2nd time obs data ,and get the bjtime ,and mm1,mm2 is the minute of
!!!hour+minutes ,because for the bjtime ,the YYYYMMDD is stable for the
!!!1,2time,and mm2-mm1 is the distance of the 2nd and 1st .Of course ,we have to 
!!! consider the special case ,that mm2 is next day ,and mm1 is nowday.
if(day1/=day2 .and.  hour1<24 .and. hour2>=0)then
mm2=60*(hour2+24)+minu2
print*,hour1,hour2
print*,'nndnnd',mm2,mm1,minu1,minu2
endif
!!!before consider this situation, mm2 is next day ,and mm1 is nowday


mmm=mm2-mm1
mmmm=mmm/15
print*,hour2,minu2,hour1,minu1
print*,mm2,mm1,mmm,mmmm
!!!!!!!here mmm is the difference of first time and second time
!!!!!!follow consider whether Itotal2 is nan.  some fortran have the direct
!!!function isnan,however,here isnan is not work.so I have to use 3d0,because
!!!!nan is not >=3d0,and also not <=3d0 .
 if(Itotal2.gt.3d0) then
       elseif(Itotal2.le.3d0) then
       else
       write(*,*) "Itotal must be nan",Itotal2

       if(Itotal1<1500)then
          Itotal2=go2*0.7    !!little times,in the day
       else
          Itotal2=9999.0    !!many times,not in the day,but in inght
          print*,'nndx'
       endif
endif
!!!!!!!!!!!!!!!before we get the 2nd time's Itotal2, <1500,or 9999.0.deal with
!!!!!!!!!!!!!!!the nan .

!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!after for mmmm>1 ,we have to interp mmmm-1 times data.do loop is icc
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
if(mmmm>1)then
kk=(Itotal2-Itotal1)/mmmm

do icc=1,mmmm-1
mm3=mm1+icc*15
hour3=mm3/60
minu3=mod(mm3,60)
Itotal3=Itotal1+kk*icc
if(Itotal1==9999.0 .or. Itotal2==9999.0)then
Itotal3=9999.0
endif



!print*,'chazhi time',hour3,minu3,Itotal3,tim2

if(hour3<10)then
 write(s_hour3,'(i1)')hour3
 s_hour3='0'//s_hour3
else
 write(s_hour3,'(i2)')hour3
endif


if(minu3<10)then
 write(s_minu3,'(i1)')minu3
 s_minu3='0'//s_minu3
else
 write(s_minu3,'(i2)')minu3
endif

write(12,200)syear2,smonth2,sday2,s_hour3,s_minu3,Itotal3,'chazhi'
!!!!here write the the chazhi data,not the 2nd data.you will find
!!!s_hour3,s_minu3,Itotal3,in fact ,here have some bug ,e.g. mm2 is next day and
!!!!mm1 the nowday this situation.I did not consider,because the given obs file 
!!! have not this situation.
enddo
endif

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!before for mmmm>1,follow for mmmm=1 .only this two situation.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
if(mmmm==1)then
if(Itotal2.gt.3d0) then
       elseif(Itotal2.le.3d0) then
       else
       write(*,*) "Itotal must be nan",Itotal2
      if(Itotal1<1500)then
          Itotal2=go2*0.7
       endif
endif
endif

write(12,100)syear2,smonth2,sday2,shour2,tim2(11:12),Itotal2
!!!!!!!write the 2rd data
!!!!!!!!next loop
if(mm2>=1440)then
mm2=mm2-1440
endif
year1=year2
month1=month2
day1=day2
hour1=hour2
minu1=minu2
mm1=mm2
Itotal1=Itotal2
enddo

100 format(a4,a2,a2,a2,a2,x,f10.2)
200 format(a4,a2,a2,a2,a2,x,f10.2,a10)
end


 
!!!!  subroutine  of  UTC TO BJTIME
subroutine Word_to_BJTIME(wb,b_y,b_m,b_d,b_h,s_y,s_m,s_d,s_h) 
implicit none

character*10::wb                  ! wb: world time,formate:2008010102
character*10::b2w                 ! b2w:beijing time to world time
integer::b_y,b_m,b_d,b_h          ! year, month, day, hour of world time
integer::dd,iii                   ! if w_d=0, the last day of month
character*4 s_y
character*2 s_m,s_d,s_h

read(wb(1:4),'(I4)') b_y          ! read year
read(wb(5:6),'(I2)') b_m          ! read month
read(wb(7:8),'(I2)') b_d          ! read day
read(wb(9:10),'(I2)') b_h         ! read hour

b_h=b_h+8                         ! change to beijing time for hour

if ( b_h < 24 ) then              ! change within one same day                                 

else if ( b_h >= 24 ) then        ! change between today and yesterday
       b_h=b_h-24
       call day(b_y,b_m,dd)
     if ( b_m /= 12 ) then        ! change within the same year
       if ( b_d == dd ) then     ! change between this month and last month
           b_m=b_m+1
           b_d=1
       else if ( b_d < dd ) then   ! change within one same month
           b_d=b_d+1
       endif
     else if ( b_m == 12 ) then   ! change between this year and last year
       if ( b_d == dd ) then
           b_y=b_y+1
           b_m=1
           b_d=1
       else if ( b_d < dd ) then 
                                            ! change within one same month and
                                           ! same year
           b_d=b_d+1
       endif
     endif
endif

write(b2w(1:4),'(I4)') b_y

if ( b_m >9 ) then
   write(b2w(5:6),'(I2)') b_m
else 
   write(b2w(6:6),'(I1)') b_m
endif

if ( b_d >9 ) then
   write(b2w(7:8),'(I2)') b_d
else 
   write(b2w(8:8),'(I1)') b_d
endif

if ( b_h >9 ) then
   write(b2w(9:10),'(I2)') b_h
else
   write(b2w(10:10),'(I1)') b_h
endif

!      print*, b2w

!b_y,b_m,b_d,b_h

write(s_y,'(i4)')b_y

if(b_m<10)then
 write(s_m,'(i1)')b_m
 s_m='0'//s_m
else
 write(s_m,'(i2)')b_m
endif

if(b_d<10)then
 write(s_d,'(i1)')b_d
 s_d='0'//s_d
else
 write(s_d,'(i2)')b_d
endif

if(b_h<10)then
 write(s_h,'(i1)')b_h
 s_h='0'//s_h
else
 write(s_h,'(i2)')b_h
endif


end



subroutine day(year,month,d)
implicit none

integer::year,month,d
integer::key               ! weather the year is leap year; 0=no, 1=yes

key=0

if ( (mod(year,4) == 0 .and. mod(year,100) /= 0) .or. &
   &  mod(year,400) == 0 ) then
      key=1
endif

if ( month == 2 .and. key == 1 ) then
      d=29
else if ( month == 2 .and. key == 0 ) then
      d=28
else if ( month == 1 .or. month == 3 .or.month == 5 .or.month == 7 &
     & .or.month == 8 .or.month == 10 .or.month == 12 ) then
      d=31
else
      d=30
endif

end
