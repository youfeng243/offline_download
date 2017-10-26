#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import sys

import time
import traceback

sys.path.append('..')
sys.path.append('../..')
sys.path.append('../../..')
reload(sys)
sys.setdefaultencoding('utf8')
from conf.midware_topic_conf import logfile
from baseworker import BaseWorker
from multiprocessing.dummy import Pool as ThreadPool


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
        cursor = self.schedule_db['tmp_offline_crawl_data'].find({"source": "supreme_court_judgment_detail.py"})
        for element in cursor:
            content = element['wenshu_content']
            tmp_result = json.loads(self.extract_keyword_news(content))
            tmp_list = []
            if 'PERSON' in tmp_result['ner_list']:
                for name in tmp_result['ner_list']['PERSON']:
                    tmp_list.append(name)
            if 'ORGANIZATION' in tmp_result['ner_list']:
                for name in tmp_result['ner_list']['ORGANIZATION']:
                    tmp_list.append(name)
            _id = element['_id']
            query_result = self.schedule_db['tmp_judge_wenshu_litigant'].find_one({"_id": _id})
            if query_result:
                query_result['nlp_litigant_list']=tmp_list
                query_result['wenshu_content']=content
                self.schedule_db['tmp_judge_wenshu_litigant'].save(query_result)
            print ''


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
