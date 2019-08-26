from datetime import datetime
import os
import json
from flask import Flask, request
from flask_restful import Resource, Api

from history import product_fy4a_disk_area_data, make_zip_file, get_hash_utf8, find_result_data, data_root_dir, \
    product_fy4a_disk_point_data

app = Flask(__name__)
api = Api(app)


class DownloadData(Resource):

    def post(self):
        requests = dict(request.form)
        area_type = requests.pop('area_type')
        print(requests)

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
                in_files = product_fy4a_disk_area_data(**requests)
                if in_files is None or len(in_files) <= 0:
                    in_files = None
                else:
                    in_files_length = len(in_files)
                    print('找到的文件总数:{}'.format(in_files_length))
            except Exception as why:
                print('下载区域文件错误: {}'.format(why))
        elif area_type == 'Point':
            lon = requests['left_up_lon']
            lat = requests['left_up_lat']
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
        print(requests)
        lon = requests.get('lon')
        lat = requests.get('lat')
        date_start = requests.get('date_start')
        date_end = requests.get('date_end')
        resultid = requests.get('resultid')
        resolution_type = requests.get('resolution_type')
        element = requests.get('element')
        result = product_fy4a_disk_point_data(date_start=date_start, date_end=date_end, lon=lon, lat=lat,
                                              resolution_type=resolution_type, resultid=resultid, element=element)
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
