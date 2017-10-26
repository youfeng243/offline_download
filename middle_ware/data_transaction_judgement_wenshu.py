#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import json
import logging
import sys

import time
import traceback

import requests

sys.path.append('..')
sys.path.append('../..')
sys.path.append('../../..')
reload(sys)
sys.setdefaultencoding('utf8')
from conf.midware_topic_conf import logfile,handled_flag,handling_flag
from baseworker import BaseWorker
from multiprocessing.dummy import Pool as ThreadPool


class midware_consumer(BaseWorker):
    def __init__(self):
        try:
            BaseWorker.__init__(self, logfile=logfile['data_transaction.logs'])
            self.tube = 'offline_crawl_data'
        except Exception as e:
            self.wrlog("sync produce fail:%s" % (traceback.format_exc()))
            self.wrlog("exception fail:%s" % (e.message))

    def start_process(self):
        self.transaction_data()

    def transaction_data(self):
        session=requests.session()
        jobid_list=[]
        a=0
        for i in range(2065,2160):
            jobid_list.append(i)
        for jobid in jobid_list:
            try:
                count_url="http://182.61.40.11:808/api?model=data&action=count&opreator=0&type=json&jobid={}".format(jobid)
                count=json.loads(session.get(url=count_url).content)['Count']
                page_count=int(count)/20
                url1 = "http://182.61.40.11:808/api?model=data&action=view&type=json&pn={0}&rn=20&jobid={1}".format(1,
                                                                                                                   jobid)
                result_content = json.loads(session.get(url=url1).content)
                for element_test in result_content['Data']:
                    if element_test['topic'] != 'judgement_wenshu':
                        break_boolean=True
                    else:
                        break_boolean=False
                    break
                if break_boolean:
                    print jobid
                    continue
                for i in range(1,page_count+1):
                    try:
                        url="http://182.61.40.11:808/api?model=data&action=view&type=json&pn={0}&rn=20&jobid={1}".format(i,jobid)
                        result_content=json.loads(session.get(url=url).content)
                        for element in result_content['Data']:
                            if element['topic']!='judgement_wenshu':
                                break
                            if element['topic'] =='' :
                                print
                            save_data=element
                            case_name = element['case_name']
                            url = element['PageUrl']
                            _id = self.get_duplicate_flag(case_name, url)
                            data = {
                                "_id": _id,
                                "case_name": case_name,
                                "url": url,
                                "wenshu_content": element['wenshu_content'],
                                "deal_flag": handling_flag
                            }

                            self.schedule_db['offline_crawl_data_judgement_wenshu'].save(data)
                            a+=1
                            print a
                    except Exception,e:
                        self.wrlog("sync produce fail:%s" % (traceback.format_exc()))
                        self.wrlog("exception fail:%s" % (e.message))
            except Exception,e:
                self.wrlog("sync produce fail:%s" % (traceback.format_exc()))
                self.wrlog("exception fail:%s" % (e.message))

    def get_duplicate_flag(self, case_name, url):
        m3 = hashlib.md5()
        md5_before_3 = str(case_name) + str(url)
        m3.update(md5_before_3)
        return m3.hexdigest()


if __name__ == '__main__':
    total_time_count = 0
    try:
        consumer = midware_consumer()
        consumer.start_process()
    except Exception as e:
        consumer.wrlog("exception in start\te:%s" % (e.message))
        consumer.wrlog("traceback in start:%s\n" % (traceback.format_exc()))
        time.sleep(5)
