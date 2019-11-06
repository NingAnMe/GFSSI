# GFSSI 软件说明文档

### 安装GFSSI数据处理程序
1. 修改config.py里面的目录和数据库连接
2. 安装Python3
3. 安装命令`python3 install.py`

#### 安装时可能遇到的问题

##### step4 在Linux系统可能出现内存不足的情况，需要执行如下命令：

`ulimit -s unlimited`

##### step5 预报程序编译需要gfortran-7的版本

在测试服务器，需要在.bashrc添加`source /opt/rh/devtoolset-7/enable`，生产环境忽略

编译命令

`gfortran-7 nowcasting_10.f90 -o forecast -fdec-math`

### 网站功能的启动命令
`python restfull.py`

### 数据手动生产操作，命令行
查看帮助信息
`python run.py -h`

#### 每个时次需要运行的命令
FY4A：4KM原始数据入库
`python run.py -f fy4a_save_4km_orbit_data_in_database -d 20010203000000 -a 20191231000000 -s FY4A_AGRI -r 4KM -e Orbit`

FY4A：4KM原始数据绘图（1分钟）
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KM -e Orbit`

FY4A：生产4KM校正数据（输入数据为4KM原始数据）（10s）
TODO 由于订正算法程序的特殊性，没有原始数据也可以根据G0计算生成4KM校正数据，所以要考虑数据缺失的判断问题（整点数据多久未到达判断为缺失）
`python run.py -f product_fy4a_4kmcorrect_disk_full_data_orbit -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KMCorrect -e Orbit`

FY4A：4KM校正数据绘图（2分钟）
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KMCorrect -e Orbit`

FY4A：生产1KM原始数据（输入数据为4KM校正数据）（4分钟）
`python run.py -f product_fy4a_1km_disk_full_data_orbit -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KM -e Orbit`

FY4A：1KM原始数据绘图（2分30秒）
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KM -e Orbit`

FY4A：生产1KM校正数据（输入数据为1KM原始数据和CIMISS辅助数据）（1分30秒）
`python run.py -f product_fy4a_1kmcorrect_disk_full_data_orbit -d 20171015000000 -a 20171015230000 -s FY4A_AGRI -r 1KMCorrect -e Orbit`

FY4A：1KM校正数据绘图（1分15秒）
`python run.py -f product_image -d 20171015000000 -a 20171015230000 -s FY4A_AGRI -r 1KMCorrect -e Orbit`


#### 每天需要运行的命令（日数据基于时次数据合成）
FY4A：4KM原始数据合成日数据（2分30秒）
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KM -e Daily`

FY4A：4KM原始数据日数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KM -e Daily`

FY4A：4KM校正数据合成日数据
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KMCorrect -e Daily`

FY4A：4KM校正数据日数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KMCorrect -e Daily`

FY4A：1KM原始数据合成日数据
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KM -e Daily`

FY4A：1KM原始数据日数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KM -e Daily`

FY4A：1KM校正数据合成日数据
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KMCorrect -e Daily`

FY4A：1KM校正数据日数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KMCorrect -e Daily`

FY3D：1KM原始数据日数据生成
`python run.py -f product_fy3d_1km_daily_data -d 20190501000000 -a 20190501000000 -s FY3D_MERSI -r 1KM -e Daily`

FY3D：1KM原始数据日数据绘图
`python run.py -f product_fy3d_1km_daily_data -d 20190501000000 -a 20190501000000 -s FY3D_MERSI -r 1KM -e Daily`


#### 每月需要运行的命令（月数据基于日数据合成）
FY4A：4KM原始数据合成月数据（3分钟）
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KM -e Monthly`

FY4A：4KM原始数据月数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KM -e Monthly`

FY4A：4KM校正数据合成月数据
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KMCorrect -e Monthly`

FY4A：4KM校正数据月数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KMCorrect -e Monthly`

FY4A：1KM原始数据合成月数据
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KM -e Monthly`

FY4A：1KM原始数据月数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KM -e Monthly`

FY4A：1KM校正数据合成月数据
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KMCorrect -e Monthly`

FY4A：1KM校正数据月数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KMCorrect -e Monthly`

FY3D：1KM原始数据月数据生成
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY3D_MERSI -r 1KM -e Monthly`

FY3D：1KM原始数据月数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY3D_MERSI -r 1KM -e Monthly`


#### 每年需要运行的命令（年数据基于月数据合成）
FY4A：4KM原始数据合成年数据（2分钟）
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KM -e Yearly`

FY4A：4KM原始数据年数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KM -e Yearly`

FY4A：4KM校正数据合成年数据
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KMCorrect -e Yearly`

FY4A：4KM校正数据年数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 4KMCorrect -e Yearly`

FY4A：1KM原始数据合成年数据
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KM -e Yearly`

FY4A：1KM原始数据年数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KM -e Yearly`

FY4A：1KM校正数据合成年数据
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KMCorrect -e Yearly`

FY4A：1KM校正数据年数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY4A_AGRI -r 1KMCorrect -e Yearly`

FY3D：1KM原始数据年数据生成
`python run.py -f product_combine_data -d 20190501000000 -a 20190501000000 -s FY3D_MERSI -r 1KM -e Yearly`

FY3D：1KM原始数据年数据绘图
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY3D_MERSI -r 1KM -e Yearly`