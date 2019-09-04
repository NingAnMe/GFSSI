import pickle
from datetime import datetime
import os
from flask import Flask, request
from flask_restful import Resource, Api

from history import product_fy4a_disk_area_data, make_zip_file, get_hash_utf8, find_result_data, data_root_dir, \
    product_fy4a_disk_point_data

from lib.lib_constant import KDTREE_LUT_FY4_4KM, KDTREE_LUT_FY4_1KM
with open(KDTREE_LUT_FY4_4KM, 'rb') as fp:
    kdtree_idx_fy4_4km, kdtree_ck_fy4_4km = pickle.load(fp)
with open(KDTREE_LUT_FY4_1KM, 'rb') as fp:
    kdtree_idx_fy4_1km, kdtree_ck_fy4_1km = pickle.load(fp)


app = Flask(__name__)
api = Api(app)


class DownloadData(Resource):

    def post(self):
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
            lon = float(requests['left_up_lon'])
            lat = float(requests['left_up_lat'])
            resultid = requests['resultid']
            resolution_type = requests['resolution_type']
            date_s = requests['date_start']
            date_e = requests['date_end']
            txt = product_fy4a_disk_point_data(date_start=date_s, date_end=date_e, lon=lon, lat=lat,
                                               resolution_type=resolution_type, resultid=resultid)
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
        requests = dict(request.form)
        print(datetime.now(), requests)
        lon = requests['lon']
        lat = requests['lat']
        resultid = requests['resultid']
        resolution_type = requests['resolution_type']
        date_s = requests['date_start']
        date_e = requests['date_end']
        element = requests['element']
        if 'FY4' in resultid and '4KM' in resolution_type:
            idx = kdtree_idx_fy4_4km
            ck = kdtree_ck_fy4_4km
        elif 'FY4' in resultid and '1KM' in resolution_type:
            idx = kdtree_idx_fy4_1km
            ck = kdtree_ck_fy4_1km
        else:
            return {'error': '分辨率错误', 'code': 0}, 200

        result = product_fy4a_disk_point_data(date_start=date_s, date_end=date_e, lon=lon, lat=lat,
                                              resolution_type=resolution_type, resultid=resultid, element=element,
                                              idx=idx, ck=ck)
        if result is not None:
            result['code'] = 1
            return result, 201
        else:
            return {'error': '没有找到任何输入数据', 'code': 0}, 200


api.add_resource(DownloadData, '/download')
api.add_resource(GetPointData, '/get_point_data')


if __name__ == '__main__':
    # host = '222.128.59.164'
    host = '0.0.0.0'
    post = 5000
    app.run(debug=True, host=host, port=5000)
