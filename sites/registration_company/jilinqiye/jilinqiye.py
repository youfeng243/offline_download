#!/usr/bin/env python
# encoding: utf-8
# -*- coding:UTF-8 -*-


import json
import sys

from conf.m_settings import store_company

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase
import requests

reload(sys)
sys.setdefaultencoding('utf8')

max_retry = 3
timeout = 40
basic_url = "http://36.48.62.24:8704/DataQuery/company/list.json"


class JiLin(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = "吉林省"
        self.city = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }
        self.params = {
            "cxnr": "",
            "cxfw": "QYMC-",
            "fddbr": "",
            "szdq": "",
            "hylx": "",
            "ztlx": "",
            "page": "",
            "pageSize": "15",
        }

    def send_data(self, url, name):
        name = name.replace(" ", "")

        province = "jilin"
        store_company(province, name)

    def start(self):
        session = requests.session()
        session.headers = self.headers
        session.proxies = self.get_proxy()
        pages = self.get_pages(session)
        if pages < 1:
            self.logger.error("获取页码失败")
            return
        for i in range(1, pages):
            self.params["page"] = str(i)
            session.params = self.params
            session.headers = self.headers
            try_cnt = 0
            while try_cnt < max_retry:
                try_cnt += 1
                try:
                    resp = session.post(url=basic_url, timeout=timeout)
                    if resp is not None and resp.status_code == 200 and len(resp.text) > 0:
                        notes = json.loads(resp.text).get("list")
                        for note in notes:
                            name = note["qymc"]
                            self.send_data(basic_url, name)
                            self.logger.info("成功获取{0}下{1}".format(basic_url, name))
                        break
                except requests.RequestException as e:
                    self.logger.error("访问第{}页网络错误".format(i))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问第{}页未知的错误".format(i))
                    self.logger.exception(e)
            if try_cnt >= max_retry:
                self.logger.error("{}次重试失败...page = {}".format(max_retry, i))
                session.proxies = self.get_proxy()

    def get_pages(self, session):
        self.params["page"] = 1
        session.params = self.params
        count = 0
        while count < max_retry:
            count += 1
            try:
                resp = session.post(url=basic_url, timeout=timeout)
                if resp is None or resp.status_code != 200 or len(resp.text) <= 0:
                    session.proxies = self.get_proxy()
                    continue

                pages = int(json.loads(resp.text).get("pageCount"))
                return pages
            except requests.RequestException as e:
                self.logger.error("访问第1页网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问第1页未知的错误")
                self.logger.exception(e)
        return 0


if __name__ == "__main__":
    worker = JiLin()
    worker()
