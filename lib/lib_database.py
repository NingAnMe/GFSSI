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


def add_result_data(resultid, planid, resolution_type, area_type, element, address, datatime):
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
