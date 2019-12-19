## 日常维护手册

### Linux系统管理

#### 账户

##### root账户
账号：root
密码：123456

##### gfssi账户（请不要修改此账户密码，业务调度需要）
账号：gfssi
密码：gfssi

##### 修改密码
登录系统的root用户，打开“终端”：输入  passwd root 。然后输入两遍新密码。（注意！！！！一定要记住新密码。）

### 系统

#### 开机
DELL服务器有开机按钮，连接电源可直接打开。

#### 关机
登录系统的root用户，打开“终端”：输入  shutdown -h now 。

#### 重启
登录系统的root用户，打开“终端”：输入  shutdown -r now 。

### GFSSI网站系统管理

#### 后台功能

##### 启动or重新启动
登录系统的gfssi用户，打开“终端”：输入python /home/gfssi/Project/OM/gfssi/restart.py 。

##### 补缺失数据
登录系统的gfssi用户，打开“终端”：输入python /home/gfssi/Project/OM/gfssi/make_up.py -s 2019110100000 -e 20191101000000 -f Orbit。
参数说明：
-s ：后面跟的参数是开始时间YYYYmmddHHMMSS，年月日时分秒
-e ：后面跟的参数是结束时间YYYYmmddHHMMSS，年月日时分秒
-f ：后面跟的参数是数据类型：Orbit是时次，Daily是日，Monthly是月，Yearly是年

# GFSSI 软件说明文档
##### 系统版本
Red Hat Enterprise Linux Server release 7.4 (Maipo)
##### java版本
java version "1.8.0_91"
Java(TM) SE Runtime Environment (build 1.8.0_91-b14)
Java HotSpot(TM) 64-Bit Server VM (build 25.91-b14, mixed mode)
##### python版本
Python 3.7.5
[GCC 7.3.0] :: Anaconda, Inc. on linux
##### ifort 版本
15.0.1

### 安装GFSSI数据处理程序
1. 修改config.py里面的目录和数据库连接
2. 安装Python3
3. 安装命令`python3 install.py`
4. 启动程序`python3 restart.py`

#### 安装时可能遇到的问题

##### step4 在Linux系统可能出现内存不足的情况，需要执行如下命令或者将此命令放到~/.bashrc：
`ulimit -s unlimited`

### 数据手动生产操作，命令行
查看帮助信息
`python run.py -h`

#### 每个时次需要运行的命令（）
FY4A：4KM原始数据入库
`python run.py -f fy4a_save_4km_orbit_data_in_database -d 20190901000000 -a 20190901000000 -s FY4A_AGRI -r 4KM -e Orbit`

FY4A：4KM原始数据绘图（1分钟）
`python run.py -f product_image -d 20190901000000 -a 20190901000000 -s FY4A_AGRI -r 4KM -e Orbit`

FY4A：生产4KM校正数据（输入数据为4KM原始数据）（10s）
TODO 由于订正算法程序的特殊性，没有原始数据也可以根据G0计算生成4KM校正数据，所以要考虑数据缺失的判断问题（整点数据多久未到达判断为缺失）
当前方案：日合成之前，重新获取，然后缺失的数据使用订正程序生成
`python run.py -f product_fy4a_4kmcorrect_disk_full_data_orbit -d 20190901000000 -a 20190901000000 -s FY4A_AGRI -r 4KMCorrect -e Orbit`

FY4A：4KM校正数据绘图（2分钟）
`python run.py -f product_image -d 20190901000000 -a 20190901000000 -s FY4A_AGRI -r 4KMCorrect -e Orbit`

FY4A：生产1KM原始数据（输入数据为4KM校正数据）（10分钟）
`python run.py -f product_fy4a_1km_disk_full_data_orbit -d 20190901000000 -a 20190901000000 -s FY4A_AGRI -r 1KM -e Orbit`

FY4A：1KM原始数据绘图（2分30秒）
`python run.py -f product_image -d 20190901000000 -a 20190901000000 -s FY4A_AGRI -r 1KM -e Orbit`

FY4A：生产1KM校正数据（输入数据为1KM原始数据和CIMISS辅助数据）（1分30秒）
`python run.py -f product_fy4a_1kmcorrect_disk_full_data_orbit -d 20190901000000 -a 20190901000000 -s FY4A_AGRI -r 1KMCorrect -e Orbit`

FY4A：1KM校正数据绘图（1分15秒）
`python run.py -f product_image -d 20190901000000 -a 20190901000000 -s FY4A_AGRI -r 1KMCorrect -e Orbit`


#### 每天需要运行的命令（日数据基于时次数据合成）（合成前需要补数据）
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
`python run.py -f product_image -d 20190501000000 -a 20190501000000 -s FY3D_MERSI -r 1KM -e Daily`


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