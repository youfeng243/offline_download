# coding=utf-8
# !/usr/bin/env python
import random
import sys

import requests
from pyquery import PyQuery

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
from sites.common import staticproxy

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
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')

    def send_data(self, url, name, date):
        name = name.replace(" ", "")
        extract_data = {
            "topic": "registration_company",
            "company": name,
            "province": "guangdong",
            "city": "",
            "registered_date": date,
            "_site_record_id": "wsnj.gdgs.gov.cn",
            "url": url
        }

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

    def get_proxy(self):
        ip = self.all_ip[random.randint(0, len(self.all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip


if __name__ == "__main__":
    worker = GD()
    worker()
