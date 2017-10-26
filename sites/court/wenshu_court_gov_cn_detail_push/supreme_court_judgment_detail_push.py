#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  'liusong'
# @Date    '2017/7/15'

import sys
import json
import time

reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from conf import m_settings
from libs.fetcher import Fetcher
from libs.taskbase import TaskBase
from libs.loghandler import getLogger
from sites.common import queue

class SupremeCourtJudgmentDetailPushWorker(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.queue = queue.Queue("supreme_court_detail")

    def start(self):
        self.queue.repair()
        try:
            while True:
                url,jsonStr = self.queue.poll()
                if jsonStr!="":
                    try:
                        judgmentMap=json.loads(jsonStr.encode('utf-8'))
                        del judgmentMap['id']
                        del judgmentMap['originUrl']
                        del judgmentMap['collectionDate']
                        self.beanstalkclient.put(m_settings.BEANSTALKD_TUBE['extract_info'],json.dumps(judgmentMap))
                        self.logger.info(jsonStr)
                        self.queue.ack(url)
                    except Exception as e:
                        self.logger.error("process url err:" + url)
                else:
                    break
        except Exception as e:
            self.logger.exception(e)

if __name__ == "__main__":
    worker = SupremeCourtJudgmentDetailPushWorker()
    worker()
