#!/usr/bin/env python
# encoding: utf-8
import os
import re
from collections import OrderedDict

import pymongo
import xlrd

# client = pymongo.MongoClient(host="172.16.215.16", port=40042)
# db_auth = client.admin
# db_auth.authenticate("work", "haizhi")
# db = client.app_data
import xlwt

if __name__ == "__main__":
    file = xlwt.Workbook()
    table = file.add_sheet('info', cell_overwrite_ok=True)
    client = pymongo.MongoClient(host="172.16.215.16", port=40042)
    db_auth = client.admin
    db_auth.authenticate("work", "haizhi")
    db = client.app_data
    try:
        excel = xlrd.open_workbook("count.xlsx")
    except Exception as e:
        print "打开失败"
    sh = excel.sheet_by_index(0)
    rows = sh.nrows
    while True:
        print "请输入起始时间,eg:2017-08-11"
        start = raw_input()
        print "请输入结束时间,eg:2017-08-12"
        end = raw_input()
        value = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        result1 = value.match(start)
        result2 = value.match(end)
        if result1 and result2 :
            break
        print "输入有误,重新输入"
        continue

    for i in xrange(2, rows):
        row_data = sh.row_values(i)
        dbname = row_data[0]
        site = row_data[1]
        count = db[dbname].find({"_in_time": {"$gte": start, "$lt": end}, "_src.0.site": site}).count()
        table.write(i, 0, site)
        table.write(i, 1, count)
        # print count
    file.save("result.xls")
