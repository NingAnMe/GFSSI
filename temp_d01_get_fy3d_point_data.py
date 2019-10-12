import os
import sys

from lib.lib_read_ssi import FY3DSSIENVI
# from lib.lib_constant import KDTREE_LUT_FY3_1KM
# import pickle
# with open(KDTREE_LUT_FY3_1KM, 'rb') as fp:
#     kdtree_idx_fy3_1km, kdtree_ck_fy3_1km = pickle.load(fp)


in_dir = '/home/gfssi/GFData/SourceData/FY3D/SSI_1KM/Daily'


# lat = 30
# lon = 105
# r = kdtree_ck_fy3_1km.query([(113.4167, 40.0833), (112.5833, 37.6167), (111.3667, 35.6500)], 1)
# print(r)
# print(kdtree_idx_fy3_1km[0][r[1]], kdtree_idx_fy3_1km[1][r[1]])

fix = {
    'DaTong': (113.4167, 40.0833),
    'TaiYuan': (112.5833, 37.6167),
    'HouMa': (111.3667, 35.6500),
}

fix_index = {
    'DaTong': (1392, 4042),
    'TaiYuan': (1638, 3958),
    'HouMa': (1835, 3837),
}
results = {
    'DaTong': {},
    'TaiYuan': {},
    'HouMa': {},
}

in_files = os.listdir(in_dir)
in_files.sort()
file_count = len(in_files)
in_files = [os.path.join(in_dir, i) for i in in_files]
print('总共找到文件：{}'.format(file_count))

ssi_type_dict = {
    'Bc': ('Ib', 0, 1400, 'w/m2'),
    'Gc': ('Itol', 0, 1400, 'w/m2'),
    'Dc': ('Id', 0, 1400, 'w/m2'),
    'Sz': ('Sz', 0, 90, '')
}


def __get_point_data_by_index(in_file, index):
    try:
        data_loader = FY3DSSIENVI(in_file)
        data = data_loader.get_data()[index]
        return data
    except Exception as why:
        print(why)


if __name__ == '__main__':
    fix_name = sys.argv[1]
    index = fix_index[fix_name]
    dates = []
    bcs = []
    gcs = []
    dcs = []
    szs = []
    out_file = 'gfssi_tmp/{}.txt'.format(fix_name)
    for in_file in in_files:
        print(in_file)
        if 'dat' not in in_file:
            continue
        if 'Bc' not in in_file:
            continue
        bc_file = in_file
        gc_file = in_file.replace('Bc', 'Gc')
        dc_file = in_file.replace('Bc', 'Dc')
        sz_file = in_file.replace('Bc', 'Sz')
        bc = __get_point_data_by_index(bc_file, index)
        gc = __get_point_data_by_index(gc_file, index)
        dc = __get_point_data_by_index(dc_file, index)
        sz = __get_point_data_by_index(sz_file, index)
        is_none = False
        for data in [bc, gc, dc, sz]:
            if data is None:
                is_none = True
        if is_none:
            print('不能正确获取数据：{}'.format(in_file))
            continue
        date = os.path.basename(in_file)[3:11]

        dates.append(date+'0000')
        bcs.append(bc)
        gcs.append(gc)
        dcs.append(dc)
        szs.append(sz)
    print(dates)
    print(bcs)
    print(gcs)
    print(dcs)
    print(szs)
    with open(out_file, 'w') as fp:
        fp.write('Date\tSz\tItol\tIb\tId\n')
        for date_, sz_, gc_, bc_, dc_ in zip(dates, szs, gcs, bcs, dcs):
            fp.write('{}\t{:.04f}\t{:.04f}\t{:.04f}\t{:.04f}\n'.format(date_, sz_, gc_, bc_, dc_))
    print('>>>:{}'.format(out_file))
