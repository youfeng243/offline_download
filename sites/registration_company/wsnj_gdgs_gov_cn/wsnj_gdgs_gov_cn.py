# coding=utf-8
# !/usr/bin/env python
import sys

import requests
from pyquery import PyQuery

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from conf.m_settings import store_company

from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase

# reload(sys)
# sys.setdefaultencoding('utf8')

max_retry = 3
timeout = 40
basic_url = "http://wsnj.gdgs.gov.cn/aiccps/bizhtml/biz03_{}.html"


class GD(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = "广东"
        self.city = ""

    def send_data(self, url, name, date):
        name = name.replace(" ", "")

        province = "guangdong"
        store_company(province, name)

    # 在call的时候调用这个函数
    def start(self):
        session = requests.session()
        session.proxies = self.get_proxy()
        for i in xrange(1, 11):
            url = basic_url.format(i)
            try_count = 0
            while try_count < max_retry:
                try_count += 1
                try:
                    result = requests.get(url=url, timeout=timeout).content
                    content = result.decode('gbk')
                    pq_result = PyQuery(content, parser='html')
                    things = pq_result.find('table.border')
                    for j in xrange(1, len(things)):
                        name = things.eq(j).find('td').eq(1).text().split('：')[1]
                        date = things.eq(j).find('td').eq(5).text().split('：')[1]
                        self.send_data(url, name, date)
                        self.logger.info("成功获取{0}下{1}".format(url, name))
                    break
                except requests.RequestException as e:
                    self.logger.error("获取列表页第{}页网络错误".format(i))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问列表页{}出现未知的错误".format(i))
                    self.logger.exception(e)
            if try_count >= max_retry:
                self.logger.error("访问详情页第{}页{}次重试失败".format(i, max_retry))
                session.proxies = self.get_proxy()


if __name__ == "__main__":
    worker = GD()
    worker()
