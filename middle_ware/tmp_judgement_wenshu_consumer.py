#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
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

from libs.pybeanstalk import PyBeanstalk
import pymongo
from conf.midware_topic_conf import mongodb_app_data, mongodb_schedule_data, beanstalk_host_cs2, beanstalk_port, \
    beanstalk_tube, IMCOMPLETE_DATA, \
    COMPLETE_DATA, topic, logfile,handled_flag,handling_flag
from conf import m_settings
from logging.handlers import RotatingFileHandler
from libs.pybeanstalkd import thrift2bytes
from libs.packet_parser_info import packet


from utils import nlp_pb2
import grpc


class BaseWorker(object):
    def __init__(self, logfile):
        try:
            self.logging = self.getLogger(logfile)
            self.query_db = self.get_mongo_client(mongodb_app_data)
            self.save_db = self.get_mongo_client(mongodb_app_data)
            self.schedule_db = self.get_mongo_client(mongodb_schedule_data)
            self.pyBeanstalk = PyBeanstalk(host=beanstalk_host_cs2, port=beanstalk_port)
            self.tube = beanstalk_tube
            self.topic = topic
        except Exception as e:
            self.wrlog("sync produce fail:%s" % (traceback.format_exc()))
            self.wrlog("exception fail:%s" % e.message)
            time.sleep(1)

    def wrlog(self, message):
        self.logging.info('%s:%s' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), message))

    def getLogger(self, uri, maxsize=1000000000):
        logger = logging.getLogger('A')
        logger.setLevel(logging.INFO)
        log_file = RotatingFileHandler(uri, maxBytes=maxsize, backupCount=5)
        if len(logger.handlers) == 0:
            logger.addHandler(log_file)
        return logger

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

    # 根据不同主题选取不同方法来处理数据
    def topic_choose(self, topic, mq_data):
        if str(topic) not in self.topic:
            return False

        method_name = str(topic) + "_handler"
        method = getattr(self, method_name, lambda: "nothing")
        return method(mq_data)

    # def sendData(self, topic, extract_data):
    #     self.pyBeanstalk.put(m_settings.BEANSTALKD_TUBE['extract_info'],
    #                          thrift2bytes(packet(m_settings.TOPICS[topic], extract_data['sourceUrl'],
    #                                              extract_data)))

    def get_md5_value(self, content):
        my_md5 = hashlib.md5()  # 获取一个MD5的加密算法对象
        my_md5.update(content)  # 得到MD5消息摘要
        my_md5_Digest = my_md5.hexdigest()  # 以16进制返回消息摘要，32位
        return my_md5_Digest

    def bid_detail_handler(self, mq_data):
        try:
            href = mq_data['url']
            title = mq_data['title']
            content = mq_data['content']
            doc_id = self.get_md5_value(content)
            province = mq_data['province']
            publish_time = mq_data['publish_time']
            url = "http://www.bid_detail.com/haizhi/{}".format(doc_id)
            extract_data = {
                "title": title,
                "publish_time": publish_time,
                "content": content,
                "province": province,
                "_site_record_id": "http://www.bid_detail.com/haizhi/{}".format(doc_id),
                "href": href
            }
            self.pyBeanstalk.put("offline_extract_info",
                                 thrift2bytes(packet(topic_id=m_settings.TOPICS['bid_detail'], url=url,
                                                     data=extract_data)))
            return COMPLETE_DATA
        except Exception, e:
            self.wrlog("exception in  bid_detail_handler:%s" % (traceback.format_exc()))
            self.wrlog("exception in  bid_detail_handler:%s" % (e.message))
            return IMCOMPLETE_DATA

    def zhixing_info_handler(self, mq_data):

        return mq_data

    def registration_company_handler(self, mq_data):
        try:

            url = mq_data['url']  # 抓取到数据的url
            del mq_data['url']
            self.pyBeanstalk.put(m_settings.BEANSTALKD_TUBE['extract_info'],
                                 thrift2bytes(packet(topic_id=m_settings.TOPICS['registration_company'], url=url,
                                                     data=mq_data)))
            return COMPLETE_DATA
        except Exception, e:
            self.wrlog("exception in  registration_company_handler:%s" % (traceback.format_exc()))
            self.wrlog("exception in  registration_company_handler:%s" % (e.message))
            return IMCOMPLETE_DATA

    def baidu_news_handler(self, mq_data):
        try:
            url = mq_data['url']  # 抓取到数据的url
            mq_data['href'] = url
            del mq_data['url']
            if 'publist_time' in mq_data:
                mq_data['publish_time'] = mq_data['publist_time']
                del mq_data['publist_time']
            keyword = self.extract_keyword_news(mq_data['summary'])
            keyword_list = json.loads(keyword)['ner_list'].get('ORGANIZATION', [])
            if len(keyword_list) == 0:
                mq_data['keyword'] = self.get_md5_value(mq_data['summary'])
            else:
                mq_data['keyword'] = str(keyword_list[0])
            url = 'http://news.baidu.com/ns?tn=news&rn=20&word={0}&cl=2'.format(mq_data['keyword'])
            tmp_list = [mq_data]
            send_data = {
                "datas": tmp_list
            }
            self.pyBeanstalk.put('offline_extract_info',
                                 thrift2bytes(packet(topic_id=m_settings.TOPICS['baidu_news'], url=url,
                                                     data=send_data)))
            return COMPLETE_DATA
        except Exception, e:
            self.wrlog("exception in  baidu_news_handler:%s" % (traceback.format_exc()))
            self.wrlog("exception in  baidu_news_handler:%s" % (e.message))
            return IMCOMPLETE_DATA

    def judgement_wenshu_handler(self, data):
        a=0
        while True:
            try:
                cursor=self.schedule_db['offline_crawl_data_judgement_wenshu'].find({'deal_flag':handling_flag})
                for mq_data in cursor:
                    case_name = mq_data["case_name"]
                    wenshu_content = mq_data["wenshu_content"]
                    url = mq_data['url']
                    doc_id = self.get_md5_value(wenshu_content)
                    extract_data = {
                        "case_name": case_name,
                        "doc_content": wenshu_content,
                        "bulletin_date": "",
                        "doc_id": doc_id,
                        "is_legal": 1,
                        "_site_record_id": url.split('http://')[1].split('/')[0],
                        "url": url
                    }
                    mod_value = {
                        'deal_flag': handled_flag
                    }
                    self.schedule_db['offline_crawl_data_judgement_wenshu'].update({'_id': mq_data['_id']}, {"$set": mod_value})
                    self.pyBeanstalk.put("offline_extract_info",
                                         thrift2bytes(packet(topic_id=m_settings.TOPICS['judgement_wenshu'], url=url,
                                                             data=extract_data)))
                    a+=1
                    print a
            except Exception, e:
                self.wrlog("exception in  judgement_wenshu_handler:%s" % (traceback.format_exc()))
                self.wrlog("exception in  judgement_wenshu_handler:%s" % (e.message))

    def extract_keyword_news(self, content):
        channel = grpc.insecure_channel("ml0:51061")
        stub = nlp_pb2.NlpStub(channel)
        response = stub.NamedIdentityRecognize(nlp_pb2.SentenceRequest(sentence=content))
        return response.message

    def check_data(self, mq_data):

        pass

    # 保存原始网页数据
    def save_html_data(self, mq_data, topic):
        pass

    # 保存结构化数据至mongo
    def save_structured_data(self, mq_data, topic):
        self.save_db[topic].save(data)
        pass

    # 将数据传输至抓取系统
    def send_message(self):
        pass


if __name__ == '__main__':
    total_time_count = 0
    while True:
        try:
            base_worker = BaseWorker(logfile=logfile['beanstalk_consumer.logs'])
            data = {}
            base_worker.judgement_wenshu_handler(data=data)
        except Exception as e:
            base_worker.wrlog("exception in start\te:%s" % e.message)
            base_worker.wrlog("traceback in start:%s\n" % (traceback.format_exc()))
            time.sleep(5)
