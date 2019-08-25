from __future__ import print_function

import grpc

from proto import gfssi_pb2
from proto import gfssi_pb2_grpc


def run():
    start = '20190630000000'
    end = '20190630125959'
    leftuplon = 70.
    leftuplat = 50.
    rightdownlon = 140.
    rightdownlat = 0.

    channel = grpc.insecure_channel('localhost:50051')
    stub = gfssi_pb2_grpc.DownLoadStub(channel)
    response = stub.DownloadAreaData(
        gfssi_pb2.DownLoadAreaDataRequest(date_start=start, date_end=end, frequency='Orbit', resolution_type='4KM',
                                          resultid='FY4A_AGRI_L2_SSI_Orbit',
                                          left_up_lon=leftuplon, left_up_lat=leftuplat,
                                          right_down_lon=rightdownlon, right_down_lat=rightdownlat))
    print("Greeter client received: " + response.message)


if __name__ == '__main__':
    run()
