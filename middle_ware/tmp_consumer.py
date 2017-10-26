#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
import time
import traceback

import pymongo
sys.path.append('..')
sys.path.append('../..')
sys.path.append('../../..')
reload(sys)
sys.setdefaultencoding('utf8')
from conf.midware_topic_conf import mongodb_schedule_data, beanstalk_host_cs2, beanstalk_port
from libs.pybeanstalk import PyBeanstalk



class midware_consumer():
    def __init__(self):
        try:
            self.pyBeanstalk = PyBeanstalk(host=beanstalk_host_cs2, port=beanstalk_port)
            self.tube = 'offline_crawl_data'
            self.schedule_db = self.get_mongo_client(mongodb_schedule_data)
        except Exception as e:
            self.wrlog("sync produce fail:%s" % (traceback.format_exc()))
            self.wrlog("exception fail:%s" % (e.message))

    def start_process(self):
        self.consumer_data()

    def consumer_data(self):
        while True:
            try:
                job = self.pyBeanstalk.reserve(self.tube)
                if job != None:
                    data = json.loads(job.body)
                    self.schedule_db['tmp_offline_crawl_data'].save(data)
                    job.delete()
            except Exception as e:
                self.wrlog("consumer fail:%s" % (traceback.format_exc()))
                self.wrlog("consumer fail:%s" % (e.message))

    def get_mongo_client(self, target_db):
        try:
            conn = pymongo.MongoClient(host=target_db["host"],
                                       port=target_db["port"],
                                       serverSelectionTimeoutMS=60)
            conn[target_db['name']].authenticate(target_db['username'], target_db['password'])
            database = conn[target_db['name']]
            return database
        except Exception, mongo_exception:
            self.wrlog("exception in get_mongo_client:%s" % mongo_exception.message)
            self.wrlog("get_mongo_client fail:%s\n" % (traceback.format_exc()))
            time.sleep(1)

if __name__ == '__main__':
    total_time_count = 0
    while True:
        try:
            consumer = midware_consumer()
            consumer.start_process()
        except Exception as e:
            consumer.wrlog("exception in start\te:%s" % (e.message))
            consumer.wrlog("traceback in start:%s\n" % (traceback.format_exc()))
            time.sleep(5)
