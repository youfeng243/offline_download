#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import logging
import random
import sys
import time
import traceback

import pymongo
import requests
import threading

from pymongo.errors import BulkWriteError

sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")
import nlp_pb2
import grpc
from multiprocessing.dummy import Pool as ThreadPool
reload(sys)
sys.setdefaultencoding('utf8')
from middle_ware.baseworker import BaseWorker
from conf.midware_topic_conf import logfile, handled_flag, handling_flag
class tianyancha(BaseWorker):
    def __init__(self, **kwargs):
        BaseWorker.__init__(self, logfile=logfile['tmp.logs'])
        self.session=requests.session()
        self.channel = grpc.insecure_channel("cs4:51051")
        self.stub = nlp_pb2.NlpStub(self.channel)
        # self.channel1 = grpc.insecure_channel("localhost:51052")
        # self.stub1 = nlp_pb2.NlpStub(self.channel1)
        # self.channel2 = grpc.insecure_channel("localhost:51053")
        # self.stub2 = nlp_pb2.NlpStub(self.channel2)
        # self.channel3 = grpc.insecure_channel("localhost:51054")
        # self.stub3 = nlp_pb2.NlpStub(self.channel3)




    def _insert_info_batch(self, table, lst, is_order=True, insert=False):
        if lst != None and len(lst) == 0: return
        dbtemp = self.db.db[table]
        bulk = dbtemp.initialize_ordered_bulk_op() if is_order else dbtemp.initialize_unordered_bulk_op()
        for item in lst:
            # print item
            if insert:
                bulk.insert(item)

            else:
                _id = item.pop('_id')
                bulk.find({'_id': _id}).upsert().update({'$set': item})
        try:
            bulk.execute({'w': 0})
            print ('insert_logs:' + str(len(lst)))
            logging.info('insert_logs:' + str(len(lst)))
        except BulkWriteError as bwe:
            logging.info(bwe.details)

    def save_data(self,data):
        if 'doc_content' not in data:
            return
        content=data['doc_content']
        if len(content)<10:
            return
        time1=time.time()
        response = self.stub.EventExtract(nlp_pb2.SentenceRequest2(sentence1="judge_wenshu", sentence2=content))
        print("Client received: " + response.message),'success'
        # self.wrlog(str(time.time() - time1))



    def proccess(self):
        try:
            cursor=self.query_db['judgement_wenshu'].find({})
            tmp_list=[]
            pool = ThreadPool(processes=32)
            poolasy = []
            start_schedule_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print start_schedule_time
            for element in cursor:
                try:
                    tmp_list.append(element)
                    if len(tmp_list)>100:
                        result = pool.map(self.save_data, tmp_list)
                        poolasy.append(result)
                        tmp_list=[]
                except Exception,e:
                    print e.message
                    print traceback.format_exc()
        except Exception,e:
            pass
        finally:
            print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())



if __name__ == '__main__':
    tianyancha = tianyancha()
    tianyancha.proccess()
