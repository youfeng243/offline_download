# -*- coding:UTF-8 -*-
# !/usr/bin/env python
# 只有一页
import sys

from conf.m_settings import store_company

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
from pyquery import PyQuery

from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase
import requests, sys

reload(sys)
sys.setdefaultencoding('utf8')

max_retry = 3
timeout = 40
basic_url = "http://zcj.hnaic.gov.cn/html/RegPlac/MoreList.html"
host = "http://zcj.hnaic.gov.cn/html/RegPlac/"


class HuNan(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = "湖南 "
        self.city = ""

    def send_data(self, url, name, date):
        name = name.replace(" ", "")

        province = "hunan"
        store_company(province, name)

    def start(self):
        session = requests.session()
        session.proxies = self.get_proxy()
        try_cnt = 0
        while try_cnt < max_retry:
            try_cnt += 1
            try:
                # 从根目录下获取详情url
                resp = session.get(basic_url, timeout=timeout)
                if resp is not None and resp.status_code == 200:
                    result = resp.content
                    content = result.decode('utf-8')
                    pq_result = PyQuery(content, parser='html')
                    things = pq_result.find('tbody').find('tr')
                    for i in xrange(0, len(things)):
                        detail = things.eq(i).find('a').attr("href")
                        detail_url = host + detail
                        self.parse_detail(session, detail_url)
                    break
            except requests.RequestException as e:
                self.logger.error("访问首页网络错误".format(i))
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问首页出现未知的错误".format(i))
                self.logger.exception(e)
        if try_cnt >= max_retry:
            self.logger.error("连续{}次访问首页失败:http://zcj.hnaic.gov.cn/html/RegPlac/MoreList.html".format(max_retry))

    def parse_detail(self, session, url):
        try_cnt = 0
        while try_cnt < max_retry:
            try_cnt += 1
            try:
                resp = session.get(url, timeout=timeout)
                if resp is not None and resp.status_code == 200:
                    detail_result = resp.content.decode("utf-8")
                    detail_pq_result = PyQuery(detail_result, parser='html')
                    things = detail_pq_result.find('tr')
                    for i in xrange(1, len(things)):
                        name = things.eq(i).find('td').eq(1).text()
                        date = things.eq(i).find('td').eq(2).text()
                        self.send_data(url, name, date)
                        self.logger.info("成功获取{0}下{1},注册时间为:{2}".format(url, name, date))
                    break
            except requests.RequestException as e:
                self.logger.error("获取详情页{}网络错误".format(url))
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问详情页{}出现未知的错误".format(url))
                self.logger.exception(e)
        if try_cnt >= max_retry:
            self.logger.error("连续{}次访问详情页失败:{}".format(max_retry, url))
            session.proxies = self.get_proxy()


if __name__ == "__main__":
    worker = HuNan()
    # worker.send_data()
    worker()
