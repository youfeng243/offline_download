#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-24 16:28
import json
import sys
import time

sys.path.append("..")
sys.path.append("../..")


from conf import m_settings
from libs.taskbase import TaskBase


class LanzhouPublicResourceTenderWorker(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.beanstalkclient = m_settings.beanstalk_client()



    def sendData(self):
        extract_data={
            "topic":"registration_company",
            "company":"招商银行股份有限公司",
            "province":"广东",
            "city":"广东深圳",
            "registered_date":"1987-03-31",#"2011-11-11"
            "_site_record_id":"zbox.sz.haizhi.com",   #站点的site,
            "url":"http://zbox.sz.haizhi.com/ehuqnjfbg" #抓取到数据的url
        }
        self.beanstalkclient.put("offline_crawl_data",json.dumps(extract_data))
        time.sleep(1)

if __name__ == "__main__":
    worker = LanzhouPublicResourceTenderWorker()
    worker.sendData()
