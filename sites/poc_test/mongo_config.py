#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time: 2017/7/12 上午11:22
@Author: CZC
@File: config.py
"""


class TestDataDB(object):
    MONGODB_SERVER = "mongo0"
    MONGODB_PORT = 40042
    MONGODB_DB = "test"
    MONGO_USER = "work"
    MONGO_PSW = "haizhi"

    MONGODB_COLLECTION = "gdebidding"
    MONGODB_COLLECTION2 = "landchina"
    MONGODB_COLLECTION3 = "landchina2"
    MONGODB_COLLECTION0819 = "landchina0819"




BEANSTALK_HOST = 'cs2'
BEANSTALK_PORT = 11300
BEANSTALK_TUBE = 'offline_extract_info'

TOPIC = {
    'patent': 43,
}
