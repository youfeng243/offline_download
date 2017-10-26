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
from conf.midware_topic_conf import logfile, handled_flag, handling_flag
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
        while True:
            try:
                cursor = self.schedule_db['offline_crawl_data_trainspider_baidu_news'].find(
                    {"deal_flag": handling_flag})
                for element in cursor:
                    topic = element.get('topic', '')
                    data = element
                    data['url'] = data['PageUrl']
                    _id=element['_id']
                    del data['_id']
                    del data['已发'.decode('utf-8')]
                    del data['已采'.decode('utf-8')]
                    if 'source_page' in data:
                        del data['source_page']
                    del data['deal_flag']
                    del data['topic']
                    del data['source']
                    del data['ID']
                    result = self.topic_choose(topic=topic, mq_data=data)
                    if result:
                        self.wrlog("consumer data in topic \t%s\t%s" % (topic, json.dumps(data)))
                        mod_value = {
                            "deal_flag": handled_flag
                        }
                        self.schedule_db['offline_crawl_data_trainspider_baidu_news'].update({'_id': _id},
                                                                                             {"$set": mod_value})
                        continue
                    else:
                        print topic
                        self.wrlog("imcomplete data \t%s\t%s" % ("!!!!", json.dumps(data)))
            except Exception as e:
                self.wrlog("consumer fail:%s" % (traceback.format_exc()))
                self.wrlog("consumer fail:%s" % (e.message))


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
