#!/usr/bin/env python
# encoding: utf-8
# -*- coding:UTF-8 -*-

import json
import random
import re
import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from sites.common import staticproxy

from pyquery import PyQuery

from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase
import requests, sys

reload(sys)
sys.setdefaultencoding('utf8')

cookie_url = "http://www.zjgsj.gov.cn/baweb/show/shiju/gg.jsp?fenceid=95000000&queryType=6"
basic_url = "http://www.zjgsj.gov.cn/baweb/show/shiju/gg.jsp?fenceid=95000000&total=21548&queryType=6&pagenum={}&action=pagin&findWenhao=&findName="
max_retry = 3
timeout = 40


class ZhenJ(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beans_client = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = "江苏省"
        self.city = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')

    def send_data(self, url, name):
        name = name.replace(" ", "")
        extract_data = {
            "topic": "registration_company",
            "company": name,
            "province": "江苏",
            "city": "镇江",
            "registered_date": "",
            "_site_record_id": "sqgsj.gov.cn",
            "url": url
        }
        self.beans_client.put("offline_crawl_data", json.dumps(extract_data))

    def start(self):
        session = requests.session()
        session.headers = self.headers
        session.proxies = self.get_proxy()
        cookie, pages = self.get_cookie()
        if cookie is None or pages < 1:
            self.logger.error("初始化cookie,页码失败")
            return
        session.cookies = cookie
        for i in xrange(1, pages):
            url = basic_url.format(i)
            try_cnt = 0
            while try_cnt < max_retry:
                try_cnt += 1
                try:
                    resp = session.get(url, timeout=timeout)
                    if resp is not None and resp.status_code == 200:
                        detail_pq_result = PyQuery(resp.text, parser='html')
                        things = detail_pq_result.find('table[cellpadding="3"]').find("tr")
                        for j in xrange(1, len(things)):
                            name = things.eq(j).find("td").eq(0).text()
                            self.logger.info("成功获取:{}".format(name))
                            self.send_data(url, name)
                        break
                except requests.RequestException as e:
                    self.logger.error("访问第{}页网络错误,url为:{}".format(i, url))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问第{}页出现未知的错误,url为:{}".format(i, url))
                    self.logger.exception(e)
            if try_cnt >= max_retry:
                self.logger.error("{}次重试第{}页失败...".format(url, i))
                session.proxies = self.get_proxy()

    def get_proxy(self):
        all_ip = self.all_ip
        ip = all_ip[random.randint(0, len(all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip

    def get_cookie(self):
        session = requests.session()
        try_count = 0
        while try_count < max_retry:
            try_count += 1
            try:
                resp = session.get(cookie_url, timeout=timeout)
                if resp is None or resp.status_code != 200:
                    continue
                a = resp.cookies
                detail_pq_result = PyQuery(resp.content, parser='html')
                page = detail_pq_result.find("table[cellpadding='5']").find('td').text()
                pages = re.findall(r"\d{4}", page)[0]
                return a, int(pages)
            except requests.RequestException as e:
                self.logger.error("获取cookie,页码网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("获取cookie,页码出现未知的错误")
                self.logger.exception(e)
        return None, 0


if __name__ == "__main__":
    worker = ZhenJ()
    worker()
