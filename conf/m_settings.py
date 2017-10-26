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

from conf.logger import Gsxtlogger
from conf.mongo import MongDb
from libs.pybeanstalkd import PyBeanstalk
from sites.common import util

BEANSTALKD = {
    "host": "cs2",
    "port": 11300
}
BEANSTALKD2 = {
    "host": "cs1",
    "port": 11300
}

BEANSTALKD_TUBE = {
    "extract_info": "offline_extract_info",
    "download_rsp": "download_rsp",
    "download_req": "download_req"
}
TOPICS = {
    "judgement_wenshu": 32,
    "court_ktgg": 34,
    "enterprise_owing_tax": 35,
    "zhixing_info": 42,
    "shixin_info": 38,
    'patent': 43,
    "bid_detail": 41,
    "registration_company": 193,
    'baidu_news': 40,
}

SCHEDULER_REDIS = {
    "host": "cs0",
    "port": 6379,
    "password": "haizhi@)",
    "db": 0
}

MFILE_MONGO_BACKEND = {
    "host": "182.61.13.185",
    "port": 28017,
    "user": None,
    "password": None
}
CAPTCHA_HOST = "http://172.18.180.225:9820/cap_ocr"

PROJECTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGDIR = os.path.join(PROJECTDIR, "logs")

LOCAL_FILE_BASE_DIR = os.path.join(PROJECTDIR, "data")

PROXY_HOST = "http://172.18.180.224:8571"


def mfile_database():
    client = MongoClient(host=MFILE_MONGO_BACKEND['host'], port=MFILE_MONGO_BACKEND['port'])
    database = client['mfile']
    if MFILE_MONGO_BACKEND['user'] and MFILE_MONGO_BACKEND['password']:
        database.authenticate(MFILE_MONGO_BACKEND['user'], MFILE_MONGO_BACKEND['password'])
    return database


def beanstalk_client2():
    return PyBeanstalk(BEANSTALKD2["host"], BEANSTALKD2['port'])


mongo_db_source = {
    'host': "172.17.1.119",
    'port': 40042,
    'db': 'company_data',
    "username": 'work',
    "password": 'haizhi',
}

log = Gsxtlogger('mongo.log').get_logger()

source_db = MongDb(mongo_db_source['host'], mongo_db_source['port'], mongo_db_source['db'],
                   mongo_db_source['username'],
                   mongo_db_source['password'], log=log)

extend_table = 'extend_company_list'

log.info("mongodb初始化完成..")


def store_company(province, company_name):
    data = {
        '_id': util.generator_id({}, company_name, province),
        'company_name': company_name,
        'province': province,
        'in_time': util.get_now_time(),
    }
    source_db.insert_batch_data(extend_table, [data])
