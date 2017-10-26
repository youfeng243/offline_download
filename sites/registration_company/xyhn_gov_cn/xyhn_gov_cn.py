#!/usr/bin/env python
# encoding: utf-8
# -*- coding:UTF-8 -*-


import json
import random
import sys

from conf.m_settings import store_company
from sites.common import util

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
from sites.common import staticproxy

from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase
import requests

# reload(sys)
# sys.setdefaultencoding('utf8')

basic_url = "http://www.xyhn.gov.cn/CMSInterface/cms/getCreditCodeListByWs"
max_retry = 3
timeout = 40


class HeNan(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = "河南省"
        self.city = ""
        self.headers = {
            "Host": "www.xyhn.gov.cn",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0',
            'Accept': 'application/json, text/javascript, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'http://www.xyhn.gov.cn/ca/20160707000023.htm',
            'Cookie': 'JSESSIONID=D8C9623EFA9DD2009BDAC09085719441; JSESSIONID=D97B058748F596B60535F9B24B7BF9D0; yunsuo_session_verify=f9a5662716d6413b2580a4041ccadde3; nS_wcI_5f=ynweZn7arWzQoLXGytgXtfdSUASLZfj0NWhxBw==',
            'Connection': 'keep-alive'
        }
        self.data = {
            "pagesize": "20",
            "codeType": "1",
            "page": ""
        }
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')

    def send_data(self, url, name, date):
        name = name.replace(" ", "")
        extract_data = {
            "topic": "registration_company",
            "company": name,
            "province": "henan",
            "city": "",
            "registered_date": date,
            "_site_record_id": "xyHeNan.gov.cn",
            "url": url
        }

        province = "henan"
        store_company(province, name)

    def start(self):
        session = requests.session()
        session.proxies = self.get_proxy()
        session.headers = self.headers
        pages = self.get_pages(session)
        if pages < 1:
            self.logger.error("获取页码失败")
            return
        for i in range(1, pages):
            self.data["page"] = str(i)
            try_cnt = 0
            while try_cnt < max_retry:
                try_cnt += 1
                try:
                    resp = session.post(url=basic_url, timeout=timeout, data=self.data)
                    if resp is not None and resp.status_code == 200:
                        notes = json.loads(resp.text).get("data")["dataList"]
                        for note in notes:
                            name = note["QYMC"]
                            date = note["RECEIVEDATE"]
                            self.send_data(basic_url, name, date)
                            self.logger.info("成功获取{}注册时间为:{}".format(name, date))
                        break
                except requests.RequestException as e:
                    self.logger.error("获取列表页第{}页网络错误".format(i))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问列表页{}出现未知的错误".format(i))
                    self.logger.exception(e)
            if try_cnt >= max_retry:
                self.logger.error("{}次重试失败...page = {}".format(max_retry, i))
                session.proxies = self.get_proxy()

    def get_pages(self, session):
        self.data["page"] = "1"
        count = 0
        while count < max_retry:
            count += 1
            try:
                resp = session.post(url=basic_url, timeout=timeout, data=self.data)
                if resp is not None and resp.status_code == 200:
                    pages = json.loads(resp.text).get("data")["pageCount"]
                    return int(pages)
            except requests.RequestException as e:
                self.logger.error("访问第一页网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问第一页出现未知的错误")
                self.logger.exception(e)
        return 0

    def get_proxy(self):
        ip = self.all_ip[random.randint(0, len(self.all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip


if __name__ == "__main__":
    worker = HeNan()
    worker()
