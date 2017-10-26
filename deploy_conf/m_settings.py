#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-21 15:4

"""
这个是模板配置文件,使用的时候复制一份命名为m_settings.py
切记不要上传m_settions.py
"""
import os

from pymongo import MongoClient

from libs.pybeanstalkd import PyBeanstalk

BEANSTALKD = {
    "host": "Crawler-Downloader2",
    "port": 11300
}
BEANSTALKD_TUBE = {
    "extract_info": "extract_info"
}
TOPICS = {
    "judgement_wenshu": 32,
    "court_ktgg": 34,
    "zhixing_info": 42,
    "shixin_info": 38,
    'patent': 43,
    'enterprise_owing_tax': 35
}

SCHEDULER_REDIS = {
    "host": "Crawler-DataServer2",
    "port": 6379,
    "password": "haizhi@)",
    "db": 0
}

MFILE_MONGO_BACKEND = {
    "host": "Crawler-DataServer2",
    "port": 40042,
    "user": "work",
    "password": "haizhi"
}
CAPTCHA_HOST = "http://Crawler-Downloader1:9820/cap_ocr"

PROJECTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGDIR = os.path.join(PROJECTDIR, "logs")

LOCAL_FILE_BASE_DIR = os.path.join(PROJECTDIR, "data")


def mfile_database():
    client = MongoClient(host=MFILE_MONGO_BACKEND['host'], port=MFILE_MONGO_BACKEND['port'])
    database = client['mfile']
    if MFILE_MONGO_BACKEND['user'] and MFILE_MONGO_BACKEND['password']:
        database.authenticate(MFILE_MONGO_BACKEND['user'], MFILE_MONGO_BACKEND['password'])
    return database


def beanstalk_client():
    return PyBeanstalk(BEANSTALKD["host"], BEANSTALKD['port'])
