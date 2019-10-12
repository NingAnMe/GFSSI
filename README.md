# GFSSI

#### step4 在Linux系统可能出现内存不足的情况，需要执行如下命令：

`ulimit -s unlimited`

#### step5 编译的需要gfortran-7的版本

在公司的服务器，需要在.bashrc添加`source /opt/rh/devtoolset-7/enable`

编译命令

`gfortran-7 nowcasting_10.f90 -o forecast -fdec-math`


# 运行命令
```shell script
# 运行FY4A原始数据（时次数据）入库 
python run.py -f fy4a_save_4km_orbit_data_in_database -d 20190101000000 -a 20190101000000 -s FY4A_AGRI -r 4KM -e Orbit

# 运行FY3D原始数据（日数据）转为HDF格式，并且入库
python run.py -f fy3d_product_daily_data_and_save_in_database -d 20190101000000 -a 20190101000000 -s FY3D_MERSI -r 1KM -e Daily

# 运行FY3D绘图（日数据）
python run.py -f fy3d_product_daily_data_and_save_in_database -d 20190101000000 -a 20190101000000 -s FY3D_MERSI -r 1KM -e Daily
```