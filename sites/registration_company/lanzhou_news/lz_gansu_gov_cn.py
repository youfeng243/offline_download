#!/usr/bin/env python
# encoding: utf-8

import json
import random
import re
import sys
import time

sys.path.append("..")
sys.path.append("../..")
from sites.common import staticproxy

from pyquery import PyQuery

from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase
import requests, sys

reload(sys)
sys.setdefaultencoding('utf8')


class Lzgansugov(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = "兰州"
        self.city = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Upgrade-Insecure-Requests": "1",
        }
        self.params = {
            "col": "1",
            "appid": "1",
            "webid": "1",
            "path": "/",
            "columnid": "",
            "sourceContentType": "1",
            "unitid": "4702",
            "webname": "兰州市政府",
            "permissiontype": "0"
        }
        self.all_ip = staticproxy.get_all_proxie()

    def sendData(self, url, name, date, content):
        extract_data = {
            "publish_time": date,
            "source": "Lzgansugov",
            "url": url,
            "summary": content,
            "title": name,
            "topic": "兰州政府新闻",
            "_site_record_id": "lz.gansu.gov.cn",
        }

        self.beanstalkclient.put("offline_crawl_data", json.dumps(extract_data))

    def start(self):
        basicurl = "http://www.lz.gansu.gov.cn/module/web/jpage/dataproxy.jsp?startrecord={}&endrecord={}&perpage=15"
        session = requests.session()
        all_list = ["122", "123", "127", "128", "129"]
        session.proxies = self.getproxie()
        for a in all_list:
            self.params["columnid"] = a
            pagenum = self.getpagenum(a)
            for j in range(1, pagenum):
                session.headers = self.headers
                url = basicurl.format((j - 1) * 45 + 1, 45 * j)

                session.params = self.params
                try_cnt = 0
                while try_cnt < 3:
                    try:
                        try_cnt += 1
                        resp = session.post(url)
                        if resp is not None and resp.status_code == 200:
                            detail_pq_result = PyQuery(resp.text, parser='html')
                            allnotes = detail_pq_result.find("a")

                            for i in xrange(0, len(allnotes)):
                                name = allnotes.eq(i).attr("title")
                                url = allnotes.eq(i).attr("href")
                                date = re.findall(r"\d{4}/\d+/\d+", url)[0]
                                content, url = self.parse_content(url)
                                self.sendData(url, name, date, content)
                                self.logger.info("成功获取{0}下{1}".format(url, name))
                            break
                    except Exception as e:
                        self.logger.error("网络错误...")
                        self.logger.exception(e)
                if try_cnt >= 3:
                    self.logger.error("三次重试失败...")
                    proxie = self.getproxie()
                    session.proxies = proxie

    def getpagenum(self, a):
        s = requests.session()
        self.params["columnid"] = a
        s.params = self.params
        s.headers = self.headers
        count = 0
        while count < 3:
            try:
                resp = s.post(
                    "http://www.lz.gansu.gov.cn/module/web/jpage/dataproxy.jsp?startrecord=46&endrecord=90&perpage=15")
                if resp is not None and resp.status_code == 200:
                    detail_pq_result = PyQuery(resp.content, parser='html')
                    pagenum = detail_pq_result.find("totalrecord").text()
                    return int(pagenum) / 45 + 1
            except Exception as e:
                self.logger.error("网络错误...")
                self.logger.exception(e)
        if count >= 3:
            self.logger.error("三次重试失败...")

    def getproxie(self):
        all_ip = self.all_ip
        ip = all_ip[random.randint(0, len(all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip

    def parse_content(self, url):
        url = "http://www.lz.gansu.gov.cn/" + url
        try_count = 0
        while try_count < 3:
            try:
                resp = requests.get(url)
                if resp is not None and resp.status_code == 200:
                    pq = PyQuery(resp.content, parser="html")
                    content = pq.find("div#zoom").text()
                    return content, url

            except Exception as e:
                self.logger.error("网络错误...")
                self.logger.exception(e)
                time.sleep(3)
        if try_count >= 3:
            self.logger.error("三次重试失败...")


if __name__ == "__main__":
    worker = Lzgansugov()
    worker()
