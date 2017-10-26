#!/usr/bin/env python
# encoding: utf-8
# -*- coding:UTF-8 -*-
# 用来统计火车采集器的运行情况,对于正在运行的任务,可能出现获取的topic或其他为空值或为0的情况
# 在使用过程中发现任何bug,请联系唐新.


import json
import sys
from pyExcelerator import *

reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import logging


def get_count(url, session):
    try_count = 0
    while try_count < 3:
        try:
            try_count += 1
            resp = session.get(url)
            if resp.status_code != 200 or resp.text == "":
                logging.error("网络异常")
            return json.loads(resp.content)["Count"]
        except Exception as e:
            pass
    return 0


def get_topic(url, session):
    try_count = 0
    while try_count < 3:
        try:
            try_count += 1
            resp = session.get(url)
            if resp.status_code != 200 or resp.text == "":
                print "出错,请重试"
            data = json.loads(resp.content)["Data"]
            return data[0]["topic"]
        except Exception as e:
            pass
    return ""


if __name__ == "__main__":
    try:
        f = open("火车采集器辅助.txt")
        olds = f.readlines()
        f.close()
    except:
        print "欢迎第一次使用"
    finally:
        f = open("火车采集器辅助.txt", "w")
    w = Workbook()
    sheet1 = w.add_sheet('sheet1')
    wide = 0
    length = 1
    ex = 0
    sheet1.write(0, 0, '站点'.decode("utf-8"))
    sheet1.write(0, 1, '主题'.decode("utf-8"))
    sheet1.write(0, 2, '数据量'.decode("utf-8"))
    sheet1.write(0, 3, '数据增量'.decode("utf-8"))
    session = requests.session()
    url = "http://182.61.40.11:808/api?&model=job&action=list&type=json"
    try_count = 0
    while try_count < 3:
        try:
            try_count += 1
            resp = session.get(url)
            if resp.status_code != 200 or resp.text == "":
                logging.error("网络异常")
            all = json.loads(resp.content)["Data"]
            break
        except Exception as e:
            logging.exception(e)
    if try_count == 3:
        logging.info("程序退出")
        sys.exit()
    for i in xrange(0, len(all)):
        task_id = all[i]["JobId"]
        task_name = all[i]["JobName"]
        count_url = "http://182.61.40.11:808/api?model=data&action=count&opreator=0&type=json&jobid={}".format(task_id)
        topic_url = "http://182.61.40.11:808/api?model=data&action=view&type=json&pn=0&rn=20&jobid={}".format(task_id)

        count = get_count(count_url, session)
        topic = get_topic(topic_url, session).replace('\r\n', '')
        sheet1.write(i + 1, 0, task_name.decode('utf-8'))
        sheet1.write(i + 1, 1, topic.decode('utf-8'))
        sheet1.write(i + 1, 2, str(count).decode('utf-8'))
        f.write(str(count) + "\n")
        try:
            old = olds[i]
        except:
            old = 0
        sheet1.write(i + 1, 3, count - int(old))
    f.close()
    w.save('火车采集器统计.xls')
    print "文件创建完成"
