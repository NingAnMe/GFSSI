#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/12/16 10:09
# @Author  : NingAnMe <ninganme@qq.com>
import re
import os
from math import ceil
import random
import pandas
import requests
from shutil import copyfile

from config import CIMISS_IP, CIMISS_USER, CIMISS_PASSWORD, DEBUG, DATA_OBS_DIR
from lib.lib_constant import STATION_LIST

API = f"http://{CIMISS_IP}/cimiss-web/api"


def copy_cimiss(date2):

    list1 = ['20171009', '20171010', '20171011', '20171012', '20171013',
             '20171014', '20171015']

    date1 = random.choice(list1)
    src = os.path.join(DATA_OBS_DIR, date1)
    dst = os.path.join(DATA_OBS_DIR, date2)
    files = os.listdir(src)
    for f in files:
        f1 = os.path.join(src, f)
        f2 = os.path.join(dst, f.replace(date1, date2))
        copyfile(f1, f2)


def download_cimiss_ssi_ssh(ymdhms_start, ymdhms_end, stations):

    interface_id = "getRadiEleByTimeRangeAndStaID"
    data_code = "RADI_CHN_MUL_HOR"
    elements = "Station_Id_d,datetime,V14311,SSH"
    order_by = "Station_ID_C:ASC,datetime:ASC"

    data_format = "json"
    time_range = f"[{ymdhms_start},{ymdhms_end}]"
    station_id = f"{','.join(stations)}"

    url = f'{API}?\
userId={CIMISS_USER}\
&pwd={CIMISS_PASSWORD}\
&interfaceId={interface_id}\
&dataCode={data_code}\
&elements={elements}\
&timeRange={time_range}\
&staIds={station_id}'

    if order_by is not None:
        url += f"&orderby={order_by}"
    if data_format is not None:
        url += f"&dataFormat={data_format}"

    response = requests.get(url, timeout=20)
    if DEBUG:
        print(url)
        print(response.content)
    if response.status_code != 200:
        print(response.content)
        return
    else:
        return response.json().get("DS")


def download_cimiss_tem(ymdhms_start, ymdhms_end, stations):
    interface_id = "getSurfEleByTimeRangeAndStaID"
    data_code = "SURF_CHN_MUL_HOR"
    elements = "Station_Id_C,datetime,TEM"
    order_by = "Station_ID_C:ASC,datetime:ASC"

    data_format = "json"
    time_range = f"[{ymdhms_start},{ymdhms_end}]"
    station_id = f"{','.join(stations)}"

    url = f'{API}?\
userId={CIMISS_USER}\
&pwd={CIMISS_PASSWORD}\
&interfaceId={interface_id}\
&dataCode={data_code}\
&elements={elements}\
&timeRange={time_range}\
&staIds={station_id}'

    if order_by is not None:
        url += f"&orderby={order_by}"
    if data_format is not None:
        url += f"&dataFormat={data_format}"

    response = requests.get(url, timeout=20)
    if DEBUG:
        print(url)
        print(response.content)
    if response.status_code != 200:
        print(response.content)
        return
    else:
        return response.json().get("DS")


def format_cimiss(ymdhms, data_ssi_ssh, data_tem, out_dir):
    data_format = {}

    for data in data_tem:
        station = data["Station_Id_C"]
        if station not in data_format:
            data_format[station] = {}
        data_station = data_format.get(station)
        if data["datetime"] not in data_station:
            data_station[data["datetime"]] = {}
        data_moment = data_station[data["datetime"]]

        data_moment["TEM"] = float(data["TEM"])
        data_moment["SSH"] = 0
        data_moment["SSI"] = 9999.00

    for data in data_ssi_ssh:
        station = data["Station_Id_d"]
        if station not in data_format:
            data_format[station] = {}
        data_station = data_format.get(station)

        if data["datetime"] not in data_station:
            data_station[data["datetime"]] = {}

        data_moment = data_station[data["datetime"]]
        ssi = float(data["V14311"])
        ssh = float(data["SSH"])
        data_moment["SSI"] = ssi if ssi != 0 else 9999.00
        data_moment["SSH"] = ssh if ssh != 999999 else 0
        if "TEM" not in data_moment:
            data_moment["TEM"] = 0

    ymd = ymdhms[:8]
    y = int(ymdhms[0:4])
    m = int(ymdhms[4:6])
    d = int(ymdhms[6:8])
    for k1, v1 in data_format.items():
        if bool(re.search('[a-zA-Z]', k1)):
            return
        out_file = os.path.join(out_dir, f"ObsData_{k1}_{ymd}.txt")
        try:
            with open(out_file, 'w') as f:
                for k2, v2 in v1.items():
                    line = f"{y}, {m:2d}, {d:2d}, {int(k2[8:10]):2d}, {v2['SSI']}, {v2['SSH']}, {v2['TEM']}\n"
                    f.write(line)
        except KeyError:
            if os.path.isfile(out_file):
                os.remove(out_file)
        if DEBUG:
            print(out_file)


def get_cimiss_ssi_ssh_tem_data(ymd, out_dir, copy_file=False):

    df = pandas.read_csv(
        STATION_LIST, sep=',', index_col=False,
        names=["station", "longitude", "latitude"])
    stations = list(df.loc[:, "station"])
    # 拷贝样板文件
    if copy_file:
        copy_cimiss(ymd)

    ymdhms_start = ymd + "000000"
    ymdhms_end = ymd + "230000"

    for i in range(ceil(len(stations) / 500)):
        stations_ = stations[500*i:500*(i+1)]
        data_ssi_ssh = download_cimiss_ssi_ssh(ymdhms_start, ymdhms_end, stations_)
        data_tem = download_cimiss_tem(ymdhms_start, ymdhms_end, stations_)
        if data_ssi_ssh is not None and data_tem is not None:
            format_cimiss(ymdhms_start, data_ssi_ssh, data_tem, out_dir)
        import time
        time.sleep(1)
    return True


if __name__ == '__main__':

    from lib_path import GFSSI_DIR

    test_dir = os.path.join(GFSSI_DIR, 'test')
    if not os.path.isdir(test_dir):
        os.makedirs(test_dir)

    get_cimiss_ssi_ssh_tem_data("20191214", test_dir)
