# -*- coding:UTF-8 -*-

# !/usr/bin/env python
# 山东省工商局登记办理业务查询
# @Author  clevertang
# @Date    2017-7.12
import sys

from pyquery import PyQuery

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from conf.m_settings import store_company

from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase
import requests, sys

reload(sys)
sys.setdefaultencoding('utf8')

basic_url = "http://218.57.139.23:8090/iaicweb/xxcx/doqylccx.jsp?start={}"
max_retry = 3
timeout = 40


class Sd(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = "山东"
        self.city = ""

    def send_data(self, url, name, date):
        name = name.replace(" ", "")
        province = "shandong"
        store_company(province, name)

    def start(self):
        session = requests.session()
        session.proxies = self.get_proxy()
        pages = self.get_pages(session)
        if pages < 1:
            self.logger.error("获取列表页失败")
            return
        for i in range(0, pages):
            url = basic_url.format(10 * i)
            try_cnt = 0
            while try_cnt < max_retry:
                try_cnt += 1
                try:
                    resp = session.get(url, timeout=timeout)
                    if resp is not None and resp.status_code == 200:
                        detail_result = resp.content.decode("gbk")
                        detail_pq_result = PyQuery(detail_result, parser='html')
                        things = detail_pq_result.find('table').eq(3).find('tr')
                        for j in xrange(1, 11):
                            name = things.eq(j).find('td').eq(1).text()
                            date = things.eq(j).find('td').eq(2).text()
                            if name == "" or name is None or "下一页" in name:
                                continue
                            self.send_data(url, name, date)
                            self.logger.info("成功获取{0}下{1},注册时间为:{2}".format(url, name, date))
                        break
                except requests.RequestException as e:
                    self.logger.error("获取列表页第{}页网络错误".format(i))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error("访问列表页{}出现未知的错误".format(i))

            if try_cnt >= max_retry:
                self.logger.error("{}次重试失败...page = {}".format(max_retry, i))
                session.proxies = self.get_proxy()

    def get_pages(self, session):
        count = 0
        while count < max_retry:
            count += 1
            try:
                resp = session.get(basic_url.format(0), timeout=timeout)
                if resp is not None and resp.status_code == 200:
                    detail_result = resp.content.decode("gbk")
                    detail_pq_result = PyQuery(detail_result, parser='html')
                    things = detail_pq_result.find('table').eq(3).find('tr')
                    pages = things.eq(12).find('font').eq(6).text()
                    return int(pages) / 10 + 1
            except requests.RequestException as e:
                self.logger.error("访问第一页网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问第一页出现未知的错误")
                self.logger.exception(e)
        return 0


if __name__ == "__main__":
    worker = Sd()
    worker()
