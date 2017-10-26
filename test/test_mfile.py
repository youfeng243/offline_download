#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-18 14:43

from libs.mfileclient import MFileClient
from pymongo import MongoClient
mc = MongoClient("172.16.215.36", 40042)
db = mc['mfile']
db.authenticate("work", "haizhi")
mf = MFileClient(db)

"""
for f in mf.get_many("jimei.gov.cn", {}):
    f.pop("data")
    print f
"""
mf.remove("gd-n-tax.gov.cn", query={}, limit=0)