# -*- coding:UTF-8 -*-

# !/usr/bin/env python

# @Author  tx
# @Date    2017-8.18
import json
import random
import re
import sys

import pymongo
import requests
from pyquery import PyQuery

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from sites.poc_test.mongo_config import TestDataDB

from sites.common import staticproxy

from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase

basic_url = "http://www.gdebidding.com/searchGdmeetc.jspx?pageNo={}&queryTitle=%E5%B9%BF%E4%B8%9C%E7%9C%81%E4%BF%A1%E7%94%A8%E5%90%88%E4%BD%9C%E6%B8%85%E7%AE%97&channelId=67"
host = "http://www.gdebidding.com"
viewhost = "http://www.gdebidding.com/content_view.jspx?contentId={}"
max_retry = 3
timeout = 40

db_save = pymongo.MongoClient(TestDataDB.MONGODB_SERVER, TestDataDB.MONGODB_PORT)[TestDataDB.MONGODB_DB]
db_save.authenticate(TestDataDB.MONGO_USER, TestDataDB.MONGO_PSW)


class HfCredit(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beans_client = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }
        self.database = TestDataDB()

    def send_data(self, url, name, date):
        extract_data = {
            "topic": "registration_company",
            "company": name,
            "province": "安徽",
            "city": "安徽合肥",
            "registered_date": date,
            "_site_record_id": "hfcredit.gov.cn",
            "url": url
        }
        self.beans_client.put("offline_crawl_data", json.dumps(extract_data))

    # 在call的时候调用这个函数
    def start(self):

        session = requests.session()
        session.headers = self.headers
        pages = self.get_pages(session)
        if pages < 1:
            return
        for i in range(1, pages + 1):
            session.proxies = self.get_proxy()
            url = basic_url.format(i)
            try_count = 0
            while try_count < max_retry:
                try_count += 1
                try:
                    resp = session.get(url=url, timeout=timeout)
                    if resp is None or resp.status_code != 200 or len(resp.text) <= 0:
                        session.proxies = self.get_proxy()
                        continue
                    pq = PyQuery(resp.text, parser="html")
                    details = pq.find("table.pn-ltable").find("tr")
                    for j in xrange(1, len(details)):
                        publish_date = details.eq(j).find("td").eq(2).text()
                        detail_url = details.eq(j).find("td").eq(1).find("a").attr("href")
                        detail_url = host + detail_url
                        self.parse(detail_url, publish_date, session)
                    break
                except requests.RequestException as e:
                    self.logger.error("访问第{}页网络错误".format(i))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问第{}页未知的错误".format(i))
                    self.logger.exception(e)
            if try_count >= max_retry:
                self.logger.error("{}次访问第{}重试失败".format(max_retry, i))
                session.proxies = self.get_proxy()

    def parse(self, url, publish_date, session):

        try_count = 0
        while try_count < max_retry:
            try_count += 1
            try:
                resp = session.get(url, timeout=timeout)
                if resp is None or resp.status_code != 200 or len(resp.text) <= 0:
                    session.proxies = self.get_proxy()
                    continue
                pq = PyQuery(resp.text, parser="html")
                title = pq.find("h1").text()
                author = pq.find("div.padding-big").find("div").eq(0).text()
                author = re.findall(u"作者：(.*) ", author)[0]
                views = self.get_views(url, session)
                content = pq.find("div.padding-big").find("span").text()
                data = {
                    "title": title,
                    "author": author,
                    "views": views,
                    "publish_date": publish_date,
                    "content": content

                }
                print title
                db_save[TestDataDB.MONGODB_COLLECTION].save(data)
                break

            except requests.RequestException as e:
                self.logger.error("访问详情页网络错误,url为{}".format(url))
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问详情页未知的错误,url为{}".format(url))
                self.logger.exception(e)

        if try_count >= max_retry:
            self.logger.error("访问详情页{}次重试失败,url为:".format(max_retry, url))
            session.proxies = self.get_proxy()

    def get_proxy(self):
        ip = self.all_ip[random.randint(0, len(self.all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip

    def get_pages(self, session):
        url = basic_url.format(1)
        try_count = 0
        while try_count < max_retry:
            try_count += 1
            try:
                resp = session.get(url=url, timeout=timeout)
                if resp is None or resp.status_code != 200 or len(resp.text) <= 0:
                    session.proxies = self.get_proxy()
                    continue
                pq = PyQuery(resp.text, parser="html")
                pages = pq.find("td.pn-sp").text()
                pages = re.findall(r"(\d{2,4})", pages)[0]
                return int(pages) / 20 + 1
            except requests.RequestException as e:
                self.logger.error("访问第1页网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问第1页未知的错误")
                self.logger.exception(e)
        return 0

    def get_views(self, url, session):
        count = 0
        content_id = re.findall(r"(\d+)", url)[0]
        view_url = viewhost.format(content_id)
        while count < max_retry:
            count += 1
            try:
                resp = session.get(view_url, timeout=timeout)
                if resp is None or resp.status_code != 200 or len(resp.text) <= 0:
                    continue
                views = resp.text
                views = views.split(",")[0].replace("[", "")

                return int(views)
            except requests.RequestException as e:
                self.logger.error("获取{}的浏览数网络错误".format(url))
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("获取{}的浏览数未知的错误".format(url))
                self.logger.exception(e)
        if count >= max_retry:
            self.logger.error("获取{}的浏览数网络错误".format(url))


if __name__ == "__main__":
    worker = HfCredit()
    worker()
