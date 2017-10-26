#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import random
import sys

import requests

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
from pyquery import PyQuery
from sites.common import staticproxy
from conf import m_settings
from libs.fetcher import Fetcher
from libs.taskbase import TaskBase
from libs.loghandler import getLogger


class Lzcourt_zhixing(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.bean_client = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.province = "甘肃省"
        self.city = "兰州"
        self.params = {"__EVENTTARGET": "btnPage6",
                       "__EVENTARGUMENT": "",
                       "__LASTFOCUS": "",
                       "__VIEWSTATEGENERATOR": "7B205B14",
                       "hdPageIndex": "",
                       "hf_fymc": "",
                       "hf_ajlb": "C27383272A46EB16746AC48B10DCC2BE",
                       "hf_type": "16F35C1673B49CD5",
                       "tbGoPage": "",
                       "__EVENTVALIDATION": "/wEWDAKw+6S/DgLYm/LeDwL99O8KAove7eAHArPH37cLApy3gP0KApy3lNgDApy32MYJApy37KECArHht48JArXh844KAs7M/dkLGVfqZ+yh3IeKdW4c2xnCCXSD0VE=",
                       "__VIEWSTATE": "/wEPDwULLTIxMDA1Mjc0MDgPZBYCAgEPZBYCAgQPZBYCAgEPZBYgAgEPDxYCHgRUZXh0BQUxNDUyMmRkAgMPDxYCHwAFAzYzMmRkAgUPDxYGHwAFAjw8HgtDb21tYW5kTmFtZQUCMTIeB1Zpc2libGVnZGQCBw8PFgYfAAUBMR8BBQExHwJnZGQCCQ8PFgQfAAUDLi4uHwJnZGQCCw8PFgYfAAUBOR8BBQE5HwJnZGQCDQ8PFgYfAAUCMTAfAQUCMTAfAmdkZAIPDw8WBh8ABQIxMR8BBQIxMR8CZ2RkAhEPDxYGHwAFAjEyHwEFAjEyHwJnZGQCEw8PFgYfAAUCMTMfAQUCMTMeB0VuYWJsZWRoZGQCFQ8PFgQfAAUCMTQfAQUCMTRkZAIXDw8WBB8ABQIxNR8BBQIxNWRkAhkPDxYEHwAFAjE2HwEFAjE2ZGQCGw8PFgQfAAUCMTcfAQUCMTdkZAIfDw8WBB8ABQM2MzIfAQUDNjMyZGQCIQ8PFgQfAAUCPj4fAQUCMTRkZGRGp3Q10lCFz0lI7foNY71VP29fJg=="
                       }
        self.all_ip = staticproxy.get_all_proxie()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }
        self.host = "http://www.lzcourt.org:8090/"
        self.basicurl = "http://www.lzcourt.org:8090/publiclist.aspx?fymc=&ajlb=C27383272A46EB16746AC48B10DCC2BE&type=16F35C1673B49CD5"

    def extract_detail_link(self, response, session):
        pq = PyQuery(response.text, parser="html")
        a = pq.find("li.datas")
        if a is None or a == "":
            return None
        for i in range(0, len(a)):
            title = a.eq(i).find("p.ptitle").text()
            detail_url = self.host + a.eq(i).find("a").attr("href")
            url = detail_url.replace(" ", "")
            if "" == url:
                continue
            try_count = 0
            while try_count < 3:
                try:
                    try_count += 1
                    response = session.get(url)
                    if response is not None and response.status_code == 200:
                        self.extract_pdf_link(response, title, url)
                        break
                except requests.RequestException as e:
                    self.logger.error("网络错误")
                    self.logger.exception(e)
                    proxies = self.get_proxy()
                    if proxies is not None and proxies != "":
                        session.proxies = proxies
                except Exception as e:
                    self.logger.error("未知的错误")
                    self.logger.exception(e)
            if try_count >= 3:
                self.logger.error("三次重试失败,跳过")
                proxies = self.get_proxy()
                if proxies is not None:
                    session.proxies = proxies

    def extract_pdf_link(self, response, title, url):
        parser = PyQuery(response.content, parser='html')
        text = parser.find("table.splclist").find("tr")
        if text is None or text == "":
            return

        extract_data = {
            "case_state": text.eq(7).find("td").eq(1).text(),
            "court": text.eq(5).find("td").eq(1).text(),
            "case_date": text.eq(2).find("td").eq(3).text(),
            "i_name": text.eq(9).find("td").eq(1).text(),
            "party_card_num": "",
            "exec_money": text.eq(6).find("td").eq(3).text(),
            "max_money": text.eq(6).find("td").eq(3).text(),
            "sum_money": text.eq(6).find("td").eq(3).text(),
            "money_unit": "元",
            "province": "甘肃",
            "case_id": text.eq(1).find("td").eq(1).text(),
            "url": url,
            "source": "lanzhou_zhixing_info",
            "topic": "zhixing_info",
            "_site_record_id": "lzcourt.org:8090"
        }

        self.logger.info("案件:{}".format(title))
        self.send_data(extract_data)

    def send_data(self, extract_data):
        self.bean_client.put("offline_crawl_data", json.dumps(extract_data))

    def start(self):
        url = self.basicurl
        session = requests.session()
        proxies = self.get_proxy()
        session.headers = self.headers
        if proxies is None or proxies == "":
            return
        session.proxies = proxies
        pagenum = self.get_pagenum(url, session)
        if pagenum < 1:
            return
        for pageIndex in xrange(0, pagenum):
            self.params["hdPageIndex"] = str(pageIndex)
            try_count = 0
            while try_count < 3:

                try:
                    try_count += 1
                    response = session.post(url=url, params=self.params)
                    if response is not None and response.status_code == 200:
                        self.extract_detail_link(response, session)
                        break
                except requests.RequestException as e:
                    self.logger.exception(e)
                    self.logger.error("网络错误")
                    proxies = self.get_proxy()
                    if proxies is not None and proxies != "":
                        session.proxies = proxies
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error("未知的错误")

            if try_count >= 3:
                self.logger.error("三次重试失败,跳过本页:{}".format(pageIndex))
                proxies = self.get_proxy()
                if proxies is not None:
                    session.proxies = proxies

                    # 返回类型为int

    def get_pagenum(self, url, session):
        self.params["hdPageIndex"] = "1"
        session.params = self.params
        try_count = 0
        while try_count < 3:
            try:
                try_count += 1
                response = session.post(url, params=self.params)
                if response is not None and response.status_code == 200:
                    pq = PyQuery(response.text, parser="html")
                    pagenum = pq.find("span#lbPageCount").text()
                    if pagenum is not None and pagenum != "":
                        return int(pagenum)
            except requests.RequestException as e:
                self.logger.exception(e)
                self.logger.error("网络错误")
                proxies = self.get_proxy()
                if proxies is not None and proxies != "":
                    session.proxies = proxies
            except Exception as e:
                self.logger.exception(e)
                self.logger.error("未知的错误")

        if try_count >= 3:
            self.logger.error("三次重试获取页码数失败")
            return 0
        return 0

    # 返回类型为字符串
    def get_proxy(self):
        if self.all_ip is None:
            self.logger.error("获取ip失败")
            return ""
        all_ip = self.all_ip
        ip = all_ip[random.randint(0, len(all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip


if __name__ == "__main__":
    worker = Lzcourt_zhixing()
    worker()
