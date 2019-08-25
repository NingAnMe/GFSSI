#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/15
@Author  : AnNing
"""
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker

from lib.lib_constant import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(engine)

Base = declarative_base()


class ResultData(Base):
    __tablename__ = 'result_data'

    id = Column(Integer, primary_key=True)
    planid = Column(Integer)
    resultid = Column(String)
    address = Column(String)
    datatime = Column(DateTime)
    createtime = Column(DateTime)
    datasize = Column(String)
    linkeddata = Column(String)
    remarks = Column(String)
    element = Column(String)
    resolution_type = Column(String)
    area_type = Column(String)

    def __repr__(self):
        return """ResultData(
        planid = {}
        resultid = {}
        resolution_type = {}
        area_type = {}
        element = {}
        address = {}
        datatime = {}
        createtime = {}
        )""".format(self.planid, self.resultid, self.resolution_type, self.area_type, self.element,
                    self.address, self.datatime, self.createtime)


def add_result_data(resultid=None, planid=None, resolution_type=None, area_type=None, element=None, address=None,
                    datatime=None):
    result_data = ResultData()
    result_data.resultid = resultid
    result_data.planid = planid
    result_data.address = address
    result_data.datatime = datatime
    result_data.createtime = datetime.now()
    result_data.resolution_type = resolution_type
    result_data.area_type = area_type
    result_data.element = element
    session = Session()
    session.add(result_data)
    session.commit()
    print(result_data)


def find_result_data(resultid=None, datatime_start=None, datatime_end=None, resolution_type=None):
    session = Session()
    results = session.query(ResultData).filter(ResultData.resultid == resultid,
                                               ResultData.resolution_type == resolution_type,
                                               ResultData.datatime >= datatime_start,
                                               ResultData.datatime <= datatime_end)
    print(resultid, datatime_start, datatime_end, resolution_type)
    print('共找到结果:{}'.format(results.count()))
    return results


def find_result_image(resultid=None, datatime_start=None, datatime_end=None, element=None, resolution_type=None,
                      area_type=None):
    session = Session()
    results = session.query(ResultData).filter(ResultData.resultid == resultid,
                                               ResultData.resolution_type == resolution_type,
                                               ResultData.element == element,
                                               ResultData == area_type,
                                               ResultData.datatime >= datatime_start,
                                               ResultData.datatime <= datatime_end)
    print(resultid, datatime_start, datatime_end, resolution_type, area_type, element)
    print('共找到结果:{}'.format(results.count()))
    return results
