#!/usr/bin/env python
# encoding: utf-8
# 只有一页列表页

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

host = "http://www.lngs.gov.cn"
basic_url = "http://www.lngs.gov.cn/ecdomain/framework/lngs/anlfaiemapdbbbofiohcpgjmokfngfef.jsp"
max_retry = 3
timeout = 40


class Ln(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beans_client = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = "辽宁省"
        self.city = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }
        self.all_ip = staticproxy.get_all_proxie()

    def send_data(self, url, name, date):
        name = name.replace(" ", "")
        extract_data = {
            "topic": "registration_company",
            "company": name,
            "province": "辽宁",
            "city": "",
            "registered_date": date,
            "_site_record_id": "lngs.gov.cn",
            "url": url
        }
        self.beans_client.put("offline_crawl_data", json.dumps(extract_data))

    def start(self):
        session = requests.session()
        session.headers = self.headers
        session.proxies = self.get_proxy()
        try_cnt = 0
        while try_cnt < max_retry:
            try_cnt += 1
            try:
                resp = session.get(url=basic_url, timeout=timeout)
                if resp is not None and resp.status_code == 200:
                    detail_pq_result = PyQuery(resp.text, parser='html')
                    things = detail_pq_result.find('div.anou_nscrl').find("a")
                    for j in xrange(0, len(things)):
                        detail_url = things.eq(j).attr("href")
                        self.parse(detail_url, session)
                    break
            except requests.RequestException as e:
                self.logger.error("访问列表页第网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问列表页第出现未知的错误")
                self.logger.exception(e)

    def parse(self, url, session):
        url = host + url
        try_count = 0
        while try_count < max_retry:
            try_count += 1
            try:
                resp = session.get(url=url, timeout=timeout)
                text = re.findall(r'(<br>.*<br>)', resp.text)[0]
                all_list = text.split("<br>")
                for i in xrange(1, len(all_list) - 1):
                    date = all_list[i].split("\t")[0]
                    name = all_list[i].split("\t")[2]
                    self.logger.info("成功获取{},注册时间为{}".format(name,date))
                    self.send_data(url, name, date)
                break
            except requests.RequestException as e:
                self.logger.error("访问详情页{}网络错误".format(url))
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问详情页{}未知的错误".format(url))
                self.logger.exception(e)

        if try_count >= max_retry:
            self.logger.error("{}次重试访问详情页{}失败".format(max_retry, url))
            session.proxies = self.get_proxy()

    def get_proxy(self):
        ip = self.all_ip[random.randint(0, len(self.all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip


if __name__ == "__main__":
    worker = Ln()
    worker()
