#!/usr/bin/env python
# -*- coding:utf-8 -*-


import json
import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from conf.m_settings import store_company
from sites.common.tx_session import proxy_session

from pyquery import PyQuery

from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase
import sys

reload(sys)
sys.setdefaultencoding('utf8')
max_retry = 3
timeout = 40
basic_url = "http://www.creditjx.gov.cn/DataQuery/company/listNew.json"
detail = "http://www.creditjx.gov.cn/DataQuery/company/infoNew/{}/1"


class JX(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }
        self.params = {
            "cxfs": 0,
            "cxfw": "QYMC-",
            "cxlx": 1,
            "cxnr": "",
            "hylx": "",
            "page": "",
            "pageSize": 15,
            "szdq": "",
            "ztlx": ""
        }

    def send_data(self, url, name, date):
        name = name.replace(" ", "")
        province = "jiangxi"
        store_company(province, name)

    def start(self):
        url = basic_url
        session = proxy_session()
        session.headers = self.headers
        pages = self.get_pages(session)
        if pages < 1:
            self.logger.error("获取页码失败")
            return
        for i in xrange(1, pages):
            self.params["page"] = i
            session.params = self.params
            resp = None
            try:
                resp = session.post(url, timeout=timeout)
            except Exception as e:
                self.logger.error("访问列表页{}出错".format(url))
                self.logger.exception(e)
            data = json.loads(resp.text)
            data = data["list"]
            for j in data:
                detail_url = j["xybsm"]
                detail_url = detail.format(detail_url)
                self.parse(detail_url, session)

    def parse(self, url, session):
        resp = session.get(url, timeout=timeout)
        pq = PyQuery(resp.text, parser="html")
        name = pq.find("table#tblQyBaseInfo").find("tr").eq(0).find("td").eq(0).text()

        date = pq.find("table#tblQyBaseInfo").find("tr").eq(4).find("td").eq(0).text()
        self.logger.info("{}:{}".format(name, date))
        self.send_data(url, name, date)

    def get_pages(self, session):
        self.params["page"] = 1
        session.params = self.params

        resp = session.post(basic_url, timeout=timeout)
        if resp is not None and resp.status_code == 200:
            data = json.loads(resp.text)
            pages = data["pageCount"]
            return int(pages)
        return 0


if __name__ == "__main__":
    worker = JX()
    worker()
