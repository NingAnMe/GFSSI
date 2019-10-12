from concurrent import futures
import time

import grpc

import gfssi_pb2
import gfssi_pb2_grpc

from schedule import product_fy4a_disk_area_data

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class DownLoad(gfssi_pb2_grpc.DownLoadServicer):
    def DownLoadAreaData(self, request, response):
        print('adsfadsfadsf')
        date_start = request.get('date_start')
        date_end = request.get('date_end')
        left_up_lon = request.get('left_up_lon')
        left_up_lat = request.get('left_up_lat')
        right_down_lon = request.get('right_down_lon')
        right_down_lat = request.get('right_down_lat')
        frequency = request.get('frequency')
        resolution_type = request.get('resolution_type')
        resultid = request.get('resultid')
        zip_file = product_fy4a_disk_area_data(date_start=date_start,
                                               date_end=date_end,
                                               left_up_lon=left_up_lon,
                                               left_up_lat=left_up_lat,
                                               right_down_lon=right_down_lon,
                                               right_down_lat=right_down_lat,
                                               frequency=frequency,
                                               resolution_type=resolution_type,
                                               resultid=resultid, )
        return gfssi_pb2.DownLoadAreaDataResponse(code=1, zip_file=zip_file)


# class Greeter(hello_pb2_grpc.GreeterServicer):
#     # 工作函数
#     def SayHello(self, request, context):
#         return hello_pb2.HelloReply(message='Hello, %s!' % request.name)


def serve():
    # gRPC 服务器
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gfssi_pb2_grpc.add_DownLoadServicer_to_server(DownLoad(), server)
    server.add_insecure_port('[::]:50051')
    server.start()  # start() 不会阻塞，如果运行时你的代码没有其它的事情可做，你可能需要循环等待。
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
