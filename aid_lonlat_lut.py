import os
import h5py
import numpy as np

from lib.lib_constant import FULL_VALUE


def readASCIIfile(ASCIIfile):
    arr = []
    geoRefer = []

    fh = iter(open(ASCIIfile))
    skiprows = 6

    for i in range(skiprows):
        try:
            this_line = next(fh)
            geoRefer.append(float(this_line.split()[1]))
        except StopIteration:
            break

    while 1:
        try:
            this_line = next(fh)
            if this_line:
                arr.append(list(map(float, this_line.split())))
        except StopIteration:
            break
    fh.close()
    return arr, geoRefer


def geoRefer2xy(geoRefer):
    ncols, nrows, xll, yll, cellsize, NODATA_value = geoRefer
    x = np.linspace(xll, xll + ncols * cellsize - cellsize, ncols)
    y = np.linspace(yll, yll + nrows * cellsize - cellsize, nrows)
    return x, y


def _write_out_file(out_file, result):
    out_dir = os.path.dirname(out_file)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    valid_count = 0
    for key in result:
        if result[key] is None:
            continue
        else:
            valid_count += 1
    if valid_count == 0:
        print('没有足够的有效数据，不生成结果文件')
        return

    try:
        compression = 'gzip'
        compression_opts = 5
        shuffle = True
        with h5py.File(out_file, 'w') as hdf5:
            for dataset in result.keys():
                dtype = np.float32
                data = result[dataset]
                data[np.isnan(data)] = FULL_VALUE
                hdf5.create_dataset(dataset,
                                    dtype=dtype, data=result[dataset], compression=compression,
                                    compression_opts=compression_opts,
                                    shuffle=shuffle)
        print('>>> 成功生成HDF文件{}'.format(out_file))
    except Exception as why:
        print(why)
        print('HDF写入数据错误')
        os.remove(out_file)


def make_lonlat_lut_1km(d_dem_file, out_file):
    ddem, geoRefer = readASCIIfile(d_dem_file)
    nx, ny = geoRefer2xy(geoRefer)
    print(1, geoRefer)
    ddemArr = np.array(ddem)
    print('ddemArr', ddemArr.shape)
    ddemArr = np.array(ddem)[::-1]
    print('ddemArr', ddemArr.shape)
    ddemArr[ddemArr == -9999] = np.nan
    xx, yy = np.meshgrid(nx, ny)
    result = {
        'Latitude': yy,
        'Longitude': xx,
        'D_DEM': ddemArr
    }
    _write_out_file(out_file, result)
