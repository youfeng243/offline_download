# -*- coding:UTF-8 -*-

# !/usr/bin/env python

# @Author  clevertang
# @Date    2017-7.12
import json
import random
import sys

import requests

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from sites.common import staticproxy

from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase

json_curl = "http://hfcredit.gov.cn/Credit/HFCreditImpl?method=xydmList&PageNum={}&temp=1499842281095"
max_retry = 3
timeout = 40


class HfCredit(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = "安徽省"
        self.city = "合肥"
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }

    def send_data(self, url, name, date):
        name = name.replace(" ", "")
        extract_data = {
            "topic": "registration_company",
            "company": name,
            "province": "anhui",
            "city": "安徽合肥",
            "registered_date": date,
            "_site_record_id": "hfcredit.gov.cn",
            "url": url
        }

    # 在call的时候调用这个函数
    def start(self):
        session = requests.session()
        session.headers = self.headers
        pages = self.get_pages(session)
        if pages < 1:
            return
        for i in range(1, pages):
            session.proxies = self.get_proxy()
            url = json_curl.format(i)
            try_count = 0
            while try_count < max_retry:
                try_count += 1
                try:
                    resp = session.get(url=url, timeout=timeout)
                    if resp is None or resp.status_code != 200 or len(resp.text) <= 0:
                        session.proxies = self.get_proxy()
                        continue
                    json_data = json.loads(resp.text)
                    rows = json_data.get("rows")
                    if rows is None or len(rows) <= 0:
                        continue
                    for a in rows:
                        name = a["MC"]
                        date = a["ZCRQ"]
                        self.send_data(url, name, date)
                        self.logger.info("成功获取{0}下{1}".format(url, name))
                    break
                except requests.RequestException as e:
                    self.logger.error("访问第{}页网络错误".format(i))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问第{}页未知的错误".format(i))
                    self.logger.exception(e)
            if try_count >= max_retry:
                self.logger.error("{}次访问第{}重试失败".format(max_retry, i))
                session.proxies = self.get_proxy()

    def get_proxy(self):
        ip = self.all_ip[random.randint(0, len(self.all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip

    def get_pages(self, session):
        try_count = 0
        while try_count < max_retry:
            try_count += 1
            try:
                resp = session.get(url=json_curl.format(1), timeout=timeout)
                if resp is None or resp.status_code != 200 or len(resp.text) <= 0:
                    session.proxies = self.get_proxy()
                    continue
                pages = json.loads(resp.text).get("total")
                if pages is None:
                    continue
                return pages / 10 + 1
            except requests.RequestException as e:
                self.logger.error("访问第1页网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问第1页未知的错误")
                self.logger.exception(e)
        return 0


if __name__ == "__main__":
    worker = HfCredit()
    worker()
