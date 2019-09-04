      program cress
      parameter(nline=2000000)
	real satval(nline),satval1(nline),satval2(nline),
     &     satlat(nline),satlon(nline)
      real,allocatable :: csatval(:,:)
      integer nlat,ii,jj,is
      integer minlat,minlon,ngrid
      real rminlat,rminlon,disgrid
      character rminlat_char*10,rminlon_char*10,disgrid_char*10
      character ii_char*10,jj_char*10,input_sat*100,output_sat*100
      
      call GETARG(1,input_sat)       !插值前卫星资料路径和文件名,文本文件格式
      call GETARG(2,output_sat)      !插值后卫星资料路径和文件名,文本文件格式
      call GETARG(3,rminlat_char)    !起始点纬度*1000,例如38.9°，此处输入38900
      call GETARG(4,rminlon_char)    !起始点经度*1000,例如106.4°，此处输入106400
      call GETARG(5,disgrid_char)    !网格距*1000,例如0.04°，此处输入40
      call GETARG(6,ii_char)         !X方向格点数  
      call GETARG(7,jj_char)         !Y方向格点数
      
      read(rminlat_char,'(i10)')minlat
      read(rminlon_char,'(i10)')minlon
      read(disgrid_char,'(i10)')ngrid
      read(ii_char,'(i10)')ii
      read(jj_char,'(i10)')jj
      allocate(csatval(ii,jj))
          
      rminlat=minlat/1000.0
      rminlon=minlon/1000.0
      disgrid=ngrid/1000.0
      
      open(300,file=trim(adjustl(input_sat)))
      is=1
      DO WHILE (.TRUE.)
      READ(300,*,iostat=ierr) satlon(i),satlat(i),satval(i),
     &                        satval1(i),satval2(i)
      IF(ierr/=0) EXIT
        is=is+1
      ENDDO
      CLOSE(300)
      nlat=is-1

!!---- cressman插值
	call cressman(satval,satlat,satlon,nlat,1,rminlat,
     *            rminlon,disgrid,csatval,ii,jj)

c----- 保存卫星资料插值结果
      open(30,file=trim(adjustl(output_sat)))
	do i=1,ii
        write(30,*)(csatval(i,j),j=1,jj)
	enddo
      close(30)
      
      deallocate(csatval)
      
	stop 9999
	end

      SUBROUTINE CRESSMAN(satval,satlat,satlon,nlat,nlon,rminlat,
     *            rminlon,disgrid,csatval,ii,jj)

c~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
c satval  ------- the physical parameter on the point of satellite station
c csatval ------- the physical parameter after cressman interpose
c ia  ------- the number of the station along latitude (or south-north)
c ib  ------- the number of the station along longitude (or east-west)
c ii  ------- the number of the grib along latitude (or south-north)
c jj  ------- the number of the grib along longitude (or east-west)
c~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
c~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
c dimension arrays for satellite data
      dimension  satval(nlat,1),satlat(nlat,1),satlon(nlat,1)
c~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
c~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
c dimension arrays for satellite data after cressman interpose
      dimension  csatval(ii,jj)
c~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      dimension r1(4)
      dimension xg(ii),yg(jj)

      do i=1,ii
       xg(i)=real(rminlon)+disgrid*(i-1)
      end do
      do i=1,jj
       yg(i)=real(rminlat)+disgrid*(i-1)
      end do

******      插值半径，可根据网格距调整   *****************************
      data r1/2.0,1.0,0.5,0.1/ 
c~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
      kr1=4
c~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      esp=1.5
c      write(*,*)'interplat data-field'
c
      call ssi(xg,yg,satval,satlon,satlat,nlat,1,kr1,r1,esp,
     &         csatval,ii,jj)
      END 

C********************************************************************
      SUBROUTINE ssi(xg,yg,arry,xi,yi,ia,ib,kr1,r1,esp,
     1         aarry,ii,jj)
c
	real  cg(ii,jj),xg(ii),yg(jj),ci(ia,1),xi(ia,ib),yi(ia,ib)
	real  r1(kr1),arry(ia,ib),aarry(ii,jj)
c                                                                    
	do j=1,ib
	do i=1,ia
	 ci(i,j)=arry(i,j)
	enddo
	enddo
c	 write(*,*)'begin zhubu' 
         call ZHUBU(cg,xg,yg,ci,xi,yi,ia,ib,kr1,r1,esp,ii,jj)
c	print*,cg
c	pause
         do j=1,jj
         do i=1,ii
          aarry(i,j)=cg(i,j)
         enddo 
         enddo
c         write(*,*)'zhubu complete'
c         write(*,*)
c         write(*,'(10F10.4)')(cg(i,10),i=16,18) 
c         write(*,'(10F10.4)')(cg(10,i),i=8,10) 
c          write(*,*)'~~~~~~~~~~~~~~~~~~~~~~~'
c          write(*,*)'ssi is over !'
c          write(*,*)'~~~~~~~~~~~~~~~~~~~~~~~'
         return
         end
C********************************************************************
        SUBROUTINE ZHUBU(CG,XG,YG,CI,XI,YI,ia,ib,KM,R1,EPS,II,JJ)
c        parameter(II=41,JJ=37)
        real eps
        real CG(ii,jj),XG(II),YG(JJ),CI(ia,ib),XI(ia,ib),
     *  YI(ia,ib),DCI(ia,1),CIP(ia,1),R1(KM)

        NN=0
        K1=0
        DO 23 J=1,JJ
	  DO 23 I=1,II
        R2=0.
        CG(I,J)=0.0
37      R2=R2+100.
        DAG=0.
        WA=0.
        NH=0
        DO 38 J1=1,ib
        DO 38 I1=1,ia
        R=DIST(XG(I),YG(J),XI(I1,J1),YI(I1,J1))
C	print*,'r=  ',r,'  r2=  ',r2
czsj        IF(R.GE.R2.OR.CI(I1,J1).EQ.99.9) GOTO 38
        IF(R.GE.R2.OR.CI(I1,J1).EQ.9999.) GOTO 38
        NH=NH+1
        W=(R2**2-R**2)/(R2**2+R**2)
        WA=WA+W
        DAG=DAG+W*CI(I1,J1)
  38    CONTINUE
C	pause
	 IF(WA.LE.0.00001.OR.NH.LE.2) GOTO 37
	  CG(I,J)=CG(I,J)+DAG/WA
c   	 write(*,*) 'I=',I,'J=',J
  23    CONTINUE
  21     K1=K1+1
c	print*,'K1= ',K1
	  DO 19 J1=1,ib
	  DO 19 I1=1,ia
  19    CALL TQIP(II,JJ,XG,YG,CG,XI(I1,J1),YI(I1,J1),CIP(I1,J1))
        DO 16 I1=1,ia
        DO 16 J1=1,ib
        DCI(I1,J1)=CI(I1,J1)-CIP(I1,J1)
  16    continue
        IF(K1.GE.KM+1) GOTO 25
        DO 17 J=1,JJ
        DO 17 I=1,II
        DAG=0.
        WA=0.
        DO 18 J1=1,ib
        DO 18 I1=1,ia
        R=DIST(XG(I),YG(J),XI(I1,J1),YI(I1,J1))
        IF(R.GE.R1(K1).OR.ABS(DCI(I1,J1)).GE.EPS) GOTO 18
        W=(R1(K1)**2-R**2)/(R1(K1)**2+R**2)
        WA=WA+W
        DAG=DAG+W*DCI(I1,J1)
  18    CONTINUE
        IF(WA.LE.0.000001) DAG=0.
        IF(WA.GT.0.000001) DAG=DAG/WA
        CG(I,J)=CG(I,J)+DAG
  17    CONTINUE
        IF(K1.Lt.KM) GOTO 21
  25    CONTINUE
        RETURN
        END
C********************************************************************
        SUBROUTINE TQIP(N,M,XQ,YQ,ZQ,XP,YP,ZP)
        real XQ(N),YQ(M),ZQ(N,M),A(3),B(3)
C        *   *   *   *   *
        NM1=N-1
        DO 10 I=2,NM1
        IF(XP.LE.XQ(I)) GOTO 20
  10    CONTINUE
        I=NM1
        GOTO 30
  20    IF(I.NE.2.AND.XP-XQ(I-1).LT.XQ(I)-XP) I=I-1
C        *   *   *   *   *
  30    NM1=M-1
        DO 40 J=2,NM1
        IF(YP.LE.YQ(J)) GOTO 50
  40    CONTINUE
        J=NM1
        GOTO 60
  50    IF(J.NE.2.AND.YP-YQ(J-1).LT.YQ(J)-YP) J=J-1
C        *   *   *   *   *
  60    X1=DIST(XQ(I-1),YQ(J),XQ(1),YQ(J))
        X2=DIST(XQ(I),YQ(J),XQ(1),YQ(J))
        X3=DIST(XQ(I+1),YQ(J),XQ(1),YQ(J))
        XPP=DIST(XP,YP,XQ(1),YP)
        Y1=DIST(XQ(I),YQ(J-1),XQ(I),YQ(1))
        Y2=DIST(XQ(I),YQ(J),XQ(I),YQ(1))
        Y3=DIST(XQ(I),YQ(J+1),XQ(I),YQ(1))
        YPP=DIST(XP,YP,XP,YQ(1))
        A(1)=(XPP-X2)*(XPP-X3)/((X1-X2)*(X1-X3))
        A(2)=(XPP-X3)*(XPP-X1)/((X2-X3)*(X2-X1))
        A(3)=(XPP-X1)*(XPP-X2)/((X3-X1)*(X3-X2))
        B(1)=(YPP-Y2)*(YPP-Y3)/((Y1-Y2)*(Y1-Y3))
        B(2)=(YPP-Y3)*(YPP-Y1)/((Y2-Y3)*(Y2-Y1))
        B(3)=(YPP-Y1)*(YPP-Y2)/((Y3-Y1)*(Y3-Y2))
        I=I-2
        J=J-2
        ZP=0.
        DO 80 II=1,3
        IR=I+II
        DO 80 JJ=1,3
        JS=J+JJ
  80    ZP=ZP+A(II)*B(JJ)*ZQ(IR,JS)
        RETURN
        END
C********************************************************************
        FUNCTION DIST(LAMD1,FA1,LAMD2,FA2)
        REAL LAMD1,LAMD2
        PI=3.1415926
        DIST=2.*6370.*ASIN(SQRT(SIN((FA1-FA2)*PI/360.)*SIN((FA1-FA2)*PI
     *  /360.)+COS(FA1*PI/180.)*COS(FA2*PI/180.)*SIN((LAMD1-LAMD2)*PI/
     *  360.)*SIN((LAMD1-LAMD2)*PI/360.)))
        RETURN
        END 
