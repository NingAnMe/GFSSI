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

DATABASE_URL = 'mysql+pymysql://hzqx:PassWord@1234@183.230.93.188:3306/solar'

engine = create_engine(DATABASE_URL, echo=True)
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

    def __repr__(self):
        return """ResultData(
        planid = {}
        resultid = {}
        address = {}
        datatime = {}
        createtime = {}
        )""".format(self.planid, self.resultid, self.address, self.datatime, self.createtime)


def add_result_data(resultid, planid, address, datatime):
    result_data = ResultData()
    result_data.resultid = resultid
    result_data.planid = planid
    result_data.address = address
    result_data.datatime = datatime
    result_data.createtime = datetime.now()
    session = Session()
    session.add(result_data)
    session.commit()


add_result_data(1, 1, 'test/test.txt', datetime.now())

