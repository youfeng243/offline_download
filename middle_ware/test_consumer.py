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
        while True:
            try:
                job = self.pyBeanstalk.reserve(self.tube)
                if job is not None:
                    data = json.loads(job.body)
                    topic = data.get('topic', '')
                    if topic is None:
                        self.wrlog("imcomplete data \t%s\t%s" % ("!!!!", json.dumps(data)))
                        job.delete()
                    if topic is '':
                        self.wrlog("no topic data \t%s\t%s" % ("!!!!", json.dumps(data)))
                        job.delete()
                        continue
                    # 需增加数据存储功能
                    result = self.topic_choose(topic=topic, mq_data=data)
                    if result:
                        self.wrlog("consumer data in topic \t%s\t%s" % (topic, json.dumps(data)))
                        job.delete()
                        continue
                    else:
                        print topic
                        self.wrlog("imcomplete data \t%s\t%s" % ("!!!!", json.dumps(data)))
                        job.delete()
            except Exception as e:
                self.wrlog("consumer fail:%s" % (traceback.format_exc()))
                self.wrlog("consumer fail:%s" % (e.message))

    def proccess(self):
        while True:
            pool = ThreadPool(processes=16)
            poolasy = []
            tmp_list=[]
            try:
                content = "中国基金网  2016年09月13日 05:00银河岁岁回报定期开放债券型证券投资基金关于新增招商银行股份有限公司为代销机构的公告  经银河基金管理有限公司与招商银行股份有限公司协商,自 2016 年 9 月 12...  百度快照"
                tmp_list.append(content)
                result = pool.map(self.tmp_extract, tmp_list)
                poolasy.append(result)
            except Exception, e:
                print traceback.format_exc()
            finally:
                for item in poolasy:
                    self.wrlog(item)
                pool.close()

    def tmp_extract(self, content):
        time1=time.time()
        result = self.extract_keyword_news(content)
        print result,time.time()-time1


if __name__ == '__main__':
    total_time_count = 0
    while True:
        try:
            consumer = midware_consumer()
            consumer.proccess()
        except Exception as e:
            consumer.wrlog("exception in start\te:%s" % (e.message))
            consumer.wrlog("traceback in start:%s\n" % (traceback.format_exc()))
            time.sleep(5)
