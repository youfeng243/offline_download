#!/usr/bin/env python
# -*- coding:utf-8 -*-


import json
import random
import re
import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from sites.common import staticproxy

from pyquery import PyQuery

from libs.fetcher import Fetcher
from libs.loghandler import getLogger

from conf import m_settings
from libs.taskbase import TaskBase
import requests, sys

# reload(sys)
# sys.setdefaultencoding('utf8')
max_retry = 10
timeout = 40
token = "170805143346674334"
token_url = "http://www.gdcourts.gov.cn/common/getToKenTempPutCk"
basic_url = "http://www.gdcourts.gov.cn/web/cpws?action=gotowsxxcx"
detail_url = "http://www.gdcourts.gov.cn/web/cpws?action=wsxxxq&wsid={}&fjm=J00"
base_url = "http://www.gdcourts.gov.cn/web/cpws?action=gotowsxxcx&flag=first"


class gd_wenshu(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beans_client = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')
        self.data = {
            "ah": "",
            "ay": "",
            "dsr": "",
            "wsmc": "",
            "fjm": "J00",
            "pageNum": "",
            "token_key": "",
            "csToken": ""
        }
        self.token_data = {
            "tokenKey": ""
        }

    def send_data(self, title, content, url):
        extract_data = {

            'case_name': title, 'wenshu_content': content, '_site_record_id': "gdcourts.gov.cn",
            'source': "gd_wenshu.py", 'url': url, "topic": "judgement_wenshu"
        }
        self.beans_client.put("offline_crawl_data", json.dumps(extract_data))

    def start(self):
        session = requests.session()
        session.headers = self.headers
        session.proxies = self.get_proxy()
        base_token = self.get_base_token(session)
        self.data["token_key"] = base_token
        self.token_data["tokenKey"] = base_token
        pages = self.get_pages(session)
        if pages < 1:
            self.logger.error("获取页码失败")
            return

        for i in xrange(1, pages+1):
            tokenVal = self.get_token(session)
            self.data["csToken"] = tokenVal
            self.data["pageNum"] = str(i)
            try_cnt = 0
            while try_cnt < max_retry:
                try_cnt += 1
                try:
                    resp = session.post(basic_url, timeout=timeout, data=self.data)
                    if resp is not None and resp.status_code == 200 and resp.text != "":
                        data = json.loads(resp.text)
                        data = data.get("wsxxlist")
                        for j in data:
                            title = j.get("SWWSMC")
                            wsid = j.get("WSID")
                            url = detail_url.format(wsid)
                            content = self.parse(url, session)
                            self.send_data(title, content, url)
                            self.logger.info("成功获取案件{},url为{}".format(title, url))
                        break
                except requests.RequestException as e:
                    self.logger.error("访问列表页{}网络错误".format(i))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问列表页{}未知的错误".format(i))
                    self.logger.exception(e)
            if try_cnt >= max_retry:
                self.logger.error("{}次重试失败...,访问列表页{}".format(max_retry, i))
                session.proxies = self.get_proxy()

    def parse(self, url, session):
        try_count = 0
        while try_count < max_retry:
            try_count += 1
            try:
                resp = session.get(url, timeout=timeout)
                pq = PyQuery(resp.text, parser="html")
                content = pq.find("div[class='col-xs-12 column page-content']").find("span").text()
                return content
            except requests.RequestException as e:
                self.logger.error("访问详情页{}网络错误".format(url))
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问详情页{}未知的错误".format(url))
                self.logger.exception(e)

        if try_count >= max_retry:
            self.logger.error("{}次重试失败,访问详情页{}".format(max_retry, url))
            session.proxies = self.get_proxy()

    def get_proxy(self):
        ip = self.all_ip[random.randint(0, len(self.all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip

    def get_pages(self, session):
        tokenVal = self.get_token(session)
        self.data["csToken"] = tokenVal
        self.data["pageNum"] = 1
        try_cnt = 0
        while try_cnt < max_retry:
            try_cnt += 1
            try:
                resp = session.post(basic_url, timeout=timeout, data=self.data)
                if resp is not None and resp.status_code == 200 and resp.text != "":
                    pages = json.loads(resp.text).get("pageinfo")
                    pages = pages.get("totalPage")
                    return pages
            except requests.RequestException as e:
                self.logger.error("获取页码网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("获取页码出现未知的错误")
                self.logger.exception(e)
        return 0

    def get_token(self, session):
        try_count = 0
        while try_count < max_retry:
            try_count += 1
            try:
                resp = session.post(token_url, data=self.token_data)
                if resp is None or resp.status_code != 200:
                    session.proxies = self.get_proxy()
                    continue
                tokenVal = json.loads(resp.text).get("tokenVal")
                return  tokenVal
            except Exception as e:
                self.logger.error("获取token第{}次失败".format(try_count))
                self.logger.exception(e)
        self.logger.error("{}次获取token失败,退出".format(max_retry))
        sys.exit()

    def get_base_token(self, session):
        try_count = 0
        while try_count < max_retry:
            try_count += 1
            try:
                resp = session.get(base_url, timeout=timeout)
                if resp is None or resp.status_code != 200:
                    session.proxies = self.get_proxy()
                    continue
                base_token = re.findall(r"token.*\d{10,30}", resp.text)[0]
                base_token = re.findall(r"\d+", base_token)[0]
                return base_token
            except requests.RequestException as e:
                self.logger.error("获取初始token网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("获取初始token出现未知的错误")
                self.logger.exception(e)


if __name__ == "__main__":
    worker = gd_wenshu()
    worker()
