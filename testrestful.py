import requests

start = '20190630000000'
end = '20190630125959'
leftuplon = 70.
leftuplat = 50.
rightdownlon = 140.
rightdownlat = 0.

auth = {
    'area_type': 'Full',
    'date_start': start,
    'date_end': end,
    'resolution_type': '4KM',
    'resultid': 'FY4A_AGRI_L2_SSI_Orbit',
    'left_up_lon': leftuplon,
    'left_up_lat': leftuplat,
    'right_down_lon': rightdownlon,
    'right_down_lat': rightdownlat
}

url = 'http://127.0.0.1:5000/download'
# url = 'http://222.128.59.164:5000/download_area_data'


r = requests.post(
    url,
    data=auth)
print(r.status_code)
print(r.text)
print(r.json())
