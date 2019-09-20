import os
import sys
import numpy as np
import h5py

from lib.lib_constant import FY4A_1KM_CORRECT_LAT_LON_RANGE
from lib.lib_constant import LON_LAT_LUT_FY4_1KM
from lib.lib_database import *

from gfssi_b02_ssi_1km import _write_out_file


def get_fy4a_1km_correct_txt_lat_lon(in_file):
    if not os.path.isfile(in_file):
        raise FileExistsError(':{}'.format(in_file))
    datas = np.loadtxt(in_file, skiprows=1)
    data = {}
    indexs = {
        'Latitude': 0,
        'Longitude': 1,
        'SSI': 5,
        'DirSSI': 6,
        'DifSSI': 7,
    }
    for name, index in indexs.items():
        data[name] = datas[:, index]
    return data


def fy4a_1km_correct_txt2hdf(in_file, out_file, resultid, planid, datatime, resolution_type):
    print('INPUT <<<：{}'.format(LON_LAT_LUT_FY4_1KM))
    print('INPUT <<<：{}'.format(in_file))
    area_type = 'Full_DISK'
    if os.path.isfile(out_file):
        print('数据已经存在: {}'.format(out_file))
        if not exist_result_data(resultid=resultid, datatime=datatime,
                                 resolution_type=resolution_type,
                                 area_type=area_type):
            add_result_data(resultid=resultid, planid=planid, address=out_file, datatime=datatime,
                            resolution_type=resolution_type, area_type=area_type, element=None)
        return

    if not os.path.isfile(LON_LAT_LUT_FY4_1KM):
        raise FileExistsError('文件不存在：{}'.format(LON_LAT_LUT_FY4_1KM))

    # [9.995, 55.01, 69.995, 135.01, 0.01]
    rminlat, _, rminlon, _, res = FY4A_1KM_CORRECT_LAT_LON_RANGE

    print('min lat: {}  =====  min lon:{}  =====  res:{}'.format(rminlat, rminlon, res))

    with h5py.File(LON_LAT_LUT_FY4_1KM) as hdf:
        shape = hdf.get('Latitude')[:].shape
    print('shape:{}'.format(shape))

    datas = get_fy4a_1km_correct_txt_lat_lon(in_file)
    lats = datas.pop('Latitude')
    lons = datas.pop('Longitude')

    ii = ((lats - rminlat) / res).astype(np.int)
    jj = ((lons - rminlon) / res).astype(np.int)

    result = {}

    for key, data in datas.items():
        value = np.full(shape, np.nan)
        data = np.squeeze(data)
        value[ii, jj] = data
        result[key] = value
    _write_out_file(out_file, result)
    if os.path.isfile(out_file):
        if not exist_result_data(resultid=resultid, datatime=datatime,
                                 resolution_type=resolution_type,
                                 area_type=area_type):
            add_result_data(resultid=resultid, planid=planid, address=out_file, datatime=datatime,
                            resolution_type=resolution_type, area_type=area_type, element=None)


# if __name__ == '__main__':
#     test_in_file = '/home/gfssi/Project/OM/gfssi/step4/RetData/20171015/201710150900_varify_finally.txt'
#     test_out_file = '/home/gfssi/Project/OM/gfssi/step4/RetData/20171015/201710150900_varify_finally.hdf'
#     fy4a_1km_correct_txt2hdf(test_in_file, test_out_file)
