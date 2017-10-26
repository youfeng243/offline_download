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

max_retry = 3
timeout = 40
host = "http://www.lzcourt.org:8090/"
basic_url = "http://www.lzcourt.org:8090/publiclist.aspx?fymc=&ajlb=C27383272A46EB16746AC48B10DCC2BE&type=16F35C1673B49CD5"


class Lz_zhixing(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.bean_client = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.province = "甘肃省"
        self.city = "兰州"
        self.data = {
            "__EVENTTARGET": "tbGoPage",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": "/wEPDwULLTIxMDA1Mjc0MDgPZBYCAgEPZBYCAgQPZBYCAgEPZBYiAgEPDxYCHgRUZXh0BQUxNDUyMmRkAgMPDxYCHwAFAzYzMmRkAgUPDxYGHwAFAjw8HgtDb21tYW5kTmFtZQUBMx4HVmlzaWJsZWdkZAIHDw8WBh8ABQExHwEFATEfAmhkZAIJDw8WBB8ABQMuLi4fAmhkZAILDw8WBh8ABQEwHwEFATAfAmhkZAINDw8WBh8ABQExHwEFATEfAmdkZAIPDw8WBh8ABQEyHwEFATIfAmdkZAIRDw8WBh8ABQEzHwEFATMfAmdkZAITDw8WBh8ABQE0HwEFATQeB0VuYWJsZWRoZGQCFQ8PFgQfAAUBNR8BBQE1ZGQCFw8PFgQfAAUBNh8BBQE2ZGQCGQ8PFgQfAAUBNx8BBQE3ZGQCGw8PFgQfAAUBOB8BBQE4ZGQCHw8PFgQfAAUDNjMyHwEFAzYzMmRkAiEPDxYEHwAFAj4+HwEFATVkZAIjDw8WAh8ABQE0ZGRk43Fm/Rx7+lUjfXTylp4U4ROSH6w=",
            "__VIEWSTATEGENERATOR": "7B205B14",
            "__EVENTVALIDATION": "/wEWEAKgm9DFAQLYm/LeDwL99O8KAove7eAHArPH37cLAtazu7sHApy30OkNApy35MQGApy3qLMMApy3gP0KApy3lNgDApy32MYJApy37KECArHht48JArXh844KAs7M/dkLgCi8MFcflO1f9cUOGPpibZieb4U=",
            "hdPageIndex": "1",
            "hf_fymc": "",
            "hf_ajlb": "C27383272A46EB16746AC48B10DCC2BE",
            "hf_type": "16F35C1673B49CD5",
            "tbGoPage": ""
        }
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }

    def extract_detail_link(self, response, session):
        pq = PyQuery(response.text, parser="html")
        a = pq.find("li.datas")
        if a is None or a == "":
            return None
        for i in range(0, len(a)):
            title = a.eq(i).find("p.ptitle").text()
            detail_url = host + a.eq(i).find("a").attr("href")
            url = detail_url.replace(" ", "")
            if "" == url:
                continue
            try_count = 0
            while try_count < max_retry:
                try_count += 1
                try:
                    response = session.get(url, timeout=timeout)
                    if response is not None and response.status_code == 200:
                        self.extract_pdf_link(response, title, url)
                        break
                except requests.RequestException as e:
                    self.logger.error("访问详情页{}网络错误".format(url))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问详情页{}未知的错误".format(url))
                    self.logger.exception(e)
            if try_count >= max_retry:
                self.logger.error("{}次重试失败,跳过{}".format(max_retry, url))
                session.proxies = self.get_proxy()

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
        url = basic_url
        session = requests.session()
        session.proxies = self.get_proxy()
        pages = self.get_pages(url, session)
        if pages < 1:
            self.logger.error("获取页码失败")
            return
        for pageIndex in xrange(1, pages+1):
            self.data["tbGoPage"] = str(pageIndex)
            try_count = 0
            while try_count < max_retry:
                try_count += 1
                try:
                    response = session.post(url=url, timeout=timeout, data=self.data)
                    if response is not None and response.status_code == 200:
                        self.extract_detail_link(response, session)
                        break
                except requests.RequestException as e:
                    self.logger.error("访问列表页第{}页网络错误".format(pageIndex))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问列表页第{}页未知的错误".format(pageIndex))
                    self.logger.exception(e)

            if try_count >= max_retry:
                self.logger.error("{}次重试失败,跳过本页:{}".format(max_retry, pageIndex))
                session.proxies = self.get_proxy()
                # 返回类型为int

    def get_pages(self, url, session):
        try_count = 0
        while try_count < 3:
            try_count += 1
            try:
                response = session.post(url, timeout=timeout)
                if response is not None and response.status_code == 200:
                    pq = PyQuery(response.text, parser="html")
                    pages = pq.find("span#lbPageCount").text()
                    if pages is not None and pages != "":
                        return int(pages)
            except requests.RequestException as e:
                self.logger.error("访问页码出现网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问页码出现未知的错误")
                self.logger.exception(e)
        return 0

    # 返回类型为字符串
    def get_proxy(self):
        all_ip = self.all_ip
        ip = all_ip[random.randint(0, len(all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip


if __name__ == "__main__":
    worker = Lz_zhixing()
    worker()
