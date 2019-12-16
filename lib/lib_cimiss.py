#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/12/16 10:09
# @Author  : NingAnMe <ninganme@qq.com>
import pandas
import requests

from config import CIMISS_IP, CIMISS_USER, CIMISS_PASSWORD

API = f"http://{CIMISS_IP}/cimiss-web/api"


def download_cimiss_ssi_ssh(ymdhms_start, ymdhms_end, stations, out_file):

    interface_id = "getRadiEleByTimeRangeAndStaID"
    data_code = "RADI_CHN_MUL_HOR"
    elements = "Station_Id_d,datetime,V14311,SSH"
    order_by = "Station_ID_C:ASC,datetime:ASC"

    data_format = "text"
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

    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        print(response.content)
        return

    content = response.content.decode('utf-8')
    with open(out_file, 'w') as f:
        f.write(content)
    print(f">>>out_file          :{out_file}")


def download_cimiss_tem(ymdhms_start, ymdhms_end, stations, out_file):
    interface_id = "getSurfEleByTimeRangeAndStaID"
    data_code = "SURF_CHN_MUL_HOR"
    elements = "Station_Id_C,datetime,TEM"
    order_by = "Station_ID_C:ASC,datetime:ASC"

    data_format = "text"
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

    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        print(response.content)
        return

    content = response.content.decode('utf-8')
    with open(out_file, 'w') as f:
        f.write(content)
    print(f">>>out_file          :{out_file}")


if __name__ == '__main__':
    from lib_constant import STATION_LIST

    df = pandas.read_csv(
        STATION_LIST, sep=',', index_col=False,
        names=["station", "longitude", "latitude"])
    stations = df.loc[:, "station"]

    ymdhms_start = "20191214000000"
    ymdhms_end = "20191214230000"

    stations = stations[:500]
    outfile = f"{ymdhms_start}_{ymdhms_end}_ssi_ssh.txt"
    download_cimiss_ssi_ssh(ymdhms_start, ymdhms_end, stations, outfile)
    outfile = f"{ymdhms_start}_{ymdhms_end}_tem.txt"
    download_cimiss_tem(ymdhms_start, ymdhms_end, stations, outfile)
