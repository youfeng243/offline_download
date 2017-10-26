#!/usr/bin/env python
# encoding: utf-8



import json
import random
import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
from sites.common import staticproxy

from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase
import requests, sys

reload(sys)
sys.setdefaultencoding('utf8')

max_retry = 3
timeout = 40
basic_url = "http://wljg.egs.gov.cn:7777/gsjgw/web/dzbs/findWljjztByPage.do?pageSize=10&pageIndex={}"


class HuBei(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beans_client = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = "湖北省"
        self.city = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }
        self.params = {
            "key": "",
        }
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')

    def send_data(self, url, name):
        name = name.replace(" ", "")
        extract_data = {
            "topic": "registration_company",
            "company": name,
            "province": "湖北省",
            "city": "",
            "registered_date": "",
            "_site_record_id": "wljg.egs.gov.cn",
            "url": url
        }
        self.beans_client.put("offline_crawl_data", json.dumps(extract_data))

    def start(self):
        session = requests.session()
        session.params = self.params
        session.headers = self.headers
        session.proxies = self.get_proxy()

        pages = self.get_pages(session)
        if pages < 1:
            self.logger.error("获取页码失败")
            return
        for i in range(0, pages + 1):
            url = basic_url.format(i)
            try_cnt = 0
            while try_cnt < max_retry:
                try_cnt += 1
                try:
                    resp = session.post(url, timeout=timeout)
                    if resp is not None and resp.status_code == 200:
                        notes = json.loads(resp.text).get("data")
                        for note in notes:
                            try:
                                name = note["QYMC"]
                            except:
                                continue
                            self.send_data(url, name)
                            self.logger.info("成功获取{0}下{1}".format(url, name))
                        break
                except requests.RequestException as e:
                    self.logger.error("访问第{}页网络错误".format(i))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问第{}页出现未知的错误".format(i))
                    self.logger.exception(e)
            if try_cnt >= max_retry:
                self.logger.error("{}次重试失败...page = {}".format(max_retry, i))
                session.proxies = self.get_proxy()

    def get_pages(self, session):
        count = 0
        while count < max_retry:
            count += 1
            try:
                resp = session.post(url=basic_url.format(1), timeout=timeout)
                if resp is not None and resp.status_code == 200:
                    pages = int(json.loads(resp.text).get("total"))
                    if pages is None:
                        continue
                    return int(pages) / 10 + 1
            except requests.RequestException as e:
                self.logger.error("访问第一页网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问第一页出现未知的错误")
                self.logger.exception(e)
        return 0

    def get_proxy(self):
        ip = self.all_ip[random.randint(0, len(self.all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip


if __name__ == "__main__":
    worker = HuBei()
    worker()
