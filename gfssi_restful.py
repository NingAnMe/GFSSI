import pickle
from datetime import datetime
from dateutil.relativedelta import relativedelta

import os
from flask import Flask, request
from flask_restful import Resource, Api

from schedule import product_fy4a_disk_area_data, make_zip_file, get_hash_utf8, find_result_data, data_root_dir, \
    product_fy4a_disk_point_data

from lib.lib_constant import KDTREE_LUT_FY4_4KM, KDTREE_LUT_FY4_1KM
from lib.lib_forecast import forecast_ssi

print('读取查找表文件： {}'.format('*' * 10))
print(':{}'.format(KDTREE_LUT_FY4_4KM))
print(':{}'.format(KDTREE_LUT_FY4_1KM))

if not os.path.isfile(KDTREE_LUT_FY4_4KM):
    raise FileExistsError('{} is not exit'.format(KDTREE_LUT_FY4_4KM))
if not os.path.isfile(KDTREE_LUT_FY4_1KM):
    raise FileExistsError('{} is not exit'.format(KDTREE_LUT_FY4_1KM))

with open(KDTREE_LUT_FY4_4KM, 'rb') as fp:
    kdtree_idx_fy4_4km, kdtree_ck_fy4_4km = pickle.load(fp)
with open(KDTREE_LUT_FY4_1KM, 'rb') as fp:
    kdtree_idx_fy4_1km, kdtree_ck_fy4_1km = pickle.load(fp)

app = Flask(__name__)
api = Api(app)


class DownloadData(Resource):

    def post(self):
        print('DownloadData')
        requests = dict(request.form)
        print(datetime.now(), requests)
        area_type = requests.pop('area_type')

        hash_str = get_hash_utf8('{}'.format(datetime.now()))

        in_files = None
        if area_type == 'Full':
            resultid = requests['resultid']
            resolution_type = requests['resolution_type']
            date_s = datetime.strptime(requests['date_start'], '%Y%m%d%H%M%S')
            date_e = datetime.strptime(requests['date_end'], '%Y%m%d%H%M%S')
            results = find_result_data(resultid=resultid, datatime_start=date_s, datatime_end=date_e,
                                       resolution_type=resolution_type)
            if results.count() <= 0:
                in_files = None
            else:
                in_files = [row.address for row in results]

        elif area_type == 'Area':
            try:
                left_up_lon = float(requests['left_up_lon'])
                left_up_lat = float(requests['left_up_lat'])
                right_down_lon = float(requests['right_down_lon'])
                right_down_lat = float(requests['right_down_lat'])
                resultid = requests['resultid']
                resolution_type = requests['resolution_type']
                date_s = requests['date_start']
                date_e = requests['date_end']
                in_files = product_fy4a_disk_area_data(date_start=date_s, date_end=date_e, left_up_lon=left_up_lon,
                                                       left_up_lat=left_up_lat, right_down_lon=right_down_lon,
                                                       right_down_lat=right_down_lat, resultid=resultid,
                                                       resolution_type=resolution_type)
                if in_files is None or len(in_files) <= 0:
                    in_files = None
            except Exception as why:
                print('下载区域文件错误: {}'.format(why))
        elif area_type == 'Point':
            resultid = requests['resultid']
            resolution_type = requests['resolution_type']
            date_s = requests['date_start']
            date_e = requests['date_end']
            point_file = requests.get('path')
            if 'FY4' in resultid and '4KM' in resolution_type:
                print('4KM')
                idx = kdtree_idx_fy4_4km
                ck = kdtree_ck_fy4_4km
            elif 'FY4' in resultid and '1KM' in resolution_type:
                print('1KM')
                idx = kdtree_idx_fy4_1km
                ck = kdtree_ck_fy4_1km
            else:
                return {'error': '分辨率错误', 'code': 0}, 200

            if point_file is not None:
                in_files = product_fy4a_disk_point_data(date_start=date_s, date_end=date_e, point_file=point_file,
                                                        resolution_type=resolution_type, resultid=resultid,
                                                        idx=idx, ck=ck)
            else:
                lon = float(requests['left_up_lon'])
                lat = float(requests['left_up_lat'])
                txt = product_fy4a_disk_point_data(date_start=date_s, date_end=date_e, lon=lon, lat=lat,
                                                   resolution_type=resolution_type, resultid=resultid, idx=idx, ck=ck)
                if txt is not None:
                    in_files = [txt]
                else:
                    in_files = None
        else:
            return {'error': '不支持的区域类型:{}'.format(area_type), 'code': 0}, 400

        if in_files is not None and len(in_files) >= 0:
            in_files_length = len(in_files)
            print('找到的文件总数:{}'.format(in_files_length))
            dir_out = os.path.join(data_root_dir, 'TmpData')
            out_file = os.path.join(dir_out, '{}.zip'.format(hash_str))
            zip_file = make_zip_file(out_file=out_file, in_files=in_files)
            return {'zip_file': zip_file, 'code': 1}, 201
        else:
            return {'error': '没有找到任何输入文件，未生成zip文件', 'code': 0}, 200


class GetPointData(Resource):
    def post(self):
        print('GetPointData')
        requests = dict(request.form)
        print(datetime.now(), requests)

        is_live = requests.pop('is_live')
        is_forecast = requests.pop('is_forecast')
        lon = requests['lon']
        lat = requests['lat']
        resultid = requests['resultid']
        resolution_type = requests['resolution_type']
        date_s = requests['date_start']
        date_e = requests['date_end']
        element = requests['element']

        # 只支持时次预报
        if 'Orbit' not in resultid:
            is_forecast = 'false'
        # 只支持 4KMCorrect 和 1KM 预报
        if ('4KMCorrect' not in resolution_type) and ('1KM' not in resolution_type):
            is_forecast = 'false'

        if 'FY4' in resultid and '4KM' in resolution_type:
            print('4KM')
            idx = kdtree_idx_fy4_4km
            ck = kdtree_ck_fy4_4km
        elif 'FY4' in resultid and '1KM' in resolution_type:
            print('1KM')
            idx = kdtree_idx_fy4_1km
            ck = kdtree_ck_fy4_1km
        else:
            return {'error': '分辨率错误', 'code': 0}, 200

        result = None
        if is_live.lower() == 'true':
            if is_forecast.lower() == 'true':
                date_end = datetime.strptime(date_e, '%Y%m%d%H%M%S')
                date_e = (date_end - relativedelta(hours=4)).strftime('%Y%m%d%H%M%S')

                result_live = product_fy4a_disk_point_data(date_start=date_s, date_end=date_e, lon=lon, lat=lat,
                                                           resolution_type=resolution_type, resultid=resultid,
                                                           element=element,
                                                           idx=idx, ck=ck)

                if result_live is not None:
                    result = dict()
                    result['length'] = len(result_live['date']) - 1
                    date_s = (date_end - relativedelta(hours=5)).strftime('%Y%m%d%H%M%S')
                    result_forecast = product_fy4a_disk_point_data(date_start=date_s, date_end=date_e, lon=lon, lat=lat,
                                                                   resolution_type=resolution_type, resultid=resultid,
                                                                   element=element,
                                                                   idx=idx, ck=ck)

                    if result_forecast is not None:
                        values = result_forecast.pop('values')
                        forecast_dates, forecast_values = forecast_ssi(result_forecast['date'], values, lon, lat)
                        result_live['date'].extend(forecast_dates)
                        result_live['value'].extend(forecast_values)
                        result['date'] = result_live['date']
                        result['value'] = result_live['value']
            else:
                result = product_fy4a_disk_point_data(date_start=date_s, date_end=date_e, lon=lon, lat=lat,
                                                      resolution_type=resolution_type, resultid=resultid,
                                                      element=element,
                                                      idx=idx, ck=ck)
                if result is not None:
                    result.pop('values')
                    live_length = len(result['date']) - 1
                    result['length'] = live_length
        else:
            if is_forecast.lower() == 'true':
                date_end = datetime.strptime(date_e, '%Y%m%d%H%M%S')
                date_start = date_end - relativedelta(hours=1)
                date_s = date_start.strftime('%Y%m%d%H%M%S')

                result = product_fy4a_disk_point_data(date_start=date_s, date_end=date_e, lon=lon, lat=lat,
                                                      resolution_type=resolution_type, resultid=resultid,
                                                      element=element,
                                                      idx=idx, ck=ck)
                if result is not None:
                    values = result.pop('values')
                    forecast_dates, forecast_values = forecast_ssi(result['date'], values, lon, lat)
                    result['date'] = forecast_dates
                    result['value'] = forecast_values
                    result['length'] = 0
            else:
                print('不支持的类型：is_live 和 is_forecast 不能同时为FALSE')
                result = None
        print(result)
        if result is not None:
            result['code'] = 1

            return result, 201
        else:
            return {'error': '没有找到任何输入数据', 'code': 0}, 200


api.add_resource(DownloadData, '/download')
api.add_resource(GetPointData, '/get_point_data')

if __name__ == '__main__':
    # host = '222.128.59.164'
    post = 5000
    # host = '0.0.0.0'
    # app.run(debug=True, host=host, port=5000)
    app.run(debug=True, port=5000)
