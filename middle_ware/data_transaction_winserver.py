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
from conf.midware_topic_conf import logfile, handled_flag, handling_flag, winserver_table_duplicate_flag,path
from baseworker import BaseWorker


class midware_consumer(BaseWorker):
    def __init__(self):
        try:
            BaseWorker.__init__(self, logfile=path + 'mfiledownload/logs/winserver_transaction.logs')
            self.tube = 'offline_crawl_data'
        except Exception as e:
            self.wrlog("sync produce fail:%s" % (traceback.format_exc()))
            self.wrlog("exception fail:%s" % (e.message))

    def start_process(self):
        self.transaction_data()

    def transaction_data(self):
        session = requests.session()
        job_url="http://182.61.40.11:808/api?&model=job&action=list&type=json"
        job_content=json.loads(session.get(url=job_url).content)
        jobid_list = [
            "1708"
        ]
        # for ele in job_content['Data']:
            # jobid_list.append(ele['JobId'])
        for jobid in jobid_list:
            try:
                count_url = "http://182.61.40.11:808/api?model=data&action=count&opreator=0&type=json&jobid={}".format(
                    jobid)
                count = json.loads(session.get(url=count_url).content)['Count']
                page_count = int(count) / 20
                for i in range(1, page_count + 1):
                    try:
                        url = "http://182.61.40.11:808/api?model=data&action=view&type=json&pn={0}&rn=20&jobid={1}".format(
                            i, jobid)
                        result_content = json.loads(session.get(url=url).content)
                        del_list = [
                            "ID", "已发", "已采","_site_record_id","source",'source_page'
                        ]
                        save_data={

                        }
                        for element in result_content['Data']:
                            ID=element['ID']
                            self.wrlog("ID:%s" % (ID))
                            self.wrlog("jobid:%s" % (jobid))
                            for content in element:
                                if content in del_list:
                                    continue
                                else:
                                    save_data[content]=element[content]
                            topic = save_data['topic']
                            if topic=='news':
                                topic='baidu_news'
                            if topic not in winserver_table_duplicate_flag:
                                self.wrlog("topic error data:%s" % (json.dumps(element)))
                            save_data['deal_flag'] = handling_flag
                            table = 'tmp_09_25_offline_crawl_data_' + str(topic)
                            _id = self.get_duplicate_flag(save_data)
                            continue
                            if _id is None:
                                self.wrlog("error data:%s" % (json.dumps(element)))
                                continue
                            # query=self.schedule_db[table].find_one({"_id":_id})
                            # if query:
                            #     continue
                            save_data['_id'] = _id
                            save_data['_in_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            save_data['_utime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            self.schedule_db[table].save(save_data)
                    except Exception, e:
                        self.wrlog("sync produce fail:%s" % (traceback.format_exc()))
                        self.wrlog("exception fail:%s" % (e.message))
            except Exception, e:
                self.wrlog("sync produce fail:%s" % (traceback.format_exc()))
                self.wrlog("exception fail:%s" % (e.message))

    def get_duplicate_flag(self, data):
        try:
            m3 = hashlib.md5()
            topic = data['topic']
            topic=str(topic).strip()
            duplicate_flag_list = winserver_table_duplicate_flag[topic]
            duplicate_flag_str = ''
            for element in duplicate_flag_list:
                duplicate_flag_str += str(data[element])
            md5_before_3 = duplicate_flag_str
            m3.update(md5_before_3)
            return m3.hexdigest()
        except Exception,e:
            self.wrlog("sync produce fail:%s" % (traceback.format_exc()))
            self.wrlog("exception fail:%s" % (e.message))
            return None


if __name__ == '__main__':
    total_time_count = 0
    try:
        consumer = midware_consumer()
        consumer.start_process()
    except Exception as e:
        consumer.wrlog("exception in start\te:%s" % (e.message))
        consumer.wrlog("traceback in start:%s\n" % (traceback.format_exc()))
        time.sleep(5)
