# GFSSI

step4 在Linux系统可能出现内存不足的情况，需要执行如下命令：
`ulimit -s unlimited`

step5 编译的需要gfortran-7的版本
在公司的服务器，需要在.bashrc添加`source /opt/rh/devtoolset-7/enable`

`gfortran-7 nowcasting_10.f90 -o forecast -fdec-math`