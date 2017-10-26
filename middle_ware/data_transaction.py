#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import json
import logging
import sys

import time
import traceback

import pymongo
from pymongo import DESCENDING, ASCENDING

sys.path.append('..')
sys.path.append('../..')
sys.path.append('../../..')
reload(sys)
sys.setdefaultencoding('utf8')
from conf.midware_topic_conf import logfile, handled_flag, handling_flag,table_duplicate_flag
from baseworker import BaseWorker


class midware_consumer(BaseWorker):
    def __init__(self):
        try:
            BaseWorker.__init__(self, logfile=logfile['beanstalk_consumer.logs'])
            self.tube = 'offline_crawl_data'
        except Exception as e:
            self.wrlog("sync produce fail:%s" % (traceback.format_exc()))
            self.wrlog("exception fail:%s" % (e.message))

    def start_process(self):
        self.consumer_data()

    def consumer_data(self):
        while True:
            try:
                # self.schedule_db["offline_crawl_data_judgement_wenshu"].create_index(
                #     [
                #         ('name', pymongo.ASCENDING),
                #         ('age', pymongo.ASCENDING)
                #     ],
                #     background=True,
                #     unique=True
                # )
                cursor = self.schedule_db['tmp_offline_crawl_data'].find(
                    {"deal_flag":None})
                for element in cursor:
                    try:
                        query_id=element['_id']
                        _id=self.get_duplicate_flag(element)
                        topic=element['topic']
                        if topic=='registration_company':
                            element['company']=element['company'].strip()
                            print
                        table='offline_crawl_data_'+str(topic)
                        element['_id']=_id
                        element['deal_flag']=handling_flag

                        self.schedule_db[table].save(element)
                        mod_value={
                            'deal_flag':handled_flag
                        }
                        self.schedule_db['tmp_offline_crawl_data'].update({'_id': query_id}, {"$set": mod_value})
                    except Exception,e:
                        print e.message
            except Exception as e:
                self.wrlog("consumer fail:%s" % (traceback.format_exc()))
                self.wrlog("consumer fail:%s" % (e.message))

    def get_duplicate_flag(self,data):
        m3 = hashlib.md5()
        topic=data['topic']
        duplicate_flag_list=table_duplicate_flag[topic]
        duplicate_flag_str=''
        for element in duplicate_flag_list:
            duplicate_flag_str+=str(data[element])
        md5_before_3 = duplicate_flag_str
        m3.update(md5_before_3)
        return m3.hexdigest()

    def insert_info_batch(self, table, lst, is_order=False, insert=True):
        if lst != None and len(lst) == 0: return
        dbtemp = self.schedule_db[table]
        bulk = dbtemp.initialize_ordered_bulk_op() if is_order else dbtemp.initialize_unordered_bulk_op()
        for item in lst:
            if insert:
                bulk.insert(item)
            else:
                _id = item.pop('_id')
                bulk.find({'_id': _id}).update({'$set': item})
        try:
            bulk.execute({'w': 0})
            print ('insert_logs:' + str(len(lst)))
        except:
            print traceback.format_exc()


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
