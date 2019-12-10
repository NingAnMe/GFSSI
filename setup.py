#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/12/9 15:44
# @Author  : NingAnMe <ninganme@qq.com>
# python setup.py build_ext --inplace
import os
from distutils.core import setup, Extension
from Cython.Build import cythonize

exclude_keyword = ['init']


def check_keyword(name, keyword):
    for key in keyword:
        if key in name:
            return True
    return False


def get_extensions(ipath):
    """
    ipath      输入目录
    extensions 编译成.so的文件列表（元素是Extension对象）
    copys      拷贝的文件列表
    initpys    __init__.py的文件列表
    """
    extensions = []
    for each in os.listdir(ipath):
        if check_keyword(each, exclude_keyword):
            continue
        elif os.path.splitext(each)[1] == ".py":
            pkg = os.path.splitext(each)[0]
            mod = os.path.join(ipath, each)
            # mod = each
            extensions.append(Extension(pkg, [mod]))
        elif os.path.splitext(each)[1] == ".pyc":
            continue
    return extensions


requires = ['numpy', 'sqlalchemy', 'scipy', 'h5py',
            'PyYAML', 'gdal', 'pyproj', 'matplotlib',
            'flask_restful']

setup(
    ext_modules=cythonize(get_extensions('lib'),
                          build_dir=os.path.join("build/tmp"))
)
