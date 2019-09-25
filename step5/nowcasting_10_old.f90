program  main
implicit none        
integer,parameter ::nn=21   !!!here nn=nd+n=16+5.we read only 5 obs data ,and
                            !!! forecast 16times,every time is 15minues.
                            !!! and we will use future 16times 's time and gono 
                            !!! so we need to first compute the future time and
                            !!!gono
integer, parameter :: mm=5, mn=4
integer nd,n,i,mm1,mm2,is,n1,k,j,kk,im

integer a00(mm-1),ix(1),iday(12)
real r_data(nn),r_data_sta(nn),r_data_smarts(nn)
real work_smarts(nn),work_sta(nn)
real y(nn),pmgf(nn,mm-1),x(nn,mm-1),aa(mm-1),a0(mm-1),a(mn+1), r, f(mn,nn) !wind7Ϊ��ά���飬���һ���µķ������ݣ�15����һ�Σ���!aΪ�ع�ϵ����rΪ�����ϵ��
real wind0(nn),windy(nn),work(nn)

real q,s,u, b(mn+1,mn+1), v(mn),gl,gono,w(2)
integer locs,locd,year,month,day,hour,minu
character*12 tim
character*300 file_in_sta,file_out
logical alive
integer hour2,minu2


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!       
data iday/31,28,31,30,31,30,31,31,30,31,30,31/
nd=16   !forecast 16 times,every time is 15minutes,so 16times is 4hours.we
        !forecast 4hours 
n=5     !5 obs .we use past of 5 obs data ,to forecast 4hours.


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!following we read the input file,and get the newest 5 obs data .
!!!! and we also compute the future 16times's time and gono.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
file_in_sta='interp_out.txt'
open(12,file=file_in_sta)
     do i=1,n
         read(12,*) tim,r_data_sta(i)
         read(tim(1:4),'(i4)') year
         read(tim(5:6),'(i2)') month
         read(tim(7:8),'(i2)') day
         read(tim(9:10),'(i2)') hour
         read(tim(11:12),'(i2)') minu   
         call cal_sun_angle(gono,year,month,day,hour,minu,116.4665,39.7736)
!!!!here we use the point lat,lon.if we use other point,need edit
         r_data_smarts(i)=gono
     enddo
     mm1=hour*60+minu
     do i=n+1,n+nd
       mm2=mm1+(i-n)*15
       hour2=mm2/60
       minu2=mod(mm2,60)
       call cal_sun_angle(gono,year,month,day,hour2,minu2,116.4665,39.7736)
!!!here we use the point lat,lon.if we use other point,need edit
       r_data_smarts(i)=gono
       read(12,*) tim,r_data_sta(i)
     enddo
close(12)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!     
     
     
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!follow  we get the locs and locd,in the n=5 obs data .
!!! if this 5 obs data is ok,we will use the short-term forecast,MMGF method
!!! if this 5 obs data is not all ok,maybe only 4 obs data is ok,we will 
!!! for forecast use gono*0.7 directly,not use MMGF method 
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!     
do i=2,n
   if(r_data_sta(i-1)==9999.0 .and. r_data_sta(i)<1600)then
   locs=i
   endif
   if(r_data_sta(i)==9999.0 .and. r_data_sta(i-1)<1600)then
   locd=i-1
   endif
enddo

if(r_data_sta(1)<1600)then
   locs=1
endif
if(r_data_sta(n)<1600)then
  locd=n
endif

print*, locs, locd,'locs,locd'
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!following we first open the forecast_test.txt
!!!! and judge the locd-locs+1==n ,if yes,use MMGF,method,if no,use gono*0.7
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
file_out='forecast_test.txt'
open(21,file=file_out)
write(21,'(a)') '    in_situ       MMGF  '


if(locd-locs+1==n)then
   n1=n+nd
   work_smarts(1:n1)=r_data_smarts(locd-n+1:locd-n+n1)
   work_sta(1:n)=r_data_sta(locd-n+1:locd)
  do k=1,n
   r_data(k)=0.0  !���ָ��
  if(work_smarts(k).ne.0)then
     r_data(k)=work_sta(k)/work_smarts(k)
  endif
  if(r_data(k).lt.0.0)then
     r_data(k)=0.0
  endif
  enddo

  wind0(1:n)=r_data(1:n)  !δ����һ�ײ��
  work(1:n)=wind0(1:n)
  if(wind0(n).eq.0)then
     work(n+1:n1)=0.0
  else
!��ĳ96*2��ʱ�ε����м��������������չ���󣬾��󳤶�Ϊn1����������pmgf(n1,mm-1)������
     call MMGF(n,n1,mm,wind0(1:n),pmgf(1:n1,1:mm-1))


   do i=1,n
      do j=1,mm-1
         x(i,j)=pmgf(i,j)
      enddo
   enddo

   do i=1,n
      y(i)=wind0(i)
   enddo

!���û�ɫ�����ȼ��㷽����Ԥ����wind��Ԥ������pmgf�Ĺ�����aa���������С��Ԥ������pmgf�Ĵ�Сһ�£���Ϊmm-1
   call gra(x(1:n,1:mm-1),y(n),aa,mm-1,n)


!�������Ⱦ���aa�Ӵ�С���еõ�a0������¼����λ��a00
   do i=1,mm-1
      ix=maxloc(aa)
      a0(i)=aa(ix(1))
      a00(i)=ix(1)
      aa(ix(1))=-999.99
   enddo


!!!!! ������������mn����չ�������д����f(mn,n1)�С�
   do j=1, mn
     k=a00(j)
     do kk=1,n1
       f(j,kk)=pmgf(kk,k)
     enddo
   enddo


!!!��Ԫ���Իع飬�ع�ϵ�������a(mn+1)��

   call isqt2(f(1:mn,1:n1),wind0(1:n),mn,mn+1,n,a,q,s,r,v,u,b)

   do i=1, n1
     windy(i)=a(1)
     do j=1,mn
       windy(i)=windy(i)+a(j+1)*f(j,i)
     enddo
   enddo


!out
        do im=1,n1
	   work(im)=windy(im)
	enddo
  endif
!!����ͳ�����ʱ�Σ�1��n1-16����ͳ���������۲��ߵ����b(1)����NWP��۲��ߵ����(b2)


!�����������Ԥ����������ļ�21�С�ʵ����Ԥ������
    
    do k=6,21
    write(21,'(2f12.3)')r_data_sta(k), work(k)*work_smarts(k)
    enddo    
    close(21)
else
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!following is the valid data is < n=5 ,so we use gono*0.7 directly
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    print*,'hahaha'
    do i=1,nd
       write(21,'(2f12.3)')r_data_sta(5+i),r_data_smarts(n+i)*0.7
    enddo
    close(21)
endif

end program

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!subroutine MMGF ���������ӳ���,n1Ϊ������չ�����ĳ��ȣ�nΪԭ���еĳ���
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
subroutine MMGF(N,n1,mm,x,PMGF)
real sb(n),x(n),pmgf(n1,mm-1)


 do kk=2,mm
   do j=1,kk
     sb(j)=0.0
   enddo
    do j=1,kk
	  I=0
	  do l=j,n,kk
	   sb(j)=sb(j)+x(l)
	    I=I+1
	  enddo
	   sb(j)=sb(j)/float(I)
	enddo
	do l=1,n1
	  j=l-l/kk*kk
	  if(j.eq.0) j=kk
	  kkk=kk-1
	  pmgf(l,kkk)=sb(j)
	enddo
 enddo
return
end   

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!subroutine gra(x,y,aa,m,nl)�����ɫ�����Ⱥ���
!xΪ�������У�yΪԤ�������У�aaΪ��ɫ�����ȣ������С�����Ӹ�����ͬ
!!!���������н��б�׼������
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
subroutine gra(x,y,aa,m,nl)

real y(nl),x(nl,m),aa(m),w1(nl),wk2(m,nl),wk3(m),wk4(m),xs(nl)
real wk_min,wk_max

do i=1,m
   do j=1,nl
     w1(j)=x(j,i)
   enddo
   call standard(w1,xs,nl)
   do j=1,nl
     x(j,i)=xs(j)
	enddo
enddo
call standard(y,xs,nl)
  do j=1,nl
     y(j)=xs(j)
  enddo

!--------------------------------------
!!!�����ɫ������
!--------------------------------------
do i=1,m
    do j=1,nl
	 wk2(i,j)=abs(y(j)-x(j,i))
	enddo
enddo


do i=1,m

  wk3(i)=minval(wk2(i,:))
  wk4(i)=maxval(wk2(i,:))
enddo
 wk_min=minval(wk3)   
 wk_max=maxval(wk4)  

do i=1,m
   do j=1,nl
   wk2(i,j)=(wk_min+0.5*wk_max)/(wk2(i,j)+0.5*wk_max)
   enddo
enddo


do i=1,m
   aa(i)=sum(wk2(i,:))/float(nl)
enddo

	RETURN
	END


!!!!!!!!!!!!!!!!!!!!!!
!!!!!��׼������!x ԭʼ���У�xsΪ��׼������,nlΪʱ�䳤��
!!!!!!!!!!!!!!!!!!!!!!!
subroutine standard(x,xs,nl)
real x(nl),xs(nl),x_mean,x_sx

	x_mean=sum(x)/float(nl)
	x_sx=sum((x-x_mean)**2)/float(nl)
	do n=1,nl
		xs(n)=(x(n)-x_mean)/sqrt(x_sx)
	enddo

	RETURN
	END

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!��Ԫ���Իع�subroutine
!M �Ա������� mmΪ�ع�ϵ������mm=m+1,nΪʱ�䳤�ȣ�a(mm)��һά���飬��Żع�ϵ����qsrΪƫ��ƽ���ͣ�ƽ����׼��͸����ϵ����
! v(m)Ϊm���Ա�����ƫ���ϵ�������������������������ضȣ��ø����ϵ������������ع�Ч����uΪ�ع�ƽ����,bΪ��������
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
subroutine isqt2(x,y,m,mm,n,a,q,s,r,v,u,b)

dimension x(m,n),y(n),a(mm),b(mm,mm),v(m)
real x,y,a,b,v,q,s,r,u,yy,dyy,p,pp

	B(1,1)=N
	DO J=2,MM
	  B(1,J)=0.0
	  DO I=1,N
	  B(1,J)=B(1,J)+X(J-1,I)
      enddo
	  B(J,1)=B(1,J)
    enddo
	DO I=2,MM
	  DO J=I,MM
	    B(I,J)=0.0
	    DO  K=1,N
	    B(I,J)=B(I,J)+X(I-1,K)*X(J-1,K)
        enddo
	    B(J,I)=B(I,J)
      enddo
    enddo
	A(1)=0.0
	DO I=1,N
	A(1)=A(1)+Y(I)
    enddo
	DO I=2,MM
	  A(I)=0.0
	  DO  J=1,N
	  A(I)=A(I)+X(I-1,J)*Y(J)
      enddo
    enddo

	CALL ACHOL(B,MM,1,A,L)

	YY=0.0
	DO I=1,N
	YY=YY+Y(I)/N
    enddo
	Q=0.0
	DYY=0.0
	U=0.0

	DO I=1,N
	  P=A(1)
	  DO J=1,M
      P=P+A(J+1)*X(J,I)
      enddo
	  Q=Q+(Y(I)-P)*(Y(I)-P)
	  DYY=DYY+(Y(I)-YY)*(Y(I)-YY)
	  U=U+(YY-P)*(YY-P)
    enddo


	S=SQRT(Q/N)
	if(Q/DYY.gt.1.0)then 
	R=0.0
	else
	R=SQRT(1.0-Q/DYY)
	endif

	DO J=1,M
	  P=0.0
	  DO I=1,N
	    PP=A(1)
	    DO K=1,M
	      IF (K.NE.J) PP=PP+A(K+1)*X(K,I)
        enddo
	    P=P+(Y(I)-PP)*(Y(I)-PP)
       enddo
     if((Q/P).ge.1.0)then
	  v(J)=0.0
	  else
	  V(J)=SQRT(1.0-Q/P)
	  endif
    enddo

	RETURN
	END


	SUBROUTINE ACHOL(Aa,N,M,D,L)
	real Aa(N,N),D(N,M)
	L=1
	IF (Aa(1,1)+1.0.EQ.1.0) THEN
	  L=0
	  WRITE(*,30)
	  RETURN
	END IF
	Aa(1,1)=SQRT(Aa(1,1))
	DO  J=2,N
	Aa(1,J)=Aa(1,J)/Aa(1,1)
    enddo
	DO  I=2,N
	  DO  J=2,I
	  Aa(I,I)=Aa(I,I)-Aa(J-1,I)*Aa(J-1,I)
      enddo
	  IF (Aa(I,I)+1.0.EQ.1.0) THEN
       Aa(I,I)= 0.5 !!! ����
	    L=0
	    WRITE(*,30)
	    RETURN
	  END IF
30	  FORMAT(1X,'FAIL')

    if(Aa(I,I).gt.0.0)then
	  Aa(I,I)=SQRT(Aa(I,I))   
		else  
	     Aa(I,I)= 0.5  !0.0
	  endif
	  IF (I.NE.N) THEN
	    DO  J=I+1,N
	    DO  K=2,I
	    Aa(I,J)=Aa(I,J)-Aa(K-1,I)*Aa(K-1,J)
        enddo
	    Aa(I,J)=Aa(I,J)/Aa(I,I)
        enddo
	  END IF
  
    enddo

	DO J=1,M
	  D(1,J)=D(1,J)/Aa(1,1)
	  DO  I=2,N
	    DO K=2,I
	    D(I,J)=D(I,J)-Aa(K-1,I)*D(K-1,J)
        enddo
	    D(I,J)=D(I,J)/Aa(I,I)
      enddo
    enddo
	DO J=1,M
	  D(N,J)=D(N,J)/Aa(N,N)
	  DO  K=N,2,-1
	    DO  I=K,N
	    D(K-1,J)=D(K-1,J)-Aa(K-1,I)*D(I,J)
        enddo
	    D(K-1,J)=D(K-1,J)/Aa(K-1,K-1)
      enddo
    enddo
	RETURN
	END


!----------------------------------------------------------------------
!     subroutine getida �����ڽ��п��¼���
!----------------------------------------------------------------------   
      subroutine getida(idf,ida,iv)
      dimension idf(3),ida(3),iday(12)
      data iday/31,28,31,30,31,30,31,31,30,31,30,31/

      do 10 i=1,3
      ida(i)=idf(i)
   10 continue

      nm=iday(ida(2))
      if(idf(2).eq.2) then
      if(mod(idf(1),4).eq.0.and.mod(idf(1),100).ne.0) nm=29
      if(mod(idf(1),400).eq.0) nm=29
      endif

      ida(3)=idf(3)+iv
      if(ida(3).gt.nm) then
      ida(2)=idf(2)+1
      if(ida(2).gt.12) then
      ida(1)=idf(1)+1
      ida(2)=ida(2)-12
      endif
      ida(3)=ida(3)-nm
      endif

      end 
      
      
subroutine  cal_sun_angle(gono,year,month,day,hour,minute,lon,lat) 
real   LAT,LON,CT,LC,TT,T0
real  pi,L_time,W_time,delt_N,N0,QQ,EQ,DE_shicha
real  sinHA,gono
integer year,month,day,hour,minute,jiri_N
integer F_minute,S_hour 
 pi=3.1415926
 S_hour=hour
 F_minute=minute
 L_time=lon/15.0   
 W_time=S_hour+F_minute/60.0
 delt_N=(W_time-L_time)/24.0
 N0=79.6764+0.2422*(year-1985)-int(0.25*(year-1985))
 call caljiri(jiri_N,year,month,day) 
 QQ=2*pi*57.3*(jiri_N+delt_N-N0)/365.2422
 EQ=0.0028-1.9857*sind(QQ)+9.9059*sind(2*QQ)-7.0924*cosd(QQ)-0.6882*cosd(2*QQ)!cal DE
 DE_shicha=0.3723+23.2567*sind(QQ)+0.1149*sind(2*QQ)-0.1712*sind(3*QQ)-0.7580*cosd(QQ)+0.3656*cosd(2*QQ)+0.0201*cosd(3*QQ)
 CT=S_hour+F_minute/60.0
 LC=(lon-120)*4/60.0   
 TT=CT+LC+EQ/60.0  
!cal T0
T0=(TT-12.0)*15.0   
sinHA=sind(lat)*sind(DE_shicha)+cosd(lat)*cosd(DE_shicha)*cosd(T0) 
gono=1366.1*(1+0.033*cos(360*float(jiri_N)/365.))*sinHA

end


subroutine  caljiri(jiri_N0,year0,month0,day0)
integer jiri_N0,year0,month0,day0
real   jiri_A0,jiri_B0,jiri_C0
jiri_A0=year0/4
jiri_B0=jiri_A0-floor(jiri_A0)
jiri_C0=32.8
if(month0<=2)then
jiri_C0=30.6
endif
if(jiri_B0==0 .and. month0>2)then
jiri_C0=31.8
endif
jiri_N0=floor(30.6*month0-jiri_C0+0.5)+day0-1  !here ,we define jiri_N=jiri_N-1,just mean 1/1 jiri_N=0;
end










