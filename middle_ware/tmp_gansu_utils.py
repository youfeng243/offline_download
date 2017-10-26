#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys

import time
import traceback

from pip import req
import requests

sys.path.append('..')
sys.path.append('../..')
sys.path.append('../../..')
reload(sys)
sys.setdefaultencoding('utf8')
from conf.midware_topic_conf import logfile,mongodb_schedule_data
from baseworker import BaseWorker
from libs.pybeanstalkd import PyBeanstalk


class tmp_producer(BaseWorker):
    def __init__(self):
        try:
            BaseWorker.__init__(self, logfile=logfile['tmp.logs'])
            self.pyBeanstalk = PyBeanstalk(host='cs0', port=11400)
            self.query_db=self.get_mongo_client(mongodb_schedule_data)
            self.province='gansu'
        except Exception as e:
            self.wrlog("init fail:%s" % (traceback.format_exc()))
            self.wrlog("init fail:%s" % e.message)

    def producer_data(self):
        try:
            cursor=self.query_db['gansu_all_names'].find({})
            for element in cursor:
                name=element['_id']
                self.wrlog("consumer company:%s" % name)
                result = {
                    'company_name': name,
                    'province': self.province,
                    'start_schedule_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    'query': name,
                }
                self.send_message(json.dumps(result), self.province)
        except Exception as e:
            self.wrlog("producer fail:%s" % (traceback.format_exc()))
            self.wrlog("producer fail:%s" % e.message)


    def send_message(self, message, province):
        try:
            self.pyBeanstalk.put('gs_{0}_scheduler'.format(province), message)
        except Exception:
            time.sleep(1)


if __name__ == '__main__':
    total_time_count = 0
    try:
        session=requests.session()
        for i in range(1588,1709):
            url="http://182.61.40.11:808/api?model=data&action=count&opreator=0&type=json&jobid={i}".format(i)
            print session.get(url=url).content
        producer = tmp_producer()
        producer.producer_data()
    except Exception as e:
        producer.wrlog("exception in start\te:%s" % e.message)
        producer.wrlog("traceback in start:%s\n" % (traceback.format_exc()))
        time.sleep(5)
