# -*- coding:UTF-8 -*-

# !/usr/bin/env python
# 访问某些页面时数据不存在,出现报错正常,通过异常处理重试失败后选择跳过
import re
import sys

import requests
from pyquery import PyQuery

from conf.m_settings import store_company

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase

max_retry = 3
timeout = 40
basic_url = "http://www.sgs.gov.cn/shaic/dengjiBulletin!toNzsl.action"


class SH(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = "上海"
        self.city = "上海"
        self.headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
                        "Host": "www.sgs.gov.cn",
                        "Accept - Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Accept - Encoding": "gzip, deflate",
                        "Connection": "keep-alive",
                        "Upgrade - Insecure - Requests": "1",
                        "Cache - Control": "max-age=0"
                        }

    def send_data(self, url, name, date):
        name = name.replace(" ", "")

        province = "shanghai"
        store_company(province, name)

    # 在call的时候调用这个函数
    def start(self):
        session = requests.session()
        session.headers = self.headers
        session.proxies = self.get_proxy()
        pages = self.get_pages(session) / 20 + 1
        if pages < 2:
            self.logger.error("获取页码失败")
            return
        for i in xrange(1, pages):
            try_cnt = 0
            data = {"pageno": i}
            while try_cnt < max_retry:
                try_cnt += 1
                try:
                    response = requests.post(url=basic_url, data=data, timeout=timeout)
                    self.logger.info("POST-SUCCESS:{}\t{}".format(basic_url, response.status_code))
                    if response is None or response.status_code != 200:
                        session.proxies = self.get_proxy()
                        continue
                    pq_result = PyQuery(response.text, parser='html')
                    things = pq_result.find('table.tgList').find('tr')
                    for j in xrange(1, len(things)):
                        name = things.eq(j).find('td').eq(0).text()
                        date = things.eq(j).find('td').eq(2).text()
                        self.send_data(basic_url, name, date)
                        self.logger.info("成功获取{0}下{1}".format(basic_url, name))
                    break
                except requests.RequestException as e:
                    self.logger.error("访问列表页第{}页网络错误".format(i))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问列表页第{}页出现未知的错误".format(i))
                    self.logger.exception(e)
            if try_cnt >= max_retry:
                self.logger.error("{}次重试失败...page = {}".format(max_retry, i))
                session.proxies = self.get_proxy()

    def get_pages(self, session):
        try_count = 0
        while try_count < max_retry:
            try_count += 1
            try:
                data = {
                    "pageno": 1
                }
                resp = requests.post(url=basic_url, data=data, timeout=timeout)
                if resp is None or resp.status_code != 200:
                    session.proxies = self.get_proxy()
                    continue
                pq_result = PyQuery(resp.text, parser='html')
                page = pq_result.find('table.page').find("td").eq(1).text()
                pages = int(re.findall(r"\d+", page)[0])
                return pages

            except requests.RequestException as e:
                self.logger.error("访问第一页网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问第一页出现未知的错误")
                self.logger.exception(e)
        return 0


if __name__ == "__main__":
    worker = SH()
    # worker.send_data()
    worker()
