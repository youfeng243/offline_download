#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  'liusong'
# @Date    '2017/7/15'

import sys
import time
import random

reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from conf import m_settings
from libs.fetcher import Fetcher
from libs.packet_parser_info import packet
from libs.pybeanstalkd import thrift2bytes
from libs.taskbase import TaskBase
from libs.loghandler import getLogger
from sites.common import urlutils, extractutils,queue
from sites.common.pyqueryutils import ExtractItem
from sites.common.chrome_selenium import ChromeSelenium

post_data = {

}

headMap = {}
headMap["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8";
headMap["Accept-Language"] = "zh-CN,zh;q=0.8"
headMap["Cache-Control"] = "max-age=0"
headMap[
    "User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
headMap["Upgrade-Insecure-Requests"] = "1"


class SupremeCourtJudgmentDetailWorker(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.siteHost = "wenshu.court.gov.cn"
        chromedriverPath = "/home/work/webdriver/chromedriver"
        proxyConnection = "HDW0OWP3S3E4M8TD:3CC9C9FEB5EF1175@proxy.abuyun.com:9020"
        self.downer = ChromeSelenium(chromedriverPath,intervalTime=3000, proxyConnection=proxyConnection)
        self.waitCount=3
        self.queue = queue.Queue("supreme_court_detail")




    def start(self):
        extractItems = []


        titleExtractItem = ExtractItem("case_name", True, True,
                                       "input[id='hidCaseName']", "value")
        extractItems.append(titleExtractItem)

        # publishDateExtractItem = ExtractItem("publishDate", False, True,
        #                                      "td[id='tdFBRQ']", "text",
        #                                      neadReplaceText="发布日期：", replaceText="")
        #
        # extractItems.append(publishDateExtractItem)

        contentExtractItem = ExtractItem("wenshu_content", False, True,
                                         "div[id='DivContent']", "text")
        extractItems.append(contentExtractItem)


        self.queue.repair()
        try:
            while True:
                page = self.queue.poll()
                if page is not None:
                    try:
                        self.downer.down(page.url)
                        html = self.downer.getHtml()
                        extractResultMap = extractutils.extract(html, extractItems)
                        extractResultMap["url"]=[page.url]
                        extractResultMap["_site_record_id"]=[urlutils.getHost(page.url)]
                        extractResultMap["topic"] = ["judgement_wenshu"]
                        extractResultMap["source"]= ["supreme_court_judgment_list.py"]
                        judgmentData=self.buildData(extractResultMap)
                        self.beanstalkclient.put(m_settings.BEANSTALKD_TUBE['extract_info'],
                                                 thrift2bytes(packet(m_settings.TOPICS['judgement_wenshu'], page.url,
                                                                     judgmentData)))
                        self.prinitConsole(extractResultMap)
                        self.queue.ack(page)
                        time.sleep(random.randint(3, 6))
                    except Exception as e:
                        if page.retryCount>3:
                            self.logger.error("process url count more than 3:"+page.url)
                            self.queue.updatePush(page)
                        else:
                            page.retryCount=page.retryCount+1
                            self.queue.updatePush(page)
                else:
                    break
        except Exception as e:
            self.logger.exception(e)
        finally:
            if self.downer is not None:
                self.downer.close()

    def prinitConsole(self, extractResultMap):
        primarySize = len(extractResultMap["case_name"])
        for i in range(0, primarySize):
            printString = "{"
            for key in extractResultMap:
                printString += key + "=" + extractResultMap[key][i] + ","
            printString += "}"
            print  "process:"+printString

    def buildData(self,extractResultMap):
        judgment={"type":"object","title":"裁判文书"}
        properties={}
        primarySize = len(extractResultMap["case_name"])
        for i in range(0, primarySize):
            for key in extractResultMap:
                properties[key]=extractResultMap[key][i]
        judgment["properties"]=properties
        return judgment

if __name__ == "__main__":
    worker = SupremeCourtJudgmentDetailWorker()
    worker()
