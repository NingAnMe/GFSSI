from datetime import datetime
import os

from flask import Flask, request
from flask_restful import Resource, Api, reqparse

from history import product_fy4a_disk_area_data, make_zip_file, get_hash_utf8, find_result_data, data_root_dir


app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('task')


class DownloadAreaData(Resource):

    def post(self):
        print(request.form)

        requests = dict(request.form)
        print('?')
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
            in_files = [row.address for row in results]

        elif area_type == 'Area':
            try:
                in_files = product_fy4a_disk_area_data(**requests)
                in_files_length = len(in_files)
                print('找到的文件总数:{}'.format(in_files_length))
            except Exception as why:
                print('下载区域文件错误: {}'.format(why))
        elif area_type == 'Point':
            pass
        else:
            return {'error': '不支持的区域类型:{}'.format(area_type)}, 400

        if in_files is not None:
            in_files_length = len(in_files)
            print('找到的文件总数:{}'.format(in_files_length))
            dir_out = os.path.join(data_root_dir, 'TmpData')
            out_file = os.path.join(dir_out, '{}.zip'.format(hash_str))
            zip_file = make_zip_file(out_file=out_file, in_files=in_files)
            return {'zip_file': zip_file, 'code': 1}, 201
        else:
            return {'error': '没有找到任何输入文件，未生成zip文件'}, 500


api.add_resource(DownloadAreaData, '/download')

if __name__ == '__main__':
    app.run(debug=True)
