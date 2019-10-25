import requests

start = '20190501000000'
end = '20190501235959'
leftuplon = 70.
leftuplat = 50.
rightdownlon = 140.
rightdownlat = 0.
#
# auth = {
#     'area_type': 'Point',
#     'date_start': start,
#     'date_end': end,
#     'resolution_type': '4KM',
#     'resultid': 'FY4A_AGRI_L2_SSI_Orbit',
#     'left_up_lon': leftuplon,
#     'left_up_lat': leftuplat,
#     'right_down_lon': rightdownlon,
#     'right_down_lat': rightdownlat
# }
#
# # url = 'http://127.0.0.1:5000/download'
# url = 'http://222.128.59.164:5000/download'
#
#
# r = requests.post(
#     url,
#     data=auth)
# print(r.status_code)
# print(r.text)
# print(r.json())


auth = {
    'date_start': start,
    'date_end': end,
    'resolution_type': '1KM',
    'resultid': 'FY3D_MERSI_L3_SSI_Daily',
    'lon': 116.3672,
    'lat': 40.0781,
    'element': 'Itol',
    'is_live': True,
    'is_forecast': False
}

# url = 'http://127.0.0.1:5000/get_point_data'
url = 'http://127.0.0.1:5000/get_point_data'


r = requests.post(
    url,
    data=auth)
print(r.status_code)
print(r.text)
print(r.json())
