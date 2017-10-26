#!/usr/bin/env python
# encoding: utf-8
# -*- coding:UTF-8 -*-
# 本网站只记录最近五天的企业信息,所以手动设置一个pagenum,出现错误提示解析列表页第四页失败很正常

import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from conf.m_settings import store_company
from sites.common.tx_session import proxy_session

from pyquery import PyQuery

from libs.loghandler import getLogger

from libs.taskbase import TaskBase
import sys

reload(sys)
sys.setdefaultencoding('utf8')
basic_url = "http://www.gzaic.org.cn/ywlcListData.jsp?page={}"
max_retry = 3
timeout = 30


class Gz(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }

    def send_data(self, url, name, date):
        name = name.replace(" ", "")

        province = "guizhou"
        store_company(province, name)

    def start(self):
        session = proxy_session()
        for i in range(1, 5):
            url = basic_url.format(i)
            resp = None
            try:
                resp = session.post(url, timeout=timeout, headers=self.headers)
            except Exception as e:
                self.logger.exception(e)
            if resp is None or resp.status_code != 200:
                session.proxies = self.get_proxy()
                continue
            detail_pq_result = PyQuery(resp.text, parser='html')
            things = detail_pq_result.find('tr')
            if not isinstance(things, list) or len(things) <= 1:
                self.logger.error("解析列表页第{}页失败".format(i))
            for j in xrange(1, len(things)):
                name = things.eq(j).find("td").eq(0).text()
                date = things.eq(j).find("td").eq(3).text()

                self.send_data(url, name, date)
                self.logger.info("成功获取{0}下{1}".format(url, name))


if __name__ == "__main__":
    worker = Gz()
    worker()
