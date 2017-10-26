#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import random
import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
from pyquery import PyQuery

from sites.common import staticproxy

from libs.pdfparser import pdfparser

from conf import m_settings
from libs.fetcher import Fetcher
from libs.taskbase import TaskBase
from libs.loghandler import getLogger

max_retry = 3
timeout = 40
host = "http://www.lzcourt.org:8090/"
basic_url = "http://www.lzcourt.org:8090/publiclist.aspx?fymc=&{}&type=4F813CCBFE6A7793"

headMap = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
           "Accept-Language": "zh-CN,zh;q=0.8", "Cache-Control": "max-age=0",
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
           "Upgrade-Insecure-Requests": "1"}


class Lzcourtorg(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
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

    def extract_detail_link(self, response):
        pq = PyQuery(response.text, parser="html")
        a = pq.find("li.datas")
        for i in range(0, len(a)):
            title = a.eq(i).find("p.ptitle").text()
            detail_url = host + a.eq(i).find("a").attr("href")
            url = detail_url.replace(" ", "")
            # publishDate = a.eq(i).find("p.pdate").text()
            if "" == url:
                return
            try:
                response = self.fetcher.get(url, timeout=timeout)
                self.extract_pdf_link(response, title)
            except Exception as e:
                self.logger.error("访问pdf链接{}失败".format(url))
                self.logger.exception(e)

    def extract_pdf_link(self, response, title):

        parser = PyQuery(response.content, parser='html')

        try:
            link = parser.find("iframe").attr('src')
            if link is None or "" == link:
                return
            pdf_link = host + link
            filename = pdf_link.split('.pdf')[0].split('/')[-1] + ".pdf"
            data = self.fetcher.download_file(pdf_link, filename=filename)
            data['title'] = title
            extract_data = self.deal(data)
            if extract_data:
                self.logger.info("案件:{}".format(title))
                self.send_data(extract_data)
        except Exception as e:
            self.logger.error("访问详情页失败{}".format(title))
            self.logger.exception(e)

    def deal(self, data):
        try:
            text = pdfparser.pdf2txt(data['data'])
            extract_data = {}
            extract_data['case_name'] = data['title']
            extract_data['wenshu_content'] = text
            extract_data['_site_record_id'] = "lzcourt.org:8090"
            extract_data['source'] = "lzcourt.org.py"
            extract_data['url'] = data['sourceUrl']
            extract_data["topic"] = "judgement_wenshu"
        except Exception as e:
            self.logger.exception(e)
            extract_data = None

        return extract_data

    def send_data(self, extract_data):
        self.beanstalkclient.put("offline_crawl_data", json.dumps(extract_data)
                                 )

    def start(self):
        for a in ("ajlb=C27383272A46EB16746AC48B10DCC2BE", "ajlb=8BA7067622BA13777D80B99FDFB975A7",
                  "ajlb=CC257740F74056B454125AFA5B73264D",
                  "ajlb=03328C65D394048E2ADFF6863CC4EA22", "ajlb=E4D122FC71F333DA007E69E16B9EC534",
                  "ajlb=C9B6A2ADAD814CFA25AA57B0959359F2"):

            url = basic_url.format(a)
            pages = self.get_pages(url)
            if pages < 1:
                return
            for pageIndex in xrange(1, pages + 1):
                proxies = self.get_proxy()
                self.data["tbGoPage"] = str(pageIndex)
                fetcher = self.fetcher
                fetcher.proxies = proxies
                try:
                    response = fetcher.post(url, data=self.data, timeout=timeout)
                    self.extract_detail_link(response)
                except Exception as e:
                    self.logger.error("访问列表页{}失败".format(pageIndex))
                    self.logger.exception(e)

    def get_pages(self, url):
        if "ajlb=E4D122FC71F333DA007E69E16B9EC534" in url:
            return 1
        try:
            response = self.fetcher.post(url, timeout=timeout)
            pq = PyQuery(response.text, parser="html")
            pages = pq.find("span#lbPageCount").text()
            return int(pages)
        except Exception as e:
            self.logger.error("获取页码失败")
            self.logger.exception(e)
            return 0

    def get_proxy(self):
        all_ip = self.all_ip
        ip = all_ip[random.randint(0, len(all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip


if __name__ == "__main__":
    worker = Lzcourtorg()
    worker()
