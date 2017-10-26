# -*- coding:UTF-8 -*-

# !/usr/bin/env python

# @Author  clevertang
# @Date    2017-7.12
import json
import random
import sys

from conf.m_settings import store_company
from sites.common import util

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

basic_url = 'http://xinyong.bjhd.gov.cn/compan/companList!companList.action'
max_retry = 3
timeout = 40


class Bj(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = "北京"
        self.city = "北京"
        self.post_data = {
            "name": "请输入企业信息（如：名称、企业组织机构代码、工商注册码）",
            "types": "0",
            "page.total": "445995",
            "page.perPage": "10",
            "page.index": "",
        }
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
            "Connection": "keep-alive",
            "Content-Length": "312",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "http://xinyong.bjhd.gov.cn",
            "Referer": "http://xinyong.bjhd.gov.cn/compan/companList!companIndex.action",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')

    def send_data(self, name, date):
        name = name.replace(" ", "")
        extract_data = {
            "topic": "registration_company",
            "company": name,
            "province": "beijing",
            "city": "北京",
            "registered_date": date,
            "_site_record_id": "xinyong.bjhd.gov.cn",
            "url": basic_url
        }

        province = "beijing"
        store_company(province, name)

    def start(self):
        session = requests.session()
        session.headers = self.headers
        session.proxies = self.get_proxy()
        pages = self.get_pages(session)
        if pages < 1:
            return
        for i in range(1, pages):
            self.post_data["page.index"] = str(i)
            try_cnt = 0
            while try_cnt < max_retry:
                try:
                    try_cnt += 1

                    resp = session.post(data=self.post_data, url=basic_url, timeout=timeout)

                    if resp is not None and resp.status_code == 200:
                        data = resp.text
                        json_data = json.loads(data)
                        rows = json_data.get("resultJson", {})
                        for a in rows:
                            name = a["companName"]
                            try:
                                date = a["update"]
                            except KeyError as e:
                                date = ""  # 最后几页没有date
                                self.logger.error("没有date")
                            self.send_data(name, date)
                            self.logger.info("成功获取{0}，注册时间为{1}".format(name, date))
                        break
                except requests.RequestException as e:
                    self.logger.error("获取列表页第{}页网络错误".format(i))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问列表页{}出现未知的错误".format(i))
                    self.logger.exception(e)

            if try_cnt >= max_retry:
                self.logger.error("{}次重试失败...page = {}".format(max_retry, i))
                session.proxies = self.get_proxy()

    def get_pages(self, session):
        self.post_data["page.index"] = 1
        count = 0
        while count < max_retry:
            try:
                count += 1
                data = session.post(data=self.post_data, url=basic_url, timeout=timeout).content
                pages = json.loads(data).get("page")["pageCount"]
                return int(pages)
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
    worker = Bj()
    # worker.send_data()
    worker()
